# -*- coding: utf-8 -*-
"""vantage_short_baseline.py -- give the rim case the baseline it actually needs.

State of the trace after the creep was added (seeds 100006/102009):

    obs0 at (-1800,  0) brg 298.5   dist to source 86 m   LIT
    obs1 at (-1781,-36) brg 297.2   dist to source 45 m   LIT
    estimate (-1780.7, -35.6) sigma = 670 m      (true position (-1760, -76))
    obs0 at ( 1800,  0) brg 166.0   dist to source 85 m   LIT
    obs1 at ( 1761, 10) brg 166.0   dist to source 45 m   LIT
    estimate ( 1760.7,   9.8) sigma = 26180 m    (true position ( 1717,  21))

The creep does obtain a second bearing, and the estimated POSITION is accurate to
about 40 m.  But both bearings were taken along the same ray, so they differ by
only 1.3 degrees: two nearly parallel cuts intersect in a very long sliver and
sigma stays at hundreds of metres, far above the localisation threshold, so no
clear task is ever generated.

Creeping solves "staying lit" but not "having a baseline".  Once two bearings are
in hand the robot also knows the source is CLOSE -- it had to halve the hop to stay
lit -- so a very short lateral offset is now safe (the lit half plane passes
through the source, and the second observation point sits only ~45 m from it).

Fix: with two bearings already collected, place the next vantage at a SHORT
lateral offset (`vantage_short_step`, 35 m) at a wide angle.  That is both inside
the lit region and, at 45 m range, a 35 m baseline subtends about 40 degrees --
plenty for a good fix.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

a = '    "vantage_step_onray": 200.0,  # creep along the ray instead of jumping'
b = ('    "vantage_short_step": 35.0,   # short lateral baseline once 2 bearings exist\n'
     '    "vantage_step_onray": 200.0,  # creep along the ray instead of jumping')
assert a in s, "param anchor"
s = s.replace(a, b, 1)

a = """            if tries <= 0:
                phi0 = min(phi0, 45.0)
            elif tries == 1:
                phi0 = min(phi0, 20.0)
            else:"""
b = """            if tries <= 0:
                phi0 = min(phi0, 45.0)
            elif tries == 1:
                phi0 = min(phi0, 20.0)
            elif len(self.obs.get(c, [])) >= 2:
                # Two bearings exist but they were taken along the same ray, so
                # they are nearly parallel and sigma is huge.  The source is known
                # to be close (the creep had to halve its hop), so a SHORT lateral
                # offset is both safe and geometrically decisive.
                phi0 = 70.0
                b = float(self.p.get("vantage_short_step", 35.0))
                onray = False
            else:"""
assert a in s, "stage anchor"
s = s.replace(a, b, 1)

a = """                if (self.vantage_tries.get(c, 0) >= self.p["vantage_max_tries"]
                        and self.onray_tries.get(c, 0)
                        >= self.p.get("vantage_onray_tries", 16)):
                    continue"""
b = """                if (self.vantage_tries.get(c, 0) >= self.p["vantage_max_tries"]
                        and self.onray_tries.get(c, 0)
                        >= self.p.get("vantage_onray_tries", 16)
                        and len(self.obs.get(c, [])) >= 2):
                    continue"""
assert a in s, "budget anchor"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("short-baseline vantage installed")
