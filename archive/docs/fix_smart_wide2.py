# -*- coding: utf-8 -*-
"""fix_smart_wide2.py -- narrow the last wide table properly."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "smart_algorithms.tex")
s = io.open(p, encoding="utf-8").read()
old = "\\begin{tabular}{p{4.0cm}p{1.5cm}p{1.6cm}p{1.7cm}p{1.4cm}p{4.0cm}}"
new = "\\begin{tabular}{p{3.6cm}p{1.3cm}p{1.5cm}p{1.5cm}p{1.1cm}p{3.6cm}}"
assert old in s, "anchor missing"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("narrowed")
