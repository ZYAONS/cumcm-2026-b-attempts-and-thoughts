# -*- coding: utf-8 -*-
"""fix_optional_overfull3.py -- the negative-list longtable rows are 2 pt over;
drop the table to footnotesize (the remaining overfull are sub-millimetre)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "optional_changes.tex")
s = io.open(p, encoding="utf-8").read()
a = "\\begin{longtable}{p{0.6cm}p{3.4cm}p{3.1cm}p{3.0cm}p{2.4cm}}"
b = "\\footnotesize\n\\begin{longtable}{p{0.6cm}p{3.4cm}p{3.1cm}p{3.0cm}p{2.4cm}}"
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("footnotesize applied to the negative list")
