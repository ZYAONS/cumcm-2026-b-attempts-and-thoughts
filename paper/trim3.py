# -*- coding: utf-8 -*-
"""trim3.py -- compact the bibliography and the remaining whitespace."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()
old = "\\AtBeginEnvironment{thebibliography}{\\small}"
new = ("\\AtBeginEnvironment{thebibliography}{\\footnotesize}\n"
       "\\apptocmd{\\thebibliography}{\\setlength{\\itemsep}{0.5pt}"
       "\\setlength{\\parskip}{0pt}}{}{}")
assert old in s
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("bibliography compacted")
