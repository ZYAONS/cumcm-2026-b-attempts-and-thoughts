# -*- coding: utf-8 -*-
"""fix_region_rule_legend.py -- the shared legend of the region-rule figure
collided with the per-panel x labels; use one common x label instead."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

old = """        ax.tick_params(labelsize=12)
        ax.set_title(T("fig_q2_r%d" % i) % res["diameter"], fontsize=15)
        ax.set_xlabel(T("x_east"), fontsize=14)
        if i == 0:
            ax.set_ylabel(T("y_north"), fontsize=14)"""
new = """        ax.tick_params(labelsize=12)
        ax.set_title(T("fig_q2_r%d" % i) % res["diameter"], fontsize=15)
        if i == 0:
            ax.set_ylabel(T("y_north"), fontsize=15)"""
assert old in s, "anchor 1 missing"
s = s.replace(old, new, 1)

old2 = """    fig.suptitle(T("fig_q2_rule_title"), fontsize=16)
    figure_legend(fig, [
        MplPolygon([(0, 0)], fc="tab:red", alpha=0.55, ec="tab:red", label="定位区域"),
        Line2D([], [], color="k", lw=2.2, label="直径 $AB$"),
        Line2D([], [], color="k", ls="--", lw=1.8, label="以 $AB$ 为直径的圆"),
        Line2D([], [], color="purple", ls=":", lw=2.2, label="最小包围圆")],
        ncol=4, y=-0.02)
    fig.tight_layout(rect=(0, 0.08, 1, 0.93))
    save(fig, "fig_q2_region_rule.png")"""
new2 = """    fig.suptitle(T("fig_q2_rule_title"), fontsize=16)
    fig.tight_layout(rect=(0, 0.16, 1, 0.92))
    fig.text(0.5, 0.105, T("x_east"), ha="center", fontsize=15)
    figure_legend(fig, [
        MplPolygon([(0, 0)], fc="tab:red", alpha=0.55, ec="tab:red", label="定位区域"),
        Line2D([], [], color="k", lw=2.2, label="直径 $AB$"),
        Line2D([], [], color="k", ls="--", lw=1.8, label="以 $AB$ 为直径的圆"),
        Line2D([], [], color="purple", ls=":", lw=2.2, label="最小包围圆")],
        ncol=4, y=0.005)
    save(fig, "fig_q2_region_rule.png")"""
assert old2 in s, "anchor 2 missing"
s = s.replace(old2, new2, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
