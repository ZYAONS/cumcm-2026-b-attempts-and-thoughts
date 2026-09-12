# -*- coding: utf-8 -*-
"""fix_smart_doc.py -- two wide tables in the new report."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "smart_algorithms.tex")
s = io.open(p, encoding="utf-8").read()

pairs = [
    # the 6-column per-stop profile table: drop a column width, use small type
    ("\\begin{tabular}{lcccccc}\n\\toprule\n站点序 & 未解算 & 已听到 & 已定位 & 已清除 & 已认证不存在 & 本站检测次数 \\\\ \\midrule",
     "\\small\n\\begin{tabular}{lccccc}\n\\toprule\n站点序 & 未解算 & 已听到 & 已定位 & 已清除 & 本站检测次数 \\\\ \\midrule"),
    ("1（入场普查） & 15 & 5 & 0 & 0 & 0 & 19 \\\\",
     "1（入场普查） & 15 & 5 & 0 & 0 & 19 \\\\"),
    ("2 & 14 & 2 & 4 & 0 & 0 & 16 \\\\", "2 & 14 & 2 & 4 & 0 & 16 \\\\"),
    ("3 & 14 & 0 & 5 & 1 & 0 & 14 \\\\", "3 & 14 & 0 & 5 & 1 & 14 \\\\"),
    ("4 & 12 & 2 & 5 & 1 & 0 & 14 \\\\", "4 & 12 & 2 & 5 & 1 & 14 \\\\"),
    ("5 & 11 & 2 & 6 & 1 & 0 & 12 \\\\", "5 & 11 & 2 & 6 & 1 & 12 \\\\"),
    ("中后期各站 & 10 & 0$\\sim$2 & 0$\\sim$5 & 3$\\sim$10 & 0 & 10$\\sim$12 \\\\",
     "中后期各站 & 10 & 0$\\sim$2 & 0$\\sim$5 & 3$\\sim$10 & 10$\\sim$12 \\\\"),
    # attempt list longtable
    ("\\begin{longtable}{p{0.5cm}p{3.5cm}p{3.3cm}p{2.4cm}p{3.2cm}}",
     "\\scriptsize\n\\begin{longtable}{p{0.5cm}p{3.4cm}p{3.2cm}p{2.3cm}p{3.1cm}}"),
]
for a, b in pairs:
    if a not in s:
        print("  !! missing:", a[:46].replace("\n", " "))
        continue
    s = s.replace(a, b, 1)
    print("  ok:", a[:46].replace("\n", " "))
io.open(p, "w", encoding="utf-8").write(s)
print("done")
