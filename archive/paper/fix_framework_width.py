# -*- coding: utf-8 -*-
"""fix_framework_width.py -- let the kernel box span the full width of the four
problem boxes, so that all four dashed arrows rise vertically into the boxes."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()

# calc is needed for the midpoint placement
s = s.replace("\\usetikzlibrary{arrows.meta,positioning,shapes.geometric,fit,backgrounds}",
              "\\usetikzlibrary{arrows.meta,positioning,shapes.geometric,fit,backgrounds,calc}", 1)

a = "\\node[core, below=1.15cm of q2, xshift=1.50cm, minimum width=10.6cm] (core)"
b = ("\\node[core, minimum width=14.82cm] (core)\n"
     "     at ($(q1.south)!0.5!(q4.south) + (0,-1.15cm)$)")
assert a in s, "kernel anchor missing"
s = s.replace(a, b, 1)

# four vertical dashed arrows, one per problem box
a2 = """\\draw[dar] (core.north -| q1.south) -- node[lbl, left=2pt, pos=0.5] {} (q1.south);
\\draw[dar] (core.north -| q3.south) -- (q3.south);
\\draw[dar] (core.north -| q4.south) -- (q4.south);
\\draw[dar] ([yshift=3pt]core.north) -- ([yshift=-3pt]q2.south);"""
b2 = """\\foreach \\q in {q1, q2, q3, q4}{%
  \\draw[dar] (core.north -| \\q.south) -- (\\q.south);
}"""
assert a2 in s, "arrow anchor missing"
s = s.replace(a2, b2, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("kernel box widened, arrows made vertical")
