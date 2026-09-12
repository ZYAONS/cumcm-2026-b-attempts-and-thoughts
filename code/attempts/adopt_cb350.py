# -*- coding: utf-8 -*-
"""adopt_cb350.py -- 四池验证显示 clear_bonus 350 严格不差（0.9978 / 595.7 s / 1 例失败），
比 500 略快，据此固化。"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_data.py")
s = io.open(p, encoding="utf-8").read()
old = '"clear_bonus": 500.0,'
new = '"clear_bonus": 350.0,'
assert old in s, "anchor missing"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("clear_bonus -> 350")
