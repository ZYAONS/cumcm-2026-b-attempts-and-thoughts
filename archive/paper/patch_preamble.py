# -*- coding: utf-8 -*-
"""patch_preamble.py -- theorem environments compatible with cumcmthesis.cls.

The class already defines theorem/lemma/corollary/proof, so only a proposition
environment and a lightweight proof environment are added here.
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()
old_start = s.find("\\usepackage{amsthm}")
old_end = s.find("\\renewcommand{\\proofname}{\\heiti 证明}")
if old_start != -1 and old_end != -1:
    old_end = s.find("\n", old_end) + 1
    s = s[:old_start] + s[old_end:]
anchor = "\\usepackage{amsmath,amssymb,amsfonts}"
new = (anchor + "\n"
       "\\newtheorem{proposition}{\\heiti 命题}\n"
       "\\newenvironment{pf}{\\par\\noindent\\textbf{证明}\\quad}"
       "{\\hfill$\\blacksquare$\\par}")
assert anchor in s
s = s.replace(anchor, new, 1)
io.open(p, "w", encoding="utf-8").write(s)

for f in ("paper_p1.tex", "paper_p2.tex", "paper_p3.tex"):
    q = os.path.join(HERE, f)
    t = io.open(q, encoding="utf-8").read()
    t = t.replace("\\begin{proof}", "\\begin{pf}").replace("\\end{proof}", "\\end{pf}")
    io.open(q, "w", encoding="utf-8").write(t)
print("preamble patched, proof -> pf")
