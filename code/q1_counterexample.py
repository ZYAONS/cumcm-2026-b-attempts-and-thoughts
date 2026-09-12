#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
q1_counterexample.py -- dig into the configurations where the disk having the
positioning-region diameter as its diameter fails to cover the region.
Run: python q1_counterexample.py
"""
import math
import random
import geom_core as g

rnd = random.Random(12345)
EPS = 1.0
found = []

for t in range(200000):
    R = 1800.0

    def rp(rand):
        r = R * math.sqrt(rand.random())
        a = 2 * math.pi * rand.random()
        return (r * math.cos(a), r * math.sin(a))

    sts = [rp(rnd) for _ in range(2)]
    if math.dist(sts[0], sts[1]) < 200:
        continue
    G = rp(rnd)
    if min(math.dist(s, G) for s in sts) < 30 or max(math.dist(s, G) for s in sts) > 1500:
        continue
    bs = [g.bearing(*s, *G) for s in sts]
    res = g.region_from_bearings(sts, bs, EPS)
    if res["empty"] or not res["bounded"]:
        continue
    A, B = res["d_pair"]
    others = [v for v in res["vertices"]
              if math.dist(v, A) > 1e-6 and math.dist(v, B) > 1e-6]
    if not others:
        continue
    viol = g.diameter_disk_slack(others, A, B)
    if viol > 1e-6:
        found.append((viol, sts, G, bs, res, A, B, others))
    if len(found) >= 4000:
        break

found.sort(key=lambda r: -r[0])
print("number of failing configurations found:", len(found))
if found:
    viol, sts, G, bs, res, A, B, others = found[0]
    print("\n=== worst counterexample ===")
    print("stations :", ["(%.3f, %.3f)" % s for s in sts])
    print("true source : (%.3f, %.3f)" % G)
    print("bearings (deg): %s" % ["%.4f" % b for b in bs])
    print("intersection angle at source: %.4f deg"
          % g.region_intersection_angle(sts[0], sts[1], G))
    print("region vertices:")
    for v in res["vertices"]:
        print("    (%10.4f, %10.4f)   dist to source %8.4f" % (v[0], v[1], math.dist(v, G)))
    print("diameter D = %.6f between (%.4f, %.4f) and (%.4f, %.4f)"
          % ((res["diameter"],) + A + B))
    print("R_mec = %.6f  ->  D/2 = %.6f, extra radius = %.6f m"
          % (res["mec"][2], res["diameter"] / 2.0, res["mec"][2] - res["diameter"] / 2.0))
    for v in others:
        d = (v[0] - A[0]) * (v[0] - B[0]) + (v[1] - A[1]) * (v[1] - B[1])
        print("    vertex (%.4f, %.4f): Thales product = %+.4f  -> outside circle by %.4f m"
              % (v[0], v[1], d, d / (2.0 * res["mec"][2])))
    # angle check for the quadrilateral
    verts = res["vertices"]
    for i in range(len(verts)):
        p0 = verts[i - 1]
        p1 = verts[i]
        p2 = verts[(i + 1) % len(verts)]
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        cosang = (v1[0] * v2[0] + v1[1] * v2[1]) / (math.hypot(*v1) * math.hypot(*v2))
        print("    interior angle at vertex %d = %.4f deg" % (i, math.degrees(math.acos(max(-1, min(1, cosang))))))

    print("\nrelative size of the violation:")
    for viol, sts, G, bs, res, A, B, others in found[:10]:
        print("   viol=%10.4f m^2   D=%8.3f m   extra radius=%8.5f m   gamma=%7.3f deg"
              % (viol, res["diameter"], res["mec"][2] - res["diameter"] / 2.0,
                 g.region_intersection_angle(sts[0], sts[1], G)))
