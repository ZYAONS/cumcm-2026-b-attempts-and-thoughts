# -*- coding: utf-8 -*-
"""fix_arena_attr.py -- Brain stores the radius in self.arena_r."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()
a = 'lim = self.arena_radius - 2.0 * self.p["verify_grid"]'
b = 'lim = self.arena_r - 2.0 * self.p["verify_grid"]'
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("arena attribute fixed")
