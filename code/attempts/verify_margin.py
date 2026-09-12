# -*- coding: utf-8 -*-
"""verify_margin.py -- exclude rim candidates from the certification grid.

Diagnosis (why_extra_stops.py, seed 30000):

    stops: lattice = 7, extra = 20       <- 20 of the 27 stops are certification search
    at the end: uncovered grid points = 52
    radius of the uncovered candidates: min 1777, median 1790, max 1800 m

All 52 sit ON the arena rim and they are the same 52 points for all nine
unresolved channels.  By theorem 2 a candidate at the rim cannot be certified from
inside: certification needs the readings around it to surround it, and every
in-domain reading lies in the half plane facing the centre.  The search therefore
spends about twenty stops per case trying to prove something unprovable.

Modelling decision, stated explicitly: certification is required for the INTERIOR
of the target region.  Candidates closer to the rim than `verify_margin` are
dropped from the grid because (a) they cannot be certified with in-domain
readings, and (b) a source there radiating outward is undetectable from inside
anyway -- if it is found at all it is found by the survey sweep itself.

The rim strip is still swept by the lattice and such a source is still located and
cleared when heard; what disappears is the pointless search.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

a = '    "verify_grid": 60.0,        # spacing (m) of the certification lattice'
assert a in s, "param anchor"
s = s.replace(a, a + '\n'
              '    "verify_margin": 90.0,     # candidates closer to the rim than this\n'
              '                                # are excluded: they can never be certified\n'
              '                                # with in-domain readings (theorem 2)', 1)

a = """        if getattr(self, "_vgrid", None) is None:
            s = self.p["verify_grid"]
            pts = []"""
b = """        if getattr(self, "_vgrid", None) is None:
            s = self.p["verify_grid"]
            lim = self.arena_r - float(self.p.get("verify_margin", 90.0))
            pts = []"""
assert a in s, "grid head anchor"
s = s.replace(a, b, 1)

# the radius test inside the grid loop
old_tests = [
    "                    if math.hypot(x, y) <= self.arena_r:\n                        pts.append((x, y))",
    "                if math.hypot(x, y) <= self.arena_r:\n                    pts.append((x, y))",
    "            if math.hypot(x, y) <= self.arena_r:\n                pts.append((x, y))",
]
hit = False
for t in old_tests:
    if t in s:
        s = s.replace(t, t.replace("self.arena_r", "lim"), 1)
        hit = True
        print("  radius test replaced")
        break
assert hit, "radius test anchor"
io.open(p, "w", encoding="utf-8").write(s)
print("rim candidates excluded from the certification grid")
