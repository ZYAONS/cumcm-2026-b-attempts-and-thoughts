# -*- coding: utf-8 -*-
"""trim4.py -- final one-page compaction: slightly smaller wide figures."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
for f in ("paper_p1.tex", "paper_p2.tex", "paper_p3.tex"):
    p = os.path.join(HERE, f)
    s = io.open(p, encoding="utf-8").read()
    s = s.replace("width=0.84\\textwidth", "width=0.72\\textwidth")
    s = s.replace("width=0.70\\textwidth", "width=0.64\\textwidth")
    io.open(p, "w", encoding="utf-8").write(s)
print("wide figures reduced")
