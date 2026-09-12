# -*- coding: utf-8 -*-
"""fix_timeopt_doc2.py -- narrow the attempt-list longtable."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "time_optimization.tex")
s = io.open(p, encoding="utf-8").read()
a = "\\begin{longtable}{p{0.5cm}p{3.6cm}p{3.0cm}p{2.6cm}p{3.1cm}}"
b = "\\footnotesize\n\\begin{longtable}{p{0.5cm}p{3.4cm}p{2.8cm}p{2.4cm}p{2.9cm}}"
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("narrowed")
