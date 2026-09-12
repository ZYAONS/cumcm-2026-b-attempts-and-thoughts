# -*- coding: utf-8 -*-
"""fix_four_min.py -- shrink the attempt-list longtable."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "four_minutes.tex")
s = io.open(p, encoding="utf-8").read()
old = "\\begin{longtable}{p{0.5cm}p{3.4cm}p{3.2cm}p{2.3cm}p{3.1cm}}"
new = "\\scriptsize\n\\begin{longtable}{p{0.5cm}p{3.2cm}p{3.0cm}p{2.1cm}p{2.9cm}}"
assert old in s, "anchor missing"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("narrowed")
