# -*- coding: utf-8 -*-
"""fix_dir_a.py -- separate the three annotations of the directional panel (a)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
s = s.replace('''    ax.annotate(T("fig_dir_src"), (0, 0), textcoords="offset points", xytext=(18, 26),
                fontsize=13)''',
              '''    ax.annotate(T("fig_dir_src"), (0, 0), xytext=(-90, -430), textcoords="data",
                fontsize=13,
                arrowprops=dict(arrowstyle="-", color="gray", lw=1.2))''', 1)
s = s.replace('''    ax.annotate(T("fig_dir_silent"), (-900, -300), textcoords="offset points",
                xytext=(-46, -78), fontsize=12.5,
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.4))''',
              '''    ax.annotate(T("fig_dir_silent"), (-900, -300), xytext=(-1215, -1330),
                textcoords="data", fontsize=12.5, ha="left",
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.4))''', 1)
io.open(p, "w", encoding="utf-8").write(s)
print("panel (a) annotations separated")
