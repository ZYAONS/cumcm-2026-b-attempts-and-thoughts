# -*- coding: utf-8 -*-
"""tighten.py -- final compaction pass."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()
old = "\\AtBeginEnvironment{algorithmic}{\\footnotesize}"
new = ("\\AtBeginEnvironment{algorithmic}{\\scriptsize}\n"
       "\\renewcommand*{\\baselinestretch}{1.30}")
assert old in s, "anchor missing"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("tightened")
