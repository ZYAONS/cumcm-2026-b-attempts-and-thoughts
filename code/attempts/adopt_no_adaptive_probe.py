# -*- coding: utf-8 -*-
"""adopt_no_adaptive_probe.py -- 四池复核通过：问题三关掉 adaptive_probe。

四池各 30 例：-6.8 / -2.9 / -1.0 / -5.6 s per source，完成率全部 1.0000。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_data.py")
s = io.open(p, encoding="utf-8").read()
a = '"relocate": False, "sweep_center_first": True}'
b = '"relocate": False, "sweep_center_first": True, "adaptive_probe": False}'
if b in s:
    print("already adopted")
    sys.exit(0)
assert a in s, "P3 anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("P3: adaptive_probe=False adopted")
