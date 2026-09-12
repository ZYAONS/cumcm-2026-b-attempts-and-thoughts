#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
q1_smoke.py -- quick sanity checks of geom_core before the full Q1 study.
Run:  python q1_smoke.py
"""
import math
import geom_core as g

# ---------------------------------------------------------------- case 1
# two stations on the x axis, source placed so that the intersection angle is
# close to 90 degrees (the geometrically best configuration)
S1 = (0.0, 0.0)
S2 = (1200.0, 0.0)
G = (600.0, 900.0)
th1 = g.bearing(*S1, *G)
th2 = g.bearing(*S2, *G)
print("true bearings", th1, th2)
print("intersection angle", g.region_intersection_angle(S1, S2, G))

res = g.region_from_bearings([S1, S2], [th1, th2], 1.0)
print("empty", res["empty"], "bounded", res["bounded"])
for v in res["vertices"]:
    print("   vertex  %10.3f %10.3f   dist to G = %8.3f" %
          (v[0], v[1], math.dist(v, G)))
print("diameter  %.4f" % res["diameter"])
print("cover_ok", res["cover_ok"], "slack %.6f" % res["cover_slack"])
print("mec", res["mec"])

# analytic check
d1 = math.dist(S1, G)
d2 = math.dist(S2, G)
gam = g.region_intersection_angle(S1, S2, G)
print("asymptotic D = %.4f" % g.asymptotic_diameter(d1, d2, gam))
print("calipers     D = %.4f" % g.rotating_calipers_diameter(res["vertices"])[0])

# the true source must lie inside the region (it is consistent with both
# measurements when the errors are inside +-1 deg)
print("G inside region:", g.halfplanes_satisfied(
    g.halfplanes_from_bearings([S1, S2], [th1, th2], 1.0), G[0], G[1]))

# ---------------------------------------------------------------- case 2
# nearly parallel bearings -> the region is unbounded
S1b = (0.0, 0.0)
S2b = (100.0, 0.0)
th1b, th2b = 45.0, 45.5
res2 = g.region_from_bearings([S1b, S2b], [th1b, th2b], 1.0)
print("\nparallel case: bounded =", res2["bounded"], "empty =", res2["empty"],
      "recession_dir =", res2.get("recession_dir"))

# ---------------------------------------------------------------- case 3
# inconsistent bearings -> empty region
res3 = g.region_from_bearings([S1, S2], [90.0, 90.0], 1.0)
print("inconsistent case: empty =", res3["empty"], "bounded =", res3["bounded"])

# ---------------------------------------------------------------- case 4
# four stations: the region shrinks and stays convex
sts = [(-800.0, -600.0), (900.0, -400.0), (300.0, 1100.0), (-500.0, 700.0)]
bs = [g.bearing(*s, *G) for s in sts]
res4 = g.region_from_bearings(sts, bs, 1.0)
print("\n4 stations: n_vertices =", len(res4["vertices"]),
      "diameter = %.4f" % res4["diameter"],
      "cover_ok =", res4["cover_ok"],
      "mec_r = %.4f" % res4["mec"][2])
