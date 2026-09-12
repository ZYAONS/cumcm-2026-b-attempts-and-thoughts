# -*- coding: utf-8 -*-
"""fix_timeopt_doc.py -- the attempt-list longtable rows are 4.6 pt over."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "time_optimization.tex")
s = io.open(p, encoding="utf-8").read()
a = "\\begin{longtable}{p{0.5cm}p{3.6cm}p{3.0cm}p{2.6cm}p{3.1cm}}"
b = "\\footnotesize\n\\begin{longtable}{p{0.5cm}p{3.5cm}p{2.9cm}p{2.5cm}p{3.0cm}}"
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
s = s.replace("T3 & 认证限定为\"从未听到\"的频道 & 逻辑修正，去掉无谓搜索 & 有效 & 18 站位诊断",
              "T3 & 认证限定为"从未听到"的频道 & 逻辑修正 & 有效 & 18 站位诊断", 1)
io.open(p, "w", encoding="utf-8").write(s)
print("done")
