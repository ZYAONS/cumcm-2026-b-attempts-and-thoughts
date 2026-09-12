# -*- coding: utf-8 -*-
"""fix_err_legend.py -- the legend of the error histogram still touched its x
label on the smaller canvas."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
a = "legend_below(ax[0], ncol=2, y=-0.22, fontsize=11.5)"
b = "legend_below(ax[0], ncol=2, y=-0.46, fontsize=11.5)"
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("legend lowered")
