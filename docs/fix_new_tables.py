# -*- coding: utf-8 -*-
"""fix_new_tables.py -- the two new tables are over wide."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "optional_changes.tex")
s = io.open(p, encoding="utf-8").read()

pairs = [
    # correlation table (6 columns, long header)
    ("\\begin{tabular}{lccccc}\n\\toprule\n$a$ & 误差标准差 & $\\pm1^{\\circ}$ 截断比例 & 相隔 50 m 的误差差 & 漏源 / 总数 & 加权完成率 \\\\ \\midrule",
     "\\small\n\\begin{tabular}{lccccc}\n\\toprule\n$a$ & 标准差 & 截断比例 & 50 m 误差差 & 漏源 / 总数 & 完成率 \\\\ \\midrule"),
    # time budget table
    ("\\begin{tabular}{lcccc}\n\\toprule\n任务类 & 次数/例 & 行程/m & 占行程 & 占虚拟时间 \\\\ \\midrule",
     "\\small\n\\begin{tabular}{p{3.4cm}p{1.8cm}p{2.2cm}p{2.0cm}p{2.4cm}}\n\\toprule\n任务类 & 次数/例 & 行程/m & 占行程 & 占虚拟时间 \\\\ \\midrule"),
]
for a, b in pairs:
    if a not in s:
        print("  !! missing:", a[:50].replace("\n", " "))
        continue
    s = s.replace(a, b, 1)
    print("  ok:", a[:50].replace("\n", " "))
io.open(p, "w", encoding="utf-8").write(s)
print("done")
