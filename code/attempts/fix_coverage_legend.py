# -*- coding: utf-8 -*-
"""fix_coverage_legend.py -- the two per-panel legends of the coverage figure ran
into each other; use one shared legend below the whole figure instead."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
old = """    ax.set_title(T("fig_cov1"), fontsize=15)
    ax.set_xlabel(T("x_east"))
    ax.set_ylabel(T("y_north"))
    legend_below(ax, ncol=3, y=-0.16)"""
new = """    ax.set_title(T("fig_cov1"), fontsize=15)
    ax.set_xlabel(T("x_east"))
    ax.set_ylabel(T("y_north"))
    h1 = [Line2D([], [], color="tab:blue", ls="--", lw=1.6,
                 label="站位的 $R_{\\\\min}$ 探测圆"),
          Line2D([], [], color="k", lw=2.6, label="目标区域边界"),
          Line2D([], [], color="tab:blue", marker="^", ls="", ms=11, label="检测站位")]"""
assert old in s, "coverage anchor 1 missing"
s = s.replace(old, new, 1)

old2 = """    ax.set_ylim(1450, 2060)
    ax.set_title(T("fig_cov2"), fontsize=15)
    legend_below(ax, ncol=2, y=-0.16)
    fig.tight_layout()
    save(fig, "fig_coverage.png")"""
new2 = """    ax.set_ylim(1450, 2060)
    ax.set_title(T("fig_cov2"), fontsize=15)
    h2 = [Line2D([], [], color="tab:blue", lw=3.0, label=T("fig_cov_c")),
          Line2D([], [], color="r", ls="--", lw=2.4, label=T("fig_cov_r")),
          Line2D([], [], color="g", ls=":", lw=2.4, label=T("fig_cov_opt"))]
    fig.tight_layout()
    figure_legend(fig, h1 + h2, ncol=3, y=-0.015)
    fig.subplots_adjust(bottom=0.26)
    save(fig, "fig_coverage.png")"""
assert old2 in s, "coverage anchor 2 missing"
s = s.replace(old2, new2, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("coverage legend fixed")
