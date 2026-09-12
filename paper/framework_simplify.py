# -*- coding: utf-8 -*-
"""framework_simplify.py -- the extra q1->q3 arrow crowded the band between the
problem row and the kernel box; the kernel box plus the dashed arrows already
express that link, so the extra arrow goes away."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()
a = """% --- uncertainty propagates from problem 1 to problems 3/4 -------------
\\draw[ar, rounded corners=3pt]
      ([yshift=-2pt]q1.south) -- ++(0,-0.80)
      -- node[lbl, pos=0.55, below=1pt] {定位区域与 $\\sigma$ 直接用于位置估计}
      ([xshift=-1.30cm, yshift=-6pt]q3.south);
"""
assert a in s, "anchor missing"
s = s.replace(a, "", 1)
s = s.replace("\\node[core, below=1.75cm of q2, xshift=1.20cm, minimum width=10.4cm] (core)",
              "\\node[core, below=1.15cm of q2, xshift=1.20cm, minimum width=10.4cm] (core)", 1)
# label the dashed kernel arrows once, at the left hand side
s = s.replace("""\\draw[dar] (core.north -| q1.south) -- node[lbl, right=1.5pt] {} (q1.south);""",
              """\\draw[dar] (core.north -| q1.south) -- node[lbl, left=2pt, pos=0.5] {} (q1.south);""", 1)
io.open(p, "w", encoding="utf-8").write(s)
print("framework simplified")
