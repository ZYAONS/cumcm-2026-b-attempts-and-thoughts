#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
q1_scan.py -- numerical study: when does the disk whose diameter equals the
positioning-region diameter fail to cover that region?
Run: python q1_scan.py
"""
import math
import random
import geom_core as g

rnd = random.Random(12345)
EPS = 1.0
n_fail = 0
n_ok = 0
n_unbounded = 0
n_empty = 0
worst = []
trials = []

for t in range(20000):
    R = 1800.0
    # random stations inside the arena
    def rp():
        r = R * math.sqrt(rnd.random())
        a = 2 * math.pi * rnd.random()
        return (r * math.cos(a), r * math.sin(a))
    n_st = rnd.choice([2, 2, 2, 3, 4])
    sts = [rp() for _ in range(n_st)]
    # keep the stations well separated so the geometry is not degenerate
    if min(math.dist(a, b) for i, a in enumerate(sts) for b in sts[i + 1:]) < 200:
        continue
    # random source
    G = rp()
    if min(math.dist(s, G) for s in sts) < 30 or max(math.dist(s, G) for s in sts) > 1500:
        continue
    bs = [g.bearing(*s, *G) for s in sts]
    res = g.region_from_bearings(sts, bs, EPS)
    if res["empty"]:
        n_empty += 1
        continue
    if not res["bounded"]:
        n_unbounded += 1
        continue
    A, B = res["d_pair"]
    others = [v for v in res["vertices"]
              if math.dist(v, A) > 1e-6 and math.dist(v, B) > 1e-6]
    viol = g.diameter_disk_slack(others, A, B) if others else -1.0
    if viol > 1e-9:
        n_fail += 1
    else:
        n_ok += 1
    trials.append((viol, n_st, res["diameter"], res["mec"][2], A, B, sts, G))

print("trials kept      :", n_fail + n_ok)
print("covered          :", n_ok)
print("NOT covered      :", n_fail)
print("unbounded regions:", n_unbounded, " empty regions:", n_empty)
trials.sort(key=lambda r: -r[0])
print("\nlargest violations (violation, n_st, D, R_mec, D/2 - R_mec):")
for r in trials[:8]:
    print("  %12.4f  n=%d  D=%9.3f  Rmec=%9.3f  D/2-Rmec=%8.4f  n_vert=%d"
          % (r[0], r[1], r[2], r[3], r[2] / 2 - r[3], 0))
if trials:
    print("\nmedian D/2 - R_mec = %.6f" % sorted(r[2] / 2 - r[3] for r in trials)[len(trials) // 2])
    print("max    D/2 - R_mec = %.6f" % max(r[2] / 2 - r[3] for r in trials))
