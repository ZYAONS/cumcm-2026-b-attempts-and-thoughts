# -*- coding: utf-8 -*-
"""trim8.py -- lower the line spacing slightly and shrink the tallest float so
that the printed version also keeps a 30-page body."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()
a = "\\renewcommand*{\\baselinestretch}{1.24}"
b = "\\renewcommand*{\\baselinestretch}{1.18}"
assert a in s, "spacing anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)

# shrink the tallest figure (the 2x2 panel figure) which forces float pages
p2 = os.path.join(HERE, "make_figures_dummy")   # placeholder, figures live in code/
print("spacing -> 1.18")
