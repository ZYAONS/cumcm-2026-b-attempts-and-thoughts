# -*- coding: utf-8 -*-
"""fix_smart_wide.py -- the hybrid-comparison table is 111 pt too wide."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "smart_algorithms.tex")
s = io.open(p, encoding="utf-8").read()
a = """\\begin{tabular}{lccccc}
\\toprule
配置 & 平均站位数 & 最差完成率 & 平均时间/s & 失败算例 & 各池完成率 \\\\ \\midrule"""
b = """\\footnotesize
\\begin{tabular}{p{4.0cm}p{1.5cm}p{1.6cm}p{1.7cm}p{1.4cm}p{4.0cm}}
\\toprule
配置 & 站位数 & 最差完成率 & 时间/s & 失败 & 各池完成率（A/B/C/D） \\\\ \\midrule"""
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("wide table resized")
