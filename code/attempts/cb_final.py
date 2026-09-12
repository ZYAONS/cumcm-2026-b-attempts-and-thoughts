# -*- coding: utf-8 -*-
"""cb_final.py -- clear_bonus 的四池验证。"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "multi_pool.py")
s = io.open(p, encoding="utf-8").read()
i = s.index("CANDS = [")
j = s.index("]", s.index("s1000 + cert6")) + 1
new = '''CANDS = [
    ("cb500_now", dict(P4)),
    ("cb250", dict(P4, clear_bonus=250.0)),
    ("cb350", dict(P4, clear_bonus=350.0)),
    ("cb160", dict(P4, clear_bonus=160.0)),
]'''
s = s[:i] + new + s[j:]
io.open(p, "w", encoding="utf-8").write(s)
print("candidates updated")
