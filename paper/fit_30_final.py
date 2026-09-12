# -*- coding: utf-8 -*-
"""fit_30_final.py -- reclaim the last page.

  * the bibliography drops from \\footnotesize to \\scriptsize (47 entries; the
    paper keeps every reference, only the type size changes)
  * the two sensitivity FIGURES move to the appendix: their data is already in
    tables 10 and 13, so nothing is lost and the body gains about a page
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))

p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()
a = "\\AtBeginEnvironment{thebibliography}{\\footnotesize}"
b = "\\AtBeginEnvironment{thebibliography}{\\scriptsize}"
assert a in s, "bibliography anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("bibliography -> scriptsize")

# move the two sensitivity figures into the appendix
src = os.path.join(HERE, "paper_p3.tex")
s = io.open(src, encoding="utf-8").read()
blocks = []
for key in ("fig:q3sens", "fig:q4sens"):
    i = s.index("\\label{%s}" % key)
    j = s.rindex("\\begin{figure}", 0, i)
    k = s.index("\\end{figure}", i) + len("\\end{figure}")
    blocks.append(s[j:k])
    s = s[:j] + s[k:]
s = s.replace("\n\n\n", "\n\n")
io.open(src, "w", encoding="utf-8").write(s)
print("moved %d figures out of the body" % len(blocks))

dst = os.path.join(HERE, "paper_p4.tex")
t = io.open(dst, encoding="utf-8").read()
note = ("\n\\section*{B\\quad 灵敏度图（正文表 10、表 13 的图形表示）}\n"
        "\\addcontentsline{toc}{section}{B\\quad 灵敏度图}\n\n"
        + "\n\n".join(blocks) + "\n")
t = t.rstrip() + "\n" + note

# the appendix uses a continuation numbering: keep the figures where they are,
# the caption already carries its own text
io.open(dst, "w", encoding="utf-8").write(t)
print("appendix B added with the two figures")
