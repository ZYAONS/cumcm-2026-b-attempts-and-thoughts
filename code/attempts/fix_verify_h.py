# -*- coding: utf-8 -*-
"""fix_verify_h.py -- the reference in H4 was wrong for degenerate inputs: with
fewer than three points the origin can never be in the interior, so the
reference must say False, not True.  (The implementation was right.)"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "verify_simulator.py")
s = io.open(p, encoding="utf-8").read()
a = """            hull_pts = __import__("geom_core").convex_hull(pts)
            ref = True
            if len(hull_pts) >= 3:"""
b = """            hull_pts = __import__("geom_core").convex_hull(pts)
            ref = False                     # a degenerate hull has no interior
            if len(hull_pts) >= 3:"""
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("H4 reference fixed")
