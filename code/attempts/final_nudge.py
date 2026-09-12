# -*- coding: utf-8 -*-
"""final_nudge.py -- last label offset in the directional figure."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
a = 'xytext=(-90, -430), textcoords="data",'
b = 'xytext=(-360, -430), textcoords="data",'
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("nudged")
