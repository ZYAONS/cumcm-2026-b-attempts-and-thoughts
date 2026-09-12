# -*- coding: utf-8 -*-
"""squeeze.py -- 把正文压回 30 页（行距 1.18 -> 1.12）。"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()
m = re.search(r"\\renewcommand\*\{\\baselinestretch\}\{([0-9.]+)\}", s)
if not m:
    print("!! baselinestretch 未找到")
    sys.exit(1)
old = m.group(0)
new = "\\renewcommand*{\\baselinestretch}{1.12}"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("行距 %s -> 1.12" % m.group(1))
