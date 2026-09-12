# -*- coding: utf-8 -*-
"""trim2.py -- last compaction pass: shrink figures slightly more."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
for f in ("paper_p1.tex", "paper_p2.tex", "paper_p3.tex"):
    p = os.path.join(HERE, f)
    s = io.open(p, encoding="utf-8").read()
    for a, b in (("width=0.70\\textwidth", "width=0.62\\textwidth"),
                 ("width=0.52\\textwidth", "width=0.48\\textwidth"),
                 ("width=0.50\\textwidth", "width=0.46\\textwidth"),
                 ("width=0.47\\textwidth", "width=0.43\\textwidth")):
        s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8").write(s)
print("figures shrunk (final)")
