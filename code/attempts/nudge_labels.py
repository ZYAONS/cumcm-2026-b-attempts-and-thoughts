# -*- coding: utf-8 -*-
"""nudge_labels.py -- final small label offsets in the overview panel."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
a = "xytext=(18, -8) if i == 0 else ((24, 6) if i == 1 else (10, 20)),"
b = "xytext=(18, -10) if i == 0 else ((24, 6) if i == 1 else (6, -24)),"
assert a in s, "anchor 1"
s = s.replace(a, b, 1)
a2 = 'ax.annotate("$S_2^{*}$", sol["S2"], textcoords="offset points", xytext=(-64, 12),'
b2 = 'ax.annotate("$S_2^{*}$", sol["S2"], textcoords="offset points", xytext=(-26, -34),'
assert a2 in s, "anchor 2"
s = s.replace(a2, b2, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("labels nudged")
