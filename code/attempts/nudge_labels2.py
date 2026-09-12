# -*- coding: utf-8 -*-
"""nudge_labels2.py -- separate the 900 m / 1400 m tags and silence the
tight_layout warning of the gridspec figure."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
a = "xytext=(18, -10) if i == 0 else ((24, 6) if i == 1 else (6, -24)),"
b = "xytext=(18, -12) if i == 0 else ((26, 10) if i == 1 else (44, -8)),"
assert a in s, "anchor 1"
s = s.replace(a, b, 1)
a2 = """    fig.tight_layout()
    figure_legend(fig, [
        Line2D([], [], color="tab:blue", lw=2.0, label="干扰源至 $S_1$ 的视线"),"""
b2 = """    figure_legend(fig, [
        Line2D([], [], color="tab:blue", lw=2.0, label="干扰源至 $S_1$ 的视线"),"""
assert a2 in s, "anchor 2"
s = s.replace(a2, b2, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("done")
