# -*- coding: utf-8 -*-
"""fix_docs8.py -- last 1.5 pt overfull in the field-spec table."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "simulator_spec.tex")
s = io.open(p, encoding="utf-8").read()
a = "全部 & --- & real\\_timestamp\\_ms,\\newline virtual\\_time\\_s & 每个成功响应都带 \\\\"
b = "全部 & --- & real\\_timestamp\\_\\hspace{0pt}ms,\\newline virtual\\_time\\_s & 每个成功响应都带 \\\\"
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
