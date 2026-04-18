import math
import re
import xml.etree.ElementTree as ET

import numpy as np
import soundfile as sf
from svgpathtools import parse_path

SR = 48000
DURATION = 5.0
DRAW_FREQ = 50.0  # 一帧图形每秒重复多少次


def fnum(x):
    return float(x) if x is not None else 0.0


def parse_points_attr(s):
    s = (s or "").replace(",", " ").strip()
    if not s:
        return []
    vals = [float(v) for v in s.split()]
    return list(zip(vals[0::2], vals[1::2]))


# =========================
# 矩阵与 transform 处理
# =========================

def identity_matrix():
    return np.eye(3, dtype=float)


def translation_matrix(tx, ty):
    return np.array([
        [1.0, 0.0, tx],
        [0.0, 1.0, ty],
        [0.0, 0.0, 1.0],
    ], dtype=float)


def scale_matrix(sx, sy):
    return np.array([
        [sx, 0.0, 0.0],
        [0.0, sy, 0.0],
        [0.0, 0.0, 1.0],
    ], dtype=float)


def rotation_matrix(deg):
    a = math.radians(deg)
    c = math.cos(a)
    s = math.sin(a)
    return np.array([
        [c, -s, 0.0],
        [s,  c, 0.0],
        [0.0, 0.0, 1.0],
    ], dtype=float)


def skewx_matrix(deg):
    k = math.tan(math.radians(deg))
    return np.array([
        [1.0, k,   0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ], dtype=float)


def skewy_matrix(deg):
    k = math.tan(math.radians(deg))
    return np.array([
        [1.0, 0.0, 0.0],
        [k,   1.0, 0.0],
        [0.0, 0.0, 1.0],
    ], dtype=float)


def matrix6_to_matrix3(vals):
    a, b, c, d, e, f = vals
    return np.array([
        [a, c, e],
        [b, d, f],
        [0.0, 0.0, 1.0],
    ], dtype=float)


def parse_transform_matrix(transform_str):
    """
    把 SVG transform 字符串解析成一个 3x3 齐次矩阵。
    注意：这里是先合成矩阵，再一次性作用到点上。
    """
    if not transform_str or not transform_str.strip():
        return identity_matrix()

    M = identity_matrix()

    items = re.findall(r'([A-Za-z]+)\s*\(([^)]*)\)', transform_str)
    for name, argstr in items:
        vals = [float(v) for v in re.split(r'[\s,]+', argstr.strip()) if v]

        if name == "matrix" and len(vals) == 6:
            op = matrix6_to_matrix3(vals)

        elif name == "translate":
            tx = vals[0] if len(vals) >= 1 else 0.0
            ty = vals[1] if len(vals) >= 2 else 0.0
            op = translation_matrix(tx, ty)

        elif name == "scale":
            sx = vals[0] if len(vals) >= 1 else 1.0
            sy = vals[1] if len(vals) >= 2 else sx
            op = scale_matrix(sx, sy)

        elif name == "rotate":
            if len(vals) == 1:
                op = rotation_matrix(vals[0])
            elif len(vals) >= 3:
                ang, cx, cy = vals[0], vals[1], vals[2]
                op = (
                    translation_matrix(cx, cy)
                    @ rotation_matrix(ang)
                    @ translation_matrix(-cx, -cy)
                )
            else:
                continue

        elif name == "skewX" and len(vals) >= 1:
            op = skewx_matrix(vals[0])

        elif name == "skewY" and len(vals) >= 1:
            op = skewy_matrix(vals[0])

        else:
            continue

        # 关键：按列表顺序拼成总矩阵
        M = M @ op

    return M


def apply_matrix_to_points(pts, M):
    if pts is None or len(pts) == 0:
        return pts
    pts = np.asarray(pts, dtype=float)
    homo = np.column_stack([pts, np.ones(len(pts), dtype=float)])
    out = (M @ homo.T).T
    return out[:, :2]


# =========================
# 几何采样
# =========================

def sample_segment(a, b, n):
    t = np.linspace(0.0, 1.0, n, endpoint=False)
    return (1.0 - t)[:, None] * a + t[:, None] * b


def sample_polyline(points, n=1024, closed=False):
    if len(points) < 2:
        return np.empty((0, 2), dtype=float)

    pts = np.asarray(points, dtype=float)
    if closed:
        pts = np.vstack([pts, pts[0]])

    segs = pts[1:] - pts[:-1]
    lens = np.sqrt((segs ** 2).sum(axis=1))
    total = lens.sum()

    if total <= 1e-12:
        return np.repeat(pts[:1], n, axis=0)

    out = []
    for i, L in enumerate(lens):
        k = max(2, int(round(n * (L / total))))
        out.append(sample_segment(pts[i], pts[i + 1], k))
    out.append(pts[-1][None, :])
    return np.vstack(out)


def sample_circle(cx, cy, r, n=2048):
    t = np.linspace(0.0, 2.0 * math.pi, n, endpoint=False)
    x = cx + r * np.cos(t)
    y = cy + r * np.sin(t)
    pts = np.column_stack([x, y])
    return np.vstack([pts, pts[0]])


def sample_ellipse(cx, cy, rx, ry, n=2048):
    t = np.linspace(0.0, 2.0 * math.pi, n, endpoint=False)
    x = cx + rx * np.cos(t)
    y = cy + ry * np.sin(t)
    pts = np.column_stack([x, y])
    return np.vstack([pts, pts[0]])


def sample_rect(x, y, w, h, n=1024):
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    return sample_polyline(pts, n=n, closed=True)


def sample_path_obj(path_obj, n=4096):
    lengths = np.array([seg.length(error=1e-5) for seg in path_obj], dtype=float)
    total = lengths.sum()
    if total <= 1e-12:
        return np.empty((0, 2), dtype=float)

    pts = []
    for seg, L in zip(path_obj, lengths):
        k = max(2, int(round(n * (L / total))))
        ts = np.linspace(0.0, 1.0, k, endpoint=False)
        for t in ts:
            c = seg.point(t)
            pts.append((c.real, c.imag))

    end = path_obj[-1].end
    pts.append((end.real, end.imag))
    return np.asarray(pts, dtype=float)


def is_hidden(elem):
    style = (elem.get("style") or "").replace(" ", "").lower()
    display = (elem.get("display") or "").strip().lower()
    visibility = (elem.get("visibility") or "").strip().lower()
    if display == "none" or visibility == "hidden":
        return True
    if "display:none" in style or "visibility:hidden" in style:
        return True
    return False


# =========================
# 递归提取 SVG 图形
# =========================

def extract_shapes(svg_file):
    tree = ET.parse(svg_file)
    root = tree.getroot()
    shapes = []

    def walk(elem, parent_matrix):
        if is_hidden(elem):
            return

        tag = elem.tag.split("}")[-1]
        local_matrix = parse_transform_matrix(elem.get("transform"))
        ctm = parent_matrix @ local_matrix

        if tag == "circle":
            cx = fnum(elem.get("cx"))
            cy = fnum(elem.get("cy"))
            r = fnum(elem.get("r"))
            if r > 0:
                pts = sample_circle(cx, cy, r, n=2048)
                shapes.append(apply_matrix_to_points(pts, ctm))

        elif tag == "ellipse":
            cx = fnum(elem.get("cx"))
            cy = fnum(elem.get("cy"))
            rx = fnum(elem.get("rx"))
            ry = fnum(elem.get("ry"))
            if rx > 0 and ry > 0:
                pts = sample_ellipse(cx, cy, rx, ry, n=2048)
                shapes.append(apply_matrix_to_points(pts, ctm))

        elif tag == "rect":
            x = fnum(elem.get("x"))
            y = fnum(elem.get("y"))
            w = fnum(elem.get("width"))
            h = fnum(elem.get("height"))
            if w > 0 and h > 0:
                pts = sample_rect(x, y, w, h, n=1024)
                shapes.append(apply_matrix_to_points(pts, ctm))

        elif tag == "line":
            x1 = fnum(elem.get("x1"))
            y1 = fnum(elem.get("y1"))
            x2 = fnum(elem.get("x2"))
            y2 = fnum(elem.get("y2"))
            pts = sample_polyline([(x1, y1), (x2, y2)], n=512, closed=False)
            shapes.append(apply_matrix_to_points(pts, ctm))

        elif tag in ("polyline", "polygon"):
            pts0 = parse_points_attr(elem.get("points", ""))
            if pts0:
                pts = sample_polyline(pts0, n=1024, closed=(tag == "polygon"))
                shapes.append(apply_matrix_to_points(pts, ctm))

        elif tag == "path":
            d = elem.get("d")
            if d:
                path_obj = parse_path(d)

                # 如果 path 内部有多个连续子路径，拆开分别处理
                subpaths = []
                if hasattr(path_obj, "continuous_subpaths"):
                    subpaths = path_obj.continuous_subpaths()
                if not subpaths:
                    subpaths = [path_obj]

                for sub in subpaths:
                    pts = sample_path_obj(sub, n=4096)
                    if len(pts) > 1:
                        shapes.append(apply_matrix_to_points(pts, ctm))

        for child in list(elem):
            walk(child, ctm)

    walk(root, identity_matrix())
    return shapes


# =========================
# 生成示波器 XY 音频
# =========================

def build_clean_oscilloscope_audio(shapes, sr, duration, draw_freq):
    if not shapes:
        print("未找到有效形状。")
        return np.zeros((int(sr * duration), 2), dtype=np.float32)

    # 全局归一化
    all_pts = np.vstack(shapes)
    min_p = all_pts.min(axis=0)
    max_p = all_pts.max(axis=0)
    center = (max_p + min_p) / 2.0
    scale = np.max(np.abs(all_pts - center))
    if scale <= 1e-12:
        scale = 1.0

    normalized_shapes = []
    for pts in shapes:
        p = (pts - center) / scale
        p[:, 1] *= -1.0
        normalized_shapes.append(p)

    # 各 shape 的几何长度
    valid_shapes = []
    lengths = []
    for pts in normalized_shapes:
        if len(pts) < 2:
            continue
        diffs = np.diff(pts, axis=0)
        dists = np.linalg.norm(diffs, axis=1)
        length = dists.sum()
        if length > 1e-8:
            valid_shapes.append(pts)
            lengths.append(length)

    if not valid_shapes:
        print("所有图形长度都为 0。")
        return np.zeros((int(sr * duration), 2), dtype=np.float32)

    lengths = np.array(lengths, dtype=float)
    total_length = lengths.sum()
    total_samples_per_frame = max(8, int(sr / draw_freq))

    frame_segments = []
    for pts, length in zip(valid_shapes, lengths):
        n_samples = max(2, int(round(total_samples_per_frame * (length / total_length))))

        diffs = np.diff(pts, axis=0)
        seglens = np.linalg.norm(diffs, axis=1)
        cum = np.concatenate([[0.0], np.cumsum(seglens)])

        if cum[-1] <= 1e-12:
            continue

        target = np.linspace(0.0, cum[-1], n_samples, endpoint=False)
        x = np.interp(target, cum, pts[:, 0])
        y = np.interp(target, cum, pts[:, 1])
        frame_segments.append(np.column_stack([x, y]))

    if not frame_segments:
        print("没有可输出的帧段。")
        return np.zeros((int(sr * duration), 2), dtype=np.float32)

    frame_audio = np.vstack(frame_segments)

    if len(frame_audio) < total_samples_per_frame:
        pad = np.tile(frame_audio[-1], (total_samples_per_frame - len(frame_audio), 1))
        frame_audio = np.vstack([frame_audio, pad])
    else:
        frame_audio = frame_audio[:total_samples_per_frame]

    frame_audio *= 0.9

    num_frames = int(duration * draw_freq)
    audio = np.tile(frame_audio, (num_frames, 1))

    target_len = int(sr * duration)
    if len(audio) < target_len:
        pad = np.tile(audio[-1], (target_len - len(audio), 1))
        audio = np.vstack([audio, pad])
    else:
        audio = audio[:target_len]

    return audio.astype(np.float32)


if __name__ == "__main__":
    input_file = "untitled.svg"
    output_file = "2.wav"

    print("正在解析 SVG（含递归 transform）...")
    shapes = extract_shapes(input_file)

    print(f"提取到 {len(shapes)} 个独立 shape")
    audio = build_clean_oscilloscope_audio(shapes, SR, DURATION, DRAW_FREQ)

    sf.write(output_file, audio, SR)
    print(f"音频已生成: {output_file}")