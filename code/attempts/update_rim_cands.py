# -*- coding: utf-8 -*-
"""update_rim_cands.py -- widen the rim-ring scan."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "p4_rim.py")
s = io.open(p, encoding="utf-8").read()
i = s.index("CANDS = [")
j = s.index("]", s.index("rim_ring_n\": 12")) + 1
new = '''CANDS = [("rim0", {}),
         ("rim12", {"rim_ring_n": 12}),
         ("rim16", {"rim_ring_n": 16}),
         ("rim20", {"rim_ring_n": 20}),
         ("rim24", {"rim_ring_n": 24}),
         ("rim16 r1600", {"rim_ring_n": 16, "rim_ring_r": 1600.0}),
         ("rim16 r1700", {"rim_ring_n": 16, "rim_ring_r": 1700.0}),
         ("rim20 r1650", {"rim_ring_n": 20, "rim_ring_r": 1650.0})]'''
s = s[:i] + new + s[j:]
io.open(p, "w", encoding="utf-8").write(s)
print("candidates widened")
