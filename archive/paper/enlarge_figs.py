# -*- coding: utf-8 -*-
"""enlarge_figs.py -- the regenerated figures are more compact, so they can be
displayed larger in the paper without leaving the 30-page limit."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SCALE = {
    "0.62": "0.74",
    "0.60": "0.72",
    "0.56": "0.66",
    "0.48": "0.56",
    "0.72": "0.84",
    "0.64": "0.76",
}
for f in ("paper_p1.tex", "paper_p2.tex", "paper_p3.tex"):
    p = os.path.join(HERE, f)
    s = io.open(p, encoding="utf-8").read()
    for a, b in SCALE.items():
        s = s.replace("width=%s\\textwidth" % a, "width=%s\\textwidth" % b)
    io.open(p, "w", encoding="utf-8").write(s)
print("figure widths enlarged")
