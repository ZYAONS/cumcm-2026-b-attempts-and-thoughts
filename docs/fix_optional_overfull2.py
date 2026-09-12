# -*- coding: utf-8 -*-
"""fix_optional_overfull2.py -- close the last overfull boxes of the report."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "optional_changes.tex")
s = io.open(p, encoding="utf-8").read()

pairs = [
    # negative list: narrower columns
    ("\\begin{longtable}{p{0.6cm}p{3.6cm}p{3.3cm}p{3.2cm}p{2.6cm}}",
     "\\begin{longtable}{p{0.6cm}p{3.4cm}p{3.1cm}p{3.0cm}p{2.4cm}}"),
    ("N10 & 全域外环 \\texttt{outer\\_ring\\_gap}$>0$ & 时间 $\\times2.4$、行程 $\\times2.7$ & \\textbf{负优化} & 30 例对照 \\\\",
     "N10 & 全域外环 \\texttt{outer\\_ring\\_gap}$>0$ & 时间 $\\times2.4$ & \\textbf{负优化} & 30 例对照 \\\\"),
    ("N11 & Or-opt 初版（循环内全量重算路径） & 单局 CPU 数十秒（$O(n^4)$） & \\textbf{性能负优化} &\n已改为只优化序列前 12 个任务 \\\\",
     "N11 & Or-opt 初版（循环内全量重算） & 单局 CPU 数十秒 & \\textbf{性能负优化} & 见正文 \\\\"),
    # summary table: shrink further
    ("\\begin{tabular}{p{4.6cm}p{3.4cm}p{3.0cm}p{4.4cm}}",
     "\\begin{tabular}{p{4.4cm}p{3.1cm}p{2.9cm}p{4.3cm}}"),
    ("问题四 正式测试 3 次 & \\textbf{11/11、12/12、11/11} & 1133.1 / 945.2 / 1193.4 & 三局全部清除 \\\\",
     "问题四 正式测试 3 次 & \\textbf{11/11、12/12、11/11} & 1133 / 945 / 1193 & 三局全部清除 \\\\"),
]
for a, b in pairs:
    if a not in s:
        print("  !! missing:", a[:52].replace("\n", " "))
        continue
    s = s.replace(a, b, 1)
    print("  ok:", a[:52].replace("\n", " "))
io.open(p, "w", encoding="utf-8").write(s)
print("done")
