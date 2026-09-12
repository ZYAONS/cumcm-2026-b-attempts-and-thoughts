# -*- coding: utf-8 -*-
"""polish_panels.py -- final polish of the two reworked figures:
  * one shared legend per figure (no per-panel legends that collide)
  * more margin inside the zoom panels so labels are not clipped
  * alternating label offsets in the overview panel
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

# ---------------------------------------------------------------- Q1 ------
s = s.replace(
    '''    ax.set_title("(a) 整体几何", fontsize=16)
    legend_below(ax, ncol=2, y=-0.16)''',
    '''    ax.set_title("(a) 整体几何", fontsize=16)''', 1)
s = s.replace(
    '''    ax.set_title("(b) 定位区域局部放大", fontsize=16)
    legend_below(ax, ncol=2, y=-0.16)
    fig.tight_layout()
    save(fig, "fig_q1_region.png")''',
    '''    ax.set_title("(b) 定位区域局部放大", fontsize=16)
    fig.tight_layout()
    figure_legend(fig, [
        Line2D([], [], color="tab:blue", ls="--", lw=1.6, label="示向度 $\\\\pm1^\\\\circ$ 边界"),
        MplPolygon([(0, 0)], fc="tab:red", alpha=0.55, ec="tab:red", label="定位区域 $\\\\mathcal{R}$"),
        Line2D([], [], color="k", marker="*", ls="", ms=13, label="干扰源真实位置 $G$"),
        Line2D([], [], color="k", lw=2.2, label="直径 $AB$"),
        Line2D([], [], color="k", ls="--", lw=2.0, label="以 $AB$ 为直径的圆"),
        Line2D([], [], color="purple", ls=":", lw=2.2, label="最小包围圆")],
        ncol=3, y=-0.01)
    fig.subplots_adjust(bottom=0.26)
    save(fig, "fig_q1_region.png")''', 1)
# drop the now-duplicated per-panel labels of the zoom panel
s = s.replace(
    '''    ax.add_patch(MplPolygon(res["vertices"], closed=True, fc="tab:red", alpha=0.55,
                            ec="tab:red", lw=2.2, zorder=4, label="定位区域 $\\\\\\\\mathcal{R}$"))
    ax.add_patch(Circle(((A[0] + B[0]) / 2.0, (A[1] + B[1]) / 2.0),
                        res["diameter"] / 2.0, fill=False, ls="--", color="k", lw=2.0,
                        zorder=3, label=T("fig_diameter") % res["diameter"]))
    ax.add_patch(Circle((cx, cy), r, fill=False, ls=":", color="purple", lw=2.2,
                        zorder=3, label=T("fig_mec") % r))
    ax.plot([A[0], B[0]], [A[1], B[1]], "-", color="k", lw=2.2, zorder=5,
            label="直径 $AB$")''',
    '''    ax.add_patch(MplPolygon(res["vertices"], closed=True, fc="tab:red", alpha=0.55,
                            ec="tab:red", lw=2.2, zorder=4))
    ax.add_patch(Circle(((A[0] + B[0]) / 2.0, (A[1] + B[1]) / 2.0),
                        res["diameter"] / 2.0, fill=False, ls="--", color="k", lw=2.0,
                        zorder=3))
    ax.add_patch(Circle((cx, cy), r, fill=False, ls=":", color="purple", lw=2.2,
                        zorder=3))
    ax.plot([A[0], B[0]], [A[1], B[1]], "-", color="k", lw=2.2, zorder=5)''', 1)

# ---------------------------------------------------------------- Q2 ------
s = s.replace(
    '''    gs = fig.add_gridspec(1, 4, width_ratios=[1.35, 1, 1, 1], wspace=0.42)''',
    '''    gs = fig.add_gridspec(1, 4, width_ratios=[1.6, 1, 1, 1], wspace=0.48)''', 1)
s = s.replace(
    '''        ax.plot(*G, "o", ms=10, color=col, zorder=6)
        ax.annotate("%.0f m" % rr, G, textcoords="offset points", xytext=(8, 6),
                    fontsize=13, color=col)''',
    '''        ax.plot(*G, "o", ms=10, color=col, zorder=6)
        ax.annotate("%.0f m" % rr, G, textcoords="offset points",
                    xytext=(16, -4) if i == 0 else ((20, 8) if i == 1 else (14, 14)),
                    fontsize=13, color=col)''', 1)
s = s.replace(
    '''    for G, rr, col in zip(Gs, ranges, cols):
        ax.plot([s1[0], G[0]], [s1[1], G[1]], "-", color=col, lw=2.0)''',
    '''    for i, (G, rr, col) in enumerate(zip(Gs, ranges, cols)):
        ax.plot([s1[0], G[0]], [s1[1], G[1]], "-", color=col, lw=2.0)''', 1)
s = s.replace(
    '''    ax.set_xlim(-1650, 1650)
    ax.set_ylim(-1000, 1900)
    ax.set_title("(a) 几何总览", fontsize=15)''',
    '''    ax.set_xlim(-1750, 1750)
    ax.set_ylim(-1150, 2050)
    ax.set_title("(a) 几何总览", fontsize=15)''', 1)
s = s.replace(
    '''        half = max(res["diameter"], 2 * res["mec"][2]) * 0.95 + 8''',
    '''        half = max(res["diameter"], 2 * res["mec"][2]) * 1.15 + 12''', 1)
s = s.replace(
    '''    figure_legend(fig, [
        Line2D([], [], color="tab:blue", lw=2.0, label="干扰源至 $S_1$ 的视线"),''',
    '''    figure_legend(fig, [
        Line2D([], [], color="tab:blue", lw=2.0, label="干扰源至 $S_1$ 的视线"),
        Line2D([], [], color="tab:red", marker="*", ls="", ms=13, label="最优第二检测点 $S_2^{*}$"),''', 1)
io.open(p, "w", encoding="utf-8").write(s)
print("polished")
