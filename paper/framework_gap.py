# -*- coding: utf-8 -*-
"""framework_gap.py -- a little more vertical air in the framework diagram."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()
a = "\\node[core, below=1.30cm of q2, xshift=1.20cm, minimum width=10.4cm] (core)"
b = "\\node[core, below=1.75cm of q2, xshift=1.20cm, minimum width=10.4cm] (core)"
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
a2 = """\\draw[ar, rounded corners=4pt] (q1.south) ++(0,-0.28) -- ++(0,-0.42)
      -- node[lbl, pos=0.5, below=1pt] {位置估计} ([xshift=-1.0cm]q3.south);"""
b2 = """\\draw[ar, rounded corners=3pt]
      ([yshift=-2pt]q1.south) -- ++(0,-0.80)
      -- node[lbl, pos=0.55, below=1pt] {定位区域与 $\\sigma$ 直接用于位置估计}
      ([xshift=-1.30cm, yshift=-6pt]q3.south);"""
assert a2 in s, "anchor 2 missing"
s = s.replace(a2, b2, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("framework spacing improved")
