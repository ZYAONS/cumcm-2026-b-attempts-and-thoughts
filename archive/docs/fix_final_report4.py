# -*- coding: utf-8 -*-
"""fix_final_report4.py -- 让过长的英文项目名可以断行。"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "final_report.tex")
s = io.open(p, encoding="utf-8").read()
old = "并与开源项目 JammersSimulator-Tool 做了交叉核对：12 个常量全部一致，"
new = "并与开源项目 Jammers\\-Simulator\\-Tool 做了交叉核对：12 个常量全部一致，"
assert old in s, "anchor missing"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("hyphenation added")
