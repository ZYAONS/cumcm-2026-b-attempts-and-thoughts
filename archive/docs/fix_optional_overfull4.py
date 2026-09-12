# -*- coding: utf-8 -*-
"""fix_optional_overfull4.py -- last 5 pt: the header cell of the summary table."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "optional_changes.tex")
s = io.open(p, encoding="utf-8").read()
a = "\\begin{tabular}{p{4.2cm}p{2.9cm}p{2.7cm}p{4.2cm}}"
b = "\\begin{tabular}{p{4.0cm}p{2.7cm}p{2.6cm}p{4.4cm}}"
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
s = s.replace("问题四 正式测试 3 次 & \\textbf{11/11、12/12、11/11} & 1133 / 945 / 1193 & 三局全部清除 \\\\",
              "问题四 正式测试 3 次 & \\textbf{11/11、12/12、11/11} & 1133 / 945 / 1193 & 三局全清 \\\\", 1)
io.open(p, "w", encoding="utf-8").write(s)
print("done")
