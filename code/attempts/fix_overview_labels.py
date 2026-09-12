# -*- coding: utf-8 -*-
"""fix_overview_labels.py -- the three distance tags in the overview panel keep
colliding; replace them by colour coding that matches the zoom panels."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
a = """        ax.plot(*G, "o", ms=10, color=col, zorder=6)
        ax.annotate("%.0f m" % rr, G, textcoords="offset points",
                    xytext=(18, -12) if i == 0 else ((26, 10) if i == 1 else (44, -8)),
                    fontsize=13, color=col)"""
b = """        ax.plot(*G, "o", ms=11, color=col, zorder=6)"""
assert a in s, "anchor 1"
s = s.replace(a, b, 1)
a2 = """        Line2D([], [], color="tab:red", marker="*", ls="", ms=13, label="最优第二检测点 $S_2^{*}$"),"""
b2 = """        Line2D([], [], color="tab:red", marker="*", ls="", ms=13, label="最优第二检测点 $S_2^{*}$"),
        Line2D([], [], color="gray", marker="o", ls="", ms=10,
               label="干扰源位置（颜色对应 (b)(c)(d)）"),"""
assert a2 in s, "anchor 2"
s = s.replace(a2, b2, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("overview labels replaced by colour coding")
