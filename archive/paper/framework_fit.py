# -*- coding: utf-8 -*-
"""framework_fit.py -- guarantee the framework diagram never exceeds the text
width by wrapping it in a resizebox (scaling is < 3 %, invisible)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()
a = "\\begin{center}\n\\begin{tikzpicture}["
b = "\\begin{center}\n\\resizebox{\\textwidth}{!}{%\n\\begin{tikzpicture}["
assert a in s, "start anchor missing"
s = s.replace(a, b, 1)
a2 = "\\end{tikzpicture}\n\\captionof{figure}{四个问题的逻辑关系"
b2 = "\\end{tikzpicture}}\n\\captionof{figure}{四个问题的逻辑关系"
assert a2 in s, "end anchor missing"
s = s.replace(a2, b2, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("framework wrapped in resizebox")
