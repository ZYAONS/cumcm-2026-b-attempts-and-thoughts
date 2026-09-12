# -*- coding: utf-8 -*-
"""fix_final_report2.py -- 把正文里裸写的下标也放进数学模式。"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "final_report.tex")
s = io.open(p, encoding="utf-8").read()

# 逐行处理：不在 $...$ 内的裸下标 foo_bar 或 foo_{bar}
out = []
for line in s.split("\n"):
    if line.lstrip().startswith("%"):
        out.append(line)
        continue
    # 跳过已有数学模式的片段
    parts = re.split(r"(\$[^$]*\$)", line)
    for i, seg in enumerate(parts):
        if i % 2 == 1:
            continue
        seg = re.sub(r"\b([A-Za-z])\s*_\s*(\{[^}]*\}|[A-Za-z0-9])",
                     r"$\1_\2$", seg)
        parts[i] = seg
    out.append("".join(parts))
s = "\n".join(out)
io.open(p, "w", encoding="utf-8").write(s)
print("subscripts wrapped")
print([l for l in s.split("\n") if "d_" in l][:3])
