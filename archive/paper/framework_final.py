# -*- coding: utf-8 -*-
"""framework_final.py -- the middle arrow label touched the boxes; widen the gaps
and shorten the label."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()
reps = [
    ("minimum height=1.50cm, minimum width=2.72cm, fill=blue!6,",
     "minimum height=1.50cm, minimum width=2.58cm, fill=blue!6,"),
    ("\\node[box, right=1.20cm of q1] (q2)", "\\node[box, right=1.50cm of q1] (q2)"),
    ("\\node[box, right=1.20cm of q2] (q3)", "\\node[box, right=1.50cm of q2] (q3)"),
    ("\\node[box, right=1.20cm of q3] (q4)", "\\node[box, right=1.50cm of q3] (q4)"),
    ("\\draw[ar] (q3) -- node[lbl, above=2pt] {覆盖 $\\Rightarrow$ 认证} (q4);",
     "\\draw[ar] (q3) -- node[lbl, above=2pt] {覆盖与认证} (q4);"),
    ("\\node[core, below=1.15cm of q2, xshift=1.20cm, minimum width=10.4cm] (core)",
     "\\node[core, below=1.15cm of q2, xshift=1.50cm, minimum width=10.6cm] (core)"),
]
for a, b in reps:
    if a not in s:
        print("  !! missing:", a[:48])
        continue
    s = s.replace(a, b, 1)
    print("  ok:", a[:48])
io.open(p, "w", encoding="utf-8").write(s)
print("framework finalised")
