"""
mercury_strip_spectrum.py

生成黑色背景的长条式汞原子发射光谱图：
- 波长到 RGB 的可见光映射
- 按给定相对强度调整线条宽度
- 限制到 700 nm
- 可保存为高分辨率 PNG

依赖:
    pip install matplotlib numpy
"""

import matplotlib.pyplot as plt
import numpy as np

# --- 谱线数据 (波长 nm, 相对强度) ---
lines = [
    (404.7, 0.6), (407.9, 0.4), (410.9, 0.5),
    (434.0, 0.7), (434.8, 0.6), (435.5, 1.0),
    (491.7, 0.4), (496.7, 0.5), (502.0, 0.6), (504.0, 0.4),
    (546.2, 1.2),
    (567.7, 0.5),
    (577.2, 1.0), (579.2, 0.9),
    (586.0, 0.4), (591.6, 0.3),
    (607.4, 0.4), (612.2, 0.4), (623.6, 0.5),
    (671.8, 0.3), (690.4, 0.3)
]

# --- 波长 (nm) -> 近似 RGB 映射（可见光） ---
def wavelength_to_rgb(wavelength):
    """
    返回 (r,g,b) 三元组, 范围 [0,1]
    参考常见近似算法 (380-780 nm)
    """
    gamma = 0.8

    if 380 <= wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif 440 < wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0 ** gamma
    elif 490 < wavelength <= 510:
        R = 0.0
        G = 1.0 ** gamma
        B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif 510 < wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0 ** gamma
        B = 0.0
    elif 580 < wavelength <= 645:
        R = 1.0 ** gamma
        G = (-(wavelength - 645) / (645 - 580)) ** gamma
        B = 0.0
    elif 645 < wavelength <= 780:
        attenuation = 0.3 + 0.7 * (780 - wavelength) / (780 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0
    else:
        R = G = B = 0.0

    # clip 保证数值在 [0,1]
    return (max(0.0, min(1.0, R)),
            max(0.0, min(1.0, G)),
            max(0.0, min(1.0, B)))


def plot_long_strip(lines,
                    wl_min=350,
                    wl_max=700,
                    figsize=(16, 2),
                    base_linewidth=4.0,
                    background_color='black',
                    savepath=None,
                    dpi=300):
    """
    绘制长条式光谱
    - lines: list of (wavelength_nm, relative_intensity)
    - wl_min, wl_max: 绘图范围 (nm)
    - figsize: 图像比例 (宽, 高) 英寸
    - base_linewidth: 与强度乘积后的基础宽度
    - savepath: 若不为 None，则保存为 PNG
    - dpi: 保存时的分辨率
    """
    fig = plt.figure(figsize=figsize)
    fig.patch.set_facecolor(background_color)
    ax = fig.add_axes([0, 0, 1, 1])  # 占满整张图
    ax.set_facecolor(background_color)

    # 绘制每条谱线（纵向填满整个条带）
    for wl, intensity in lines:
        if wl_min <= wl <= wl_max:
            color = wavelength_to_rgb(wl)
            # matplotlib 要求颜色在 0-1 或 hex; 直接传 (r,g,b)
            lw = base_linewidth * float(intensity)
            # 为了更“条带感”，使用实心线并填满高度
            ax.axvline(wl, ymin=0.0, ymax=1.0, linewidth=lw, color=color, solid_capstyle='butt')

    # 去掉所有刻度与边框，得到干净的长条
    ax.set_xlim(wl_min, wl_max)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # 可选：在图下方标一个小尺度（关闭则注释掉）
    # ax2 = fig.add_axes([0.05, 0.01, 0.9, 0.05])
    # ax2.set_xlim(wl_min, wl_max)
    # ax2.set_xticks([400, 450, 500, 550, 600, 650, 700])
    # ax2.set_xticklabels(['400','450','500','550','600','650','700'], color='white')
    # ax2.set_yticks([])
    # ax2.set_facecolor(background_color)
    # for spine in ax2.spines.values():
    #     spine.set_visible(False)

    plt.tight_layout(pad=0)
    if savepath:
        plt.savefig(savepath, dpi=dpi, facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0)
        print(f"Saved: {savepath}  ({dpi} dpi)")
    plt.show()


if __name__ == "__main__":
    # 调整 base_linewidth 可以控制整体线宽感
    plot_long_strip(lines,
                    wl_min=380,
                    wl_max=700,
                    figsize=(18, 1.8),   # 宽条形 -> 更长的横向效果
                    base_linewidth=4.2,  # 与强度相乘得到最终线宽
                    background_color='black',
                    savepath="mercury_strip_700nm.png",
                    dpi=600)  # 高分辨率保存