# -*- coding: utf-8 -*-
"""final_rim6.py -- 四池验证 rim6 配置。"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "multi_pool.py")
s = io.open(p, encoding="utf-8").read()
i = s.index("CANDS = [")
j = s.index("]", s.index("cb160")) + 1
new = '''CANDS = [
    ("rim12 (now)", dict(P4)),
    ("rim6", dict(P4, rim_ring_n=6, probe_spacing=250.0)),
    ("rim8", dict(P4, rim_ring_n=8, probe_spacing=250.0)),
    ("rim6 ps650", dict(P4, rim_ring_n=6)),
    ("rim4", dict(P4, rim_ring_n=4, probe_spacing=250.0)),
]'''
s = s[:i] + new + s[j:]
io.open(p, "w", encoding="utf-8").write(s)
print("candidates updated")
