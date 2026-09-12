# -*- coding: utf-8 -*-
"""disable_c1.py -- the "clear on the way" coupling measured neutral (882.2 s vs
881.3 s over 24 cases, i.e. inside the noise), so it is switched off: it adds a
code path and computation for no benefit.  Kept as a documented negative result.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()
a = '    "enroute_clear": True,      # C1: clear located sources passed on the way'
b = ('    "enroute_clear": False,     # C1 measured NEUTRAL (881.3 vs 882.2 s over\n'
     '                                # 24 cases): the priority bonus already\n'
     '                                # captures that coupling')
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("C1 disabled (measured neutral)")
