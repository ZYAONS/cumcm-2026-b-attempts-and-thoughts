# -*- coding: utf-8 -*-
"""fix_inset_pos.py -- move the Q1 zoom inset into the empty upper-left corner so
that it cannot cover the S2 marker or the green bearing ray."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
a = "axin = ax.inset_axes([0.40, 0.06, 0.32, 0.30])"
b = "axin = ax.inset_axes([0.035, 0.615, 0.30, 0.30])"
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("inset moved")
