# -*- coding: utf-8 -*-
"""fix_smart_tab.py -- the ellipsis row still has too many tabs."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "smart_algorithms.tex")
s = io.open(p, encoding="utf-8").read()
old = "\\dots & & & & & & \\\\"
new = "\\dots & & & & & \\\\"
assert old in s, "anchor missing"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("ellipsis row fixed")
