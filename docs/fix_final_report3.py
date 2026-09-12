# -*- coding: utf-8 -*-
"""fix_final_report3.py -- 修掉最后一处 overfull（基线对比表过宽）。"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "final_report.tex")
s = io.open(p, encoding="utf-8").read()
a = "\\begin{tabular}{lc}\n\\toprule\n策略 & 最坏直径 m \\\\ \\midrule"
b = "\\small\n\\begin{tabular}{lc}\n\\toprule\n策略 & 最坏直径 m \\\\ \\midrule"
if a in s:
    s = s.replace(a, b, 1)
    print("narrowed the baseline table")
else:
    print("anchor missing, trying the wide-caption fix")
io.open(p, "w", encoding="utf-8").write(s)
