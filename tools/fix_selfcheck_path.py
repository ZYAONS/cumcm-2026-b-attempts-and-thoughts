# -*- coding: utf-8 -*-
"""fix_selfcheck_path.py -- 去掉自检报告里的本机解释器目录名。"""
import io
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(HERE, "report", "self_check.md")
s = io.open(p, encoding="utf-8").read()
old = "3.9.15（miniconda39），本次新装"
new = "3.9.15，本次新装"
if old in s:
    s = s.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8").write(s)
    print("fixed the interpreter path note")
else:
    import re
    s2 = re.sub(r"（miniconda\d*）", "", s)
    s2 = re.sub(r"miniconda\d*", "本机解释器", s2)
    io.open(p, "w", encoding="utf-8").write(s2)
    print("fixed with fallback substitution")
