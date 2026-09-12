# -*- coding: utf-8 -*-
"""update_margin_cands.py -- try sparser lattices combined with the rim ring."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "margin_rim_scan.py")
s = io.open(p, encoding="utf-8").read()
i = s.index("CANDS = [")
j = s.index("]", s.index("r8 m700")) + 1
new = '''CANDS = [
    ("s950 r12 m700", cfg(950.0, 12, 700.0)),
    ("s1100 r12 m700", cfg(1100.0, 12, 700.0)),
    ("s1300 r12 m700", cfg(1300.0, 12, 700.0)),
    ("s1500 r12 m700", cfg(1500.0, 12, 700.0)),
    ("s1100 r16 m700", cfg(1100.0, 16, 700.0)),
    ("s1300 r16 m700", cfg(1300.0, 16, 700.0)),
    ("s1300 r12 m900", cfg(1300.0, 12, 900.0)),
    ("s1500 r16 m900", cfg(1500.0, 16, 900.0)),
]'''
s = s[:i] + new + s[j:]
io.open(p, "w", encoding="utf-8").write(s)
print("candidates updated")
