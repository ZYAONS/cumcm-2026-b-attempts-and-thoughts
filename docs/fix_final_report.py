# -*- coding: utf-8 -*-
"""fix_final_report.py -- 把正文里裸写的上标放进数学模式。"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "final_report.tex")
s = io.open(p, encoding="utf-8").read()

repl = [
    ("给出 O(n^2) 顶点枚举算法", "给出 $O(n^2)$ 顶点枚举算法"),
    ("算法复杂度为 O(n^2) 次求交与 O(n^3) 次判定。",
     "算法复杂度为 $O(n^2)$ 次求交与 $O(n^3)$ 次判定。"),
    ("偏差小于 $10^{-9}$ 秒", "偏差小于 $10^{-9}$ 秒"),
    ("行程 13035 m", "行程 13035 m"),
]
for a, b in repl:
    s = s.replace(a, b)

# 兜底：任何不在 $...$ 内的裸 ^ 都包起来
out = []
for line in s.split("\n"):
    if "$" not in line and "^" in line:
        line = re.sub(r"([A-Za-z0-9()]+)\^(\{[^}]*\}|[0-9])", r"$\1^\2$", line)
    out.append(line)
s = "\n".join(out)
io.open(p, "w", encoding="utf-8").write(s)
print("superscripts wrapped")
