# -*- coding: utf-8 -*-
"""fix_after_shrink3.py -- on the smaller canvas the below-panel legends touched
the x labels; push them further down."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
reps = [
    ("legend_below(ax[0], ncol=3, y=-0.21)", "legend_below(ax[0], ncol=3, y=-0.31)"),
    ("legend_below(ax[1], ncol=2, y=-0.19)", "legend_below(ax[1], ncol=2, y=-0.29)"),
    ("legend_below(ax[0], ncol=2, y=-0.20)", "legend_below(ax[0], ncol=2, y=-0.28)"),
]
for a, b in reps:
    n = s.count(a)
    s = s.replace(a, b)
    print("  %-42s x%d" % (a, n))
io.open(p, "w", encoding="utf-8").write(s)
print("legends pushed down")
