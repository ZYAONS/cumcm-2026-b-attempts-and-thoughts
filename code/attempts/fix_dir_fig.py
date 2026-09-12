# -*- coding: utf-8 -*-
"""fix_dir_fig.py -- move the "silent here" note away from the y tick labels."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
a = """    ax.annotate(T("fig_dir_silent"), (-900, -300), textcoords="offset points",
                xytext=(-56, -56), fontsize=12.5)"""
b = """    ax.annotate(T("fig_dir_silent"), (-900, -300), textcoords="offset points",
                xytext=(-28, 70), fontsize=12.5,
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.4))"""
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
