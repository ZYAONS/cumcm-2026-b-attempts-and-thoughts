# -*- coding: utf-8 -*-
"""tighten_spacing.py -- the verification section pushed the body to 31 pages;
the format rules do not fix the line spacing, so tighten it slightly."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()
a = "\\renewcommand*{\\baselinestretch}{1.18}"
b = "\\renewcommand*{\\baselinestretch}{1.10}"
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("line spacing 1.18 -> 1.10")
