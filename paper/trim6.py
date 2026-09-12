# -*- coding: utf-8 -*-
"""trim6.py -- lower the line spacing a little so that both the electronic and
the printed version keep the body within 30 pages."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()
old = "\\renewcommand*{\\baselinestretch}{1.30}"
new = "\\renewcommand*{\\baselinestretch}{1.24}"
assert old in s
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("line spacing set to 1.24")
