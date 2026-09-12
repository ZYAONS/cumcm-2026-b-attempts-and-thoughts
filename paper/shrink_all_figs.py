# -*- coding: utf-8 -*-
"""shrink_all_figs.py -- 把所有插图宽度再缩 12%，把正文压回 30 页。"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
tot = 0
for f in ("paper_p1.tex", "paper_p2.tex", "paper_p3.tex"):
    p = os.path.join(HERE, f)
    s = io.open(p, encoding="utf-8").read()

    def shrink(m):
        global tot
        tot += 1
        return "width=%.2f\\textwidth" % (float(m.group(1)) * 0.88)

    s = re.sub(r"width=([0-9.]+)\\textwidth", shrink, s)
    io.open(p, "w", encoding="utf-8").write(s)
print("缩小 %d 张图" % tot)
