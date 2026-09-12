# -*- coding: utf-8 -*-
"""fix_summary_table.py -- the last 5 pt of the summary table."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "optional_changes.tex")
s = io.open(p, encoding="utf-8").read()
a = "\\begin{tabular}{p{4.4cm}p{3.1cm}p{2.9cm}p{4.3cm}}"
b = "\\footnotesize\n\\begin{tabular}{p{4.3cm}p{3.0cm}p{2.8cm}p{4.3cm}}"
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("summary table set to footnotesize")
