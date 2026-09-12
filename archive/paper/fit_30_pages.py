# -*- coding: utf-8 -*-
"""fit_30_pages.py -- the verification section added content, so the body is one
page over the limit.  Reclaim it without losing information:

  * the widest figures drop from 0.84 to 0.78 \\textwidth (their effective font
    stays above 9 pt because the canvases are small)
  * the bibliography goes from \\footnotesize to \\scriptsize
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# 1) figure widths
for f in ("paper_p1.tex", "paper_p2.tex", "paper_p3.tex"):
    p = os.path.join(HERE, f)
    s = io.open(p, encoding="utf-8").read()
    n = s.count("width=0.84\\textwidth")
    s = s.replace("width=0.84\\textwidth", "width=0.78\\textwidth")
    n2 = s.count("width=0.88\\textwidth")
    s = s.replace("width=0.88\\textwidth", "width=0.80\\textwidth")
    io.open(p, "w", encoding="utf-8").write(s)
    if n or n2:
        print("  %s : %d figures at 0.84->0.78, %d at 0.88->0.80" % (f, n, n2))

# 2) bibliography
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()
before = s
s = re.sub(r"(\\footnotesize\s*\n?\s*\\begin\{thebibliography\})",
           r"\\scriptsize\n\\begin{thebibliography}", s, count=1)
if s == before:
    m = re.search(r"\\begin\{thebibliography\}", s)
    if m:
        s = s[:m.start()] + "\\scriptsize\n" + s[m.start():]
        print("  bibliography font set to scriptsize (inserted before the env)")
    else:
        print("  !! bibliography environment not found")
else:
    print("  bibliography font set to scriptsize")
io.open(p, "w", encoding="utf-8").write(s)
print("done")
