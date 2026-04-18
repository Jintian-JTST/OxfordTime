import xml.etree.ElementTree as ET
import numpy as np
import soundfile as sf
from svgpathtools import parse_path

SR = 48000
DURATION = 5.0
DRAW_FREQ = 50.0  # 刷新率50Hz

def fnum(x):
    try:
        return float(x.replace('px', '').strip()) if x else 0.0
    except:
        return 0.0

def parse_points_attr(s):
    if not s: return []
    s = s.replace(',', ' ').strip()
    vals = [float(v) for v in s.split()]
    return list(zip(vals[0::2], vals[1::2]))

def extract_svg_points(svg_file):
    """解析SVG，提取所有独立图形的顶点"""
    tree = ET.parse(svg_file)
    root = tree.getroot()
    all_shapes = []

    for elem in root.iter():
        tag = elem.tag.split("}")[-1]
        pts = []
        
        if tag == "circle":
            cx, cy, r = fnum(elem.get("cx")), fnum(elem.get("cy")), fnum(elem.get("r"))
            t = np.linspace(0, 2*np.pi, 300, endpoint=False)
            pts = np.column_stack([cx + r*np.cos(t), cy + r*np.sin(t)])
            pts = np.vstack([pts, pts[0]]) 
            
        elif tag == "rect":
            x, y, w, h = fnum(elem.get("x")), fnum(elem.get("y")), fnum(elem.get("width")), fnum(elem.get("height"))
            pts = np.array([(x,y), (x+w,y), (x+w,y+h), (x,y+h), (x,y)])
            
        elif tag in ("line", "polyline", "polygon"):
            if tag == "line":
                pts = np.array([(fnum(elem.get("x1")), fnum(elem.get("y1"))), 
                                (fnum(elem.get("x2")), fnum(elem.get("y2")))])
            else:
                pts = np.array(parse_points_attr(elem.get("points", "")))
            if tag == "polygon" and len(pts) > 0:
                pts = np.vstack([pts, pts[0]])
                
        elif tag == "path":
            d = elem.get("d")
            if d:
                path = parse_path(d)
                # 提高路径的采样密度，防止三叉戟的圆弧变成多边形
                num_samples = max(300, int(path.length() / 1.5)) if path.length() > 0 else 300
                pts = np.array([(path.point(t).real, path.point(t).imag) 
                               for t in np.linspace(0, 1, num_samples)])
        
        if len(pts) > 1:
            all_shapes.append(pts)
            
    return all_shapes

def build_clean_oscilloscope_audio(shapes, sr, duration, draw_freq):
    if not shapes:
        print("未找到有效形状！")
        return np.zeros((int(sr * duration), 2))

    # 1. 坐标统一归一化 (计算所有点的外框)
    all_pts = np.vstack(shapes)
    min_p = all_pts.min(axis=0)
    max_p = all_pts.max(axis=0)
    center = (max_p + min_p) / 2.0
    
    # 归一化并翻转Y轴
    for i in range(len(shapes)):
        shapes[i] = shapes[i] - center
        scale = np.max(np.abs(all_pts - center))
        if scale > 0:
            shapes[i] = shapes[i] / scale
        shapes[i][:, 1] *= -1.0 

    # 2. 计算每个独立图形的物理长度
    lengths = []
    valid_shapes = []
    for pts in shapes:
        diffs = np.diff(pts, axis=0)
        dist = np.sum(np.linalg.norm(diffs, axis=1))
        if dist > 1e-6:
            lengths.append(dist)
            valid_shapes.append(pts)

    shapes = valid_shapes
    total_length = sum(lengths)
    total_samples_per_frame = int(sr / draw_freq)

    # 3. 分段进行匀速插值 (跳跃线不占用音频采样点)
    frame_segments = []
    for pts, length in zip(shapes, lengths):
        # 按该图形长度占总长度的比例，分配采样点
        n_samples = max(2, int(total_samples_per_frame * (length / total_length)))
        
        diffs = np.diff(pts, axis=0)
        dists = np.linalg.norm(diffs, axis=1)
        cum_dists = np.concatenate(([0], np.cumsum(dists)))
        
        target_dists = np.linspace(0, cum_dists[-1], n_samples)
        x_seg = np.interp(target_dists, cum_dists, pts[:, 0])
        y_seg = np.interp(target_dists, cum_dists, pts[:, 1])
        
        frame_segments.append(np.column_stack([x_seg, y_seg]))

    # 将所有分段音频拼接成一帧
    frame_audio = np.vstack(frame_segments)

    # 补齐误差导致的少量采样点缺失
    if len(frame_audio) < total_samples_per_frame:
        pad = np.tile(frame_audio[-1], (total_samples_per_frame - len(frame_audio), 1))
        frame_audio = np.vstack([frame_audio, pad])
    else:
        frame_audio = frame_audio[:total_samples_per_frame]

    frame_audio *= 0.9  # 留出 10% 电压余量，防止边缘削波

    # 4. 循环生成完整音频
    num_frames = int(duration * draw_freq)
    audio = np.tile(frame_audio, (num_frames, 1))

    return audio.astype(np.float32)

if __name__ == "__main__":
    input_file = "untitled.svg"
    output_file = "clean_scope.wav"
    
    print("正在提取并计算消除飞线的匀速路径...")
    shapes = extract_svg_points(input_file)
    
    audio = build_clean_oscilloscope_audio(shapes, SR, DURATION, DRAW_FREQ)
    
    sf.write(output_file, audio, SR)
    print(f"音频已生成: {output_file}。请再次放入示波器查看！")