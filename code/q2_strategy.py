#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
q2_strategy.py -- PROBLEM 2: where should the second detection point be placed?

Setting
-------
One station S1 has measured the apparent bearing (SVD) th1_hat of an
OMNIDIRECTIONAL source G.  The reading carries a bounded systematic error,
therefore the TRUE bearing of G seen from S1 satisfies
        theta1_true = th1_hat + d1 ,       |d1| <= eps   (eps = 1 deg)
and the only other a-priori information is
        * the source was received at S1  =>  r = |G - S1| <= R_max = 1500 m,
        * r > 5 m (otherwise the reading would have been "near"),
        * G lies inside the 1800 m circular arena,
        * every source can be received from at most R_eff <= 1500 m and from
          at least R_min = 1000 m, R_eff being unknown.

Hence the feasible source set is the thin sector
        Gset = { S1 + r*u(th1_hat + d) : r in (5, r_hi], |d| <= eps }
with r_hi = min(1500, distance from S1 to the arena boundary along that ray).

Design criterion (robust / minimax)
-----------------------------------
For a candidate second point S2 let D(S1,S2,G,d2) be the diameter of the
cross-fixing positioning region obtained from the two measured bearings
(th1_hat at S1 and bearing(S2->G)+d2 at S2, |d2| <= eps).  The second point is
chosen as

        S2* = argmin_{S2 in Omega}  max_{G in Gset, |d2|<=eps}  D(...)

with Omega = { S2 : |S2 - G| <= R_guard for every G in Gset }  the set of points
from which the second measurement is guaranteed to succeed when the worst-case
reception radius R_guard (1000 m) is assumed.  The candidate region reported in
the paper is the sub-level set { S2 : J(S2) <= (1+eta) * J(S2*) }.

Run: python q2_strategy.py
"""
import json
import math
import os

import geom_core as g

EPS = 1.0            # bearing error bound (deg)
R_MAX = 1500.0       # largest possible effective reception radius (m)
R_MIN = 1000.0       # smallest possible effective reception radius (m)
R_NEAR = 5.0         # "near" threshold (m)
ARENA_R = 1800.0     # target region radius (m)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


# ---------------------------------------------------------------------------
# feasible source set
# ---------------------------------------------------------------------------
def source_grid(s1, th1_hat, r_lo=R_NEAR + 1.0, r_hi=R_MAX,
                n_r=24, n_d=5, eps=EPS):
    """
    Discretisation of the feasible source set (thin sector) in the LOCAL frame
    of S1.  Returns a list of (r, delta, absolute position).
    Only points inside the arena are kept.
    """
    pts = []
    for i in range(n_r):
        # log spacing puts more weight on the short distances, where the
        # geometry is most sensitive
        f = i / float(n_r - 1)
        r = r_lo * (r_hi / r_lo) ** f
        for j in range(n_d):
            d = -eps + 2.0 * eps * j / float(n_d - 1)
            a = math.radians(th1_hat + d)
            p = (s1[0] + r * math.cos(a), s1[1] + r * math.sin(a))
            if math.hypot(p[0], p[1]) <= ARENA_R + 1e-9:
                pts.append((r, d, p))
    return pts


def worst_region_diameter(s1, s2, th1_hat, gset, eps=EPS, use_exact=True):
    """
    max over the feasible source set and over the second reading error of the
    diameter of the cross-fixing region.  Returns (J, detail) where detail
    records the worst case found (useful for the paper).
    """
    worst = 0.0
    info = None
    for (r, d, p) in gset:
        th2_true = g.bearing(s2[0], s2[1], p[0], p[1])
        for sgn in (-1.0, 1.0):
            th2_hat = th2_true + sgn * eps
            if use_exact:
                res = g.region_from_bearings([s1, s2], [th1_hat, th2_hat], eps)
                if res["empty"] or not res["bounded"]:
                    D = float("inf")
                else:
                    D = res["diameter"]
            else:
                d1 = r
                d2 = math.dist(s2, p)
                gam = abs(g.ang_diff(g.bearing(p[0], p[1], s1[0], s1[1]),
                                     g.bearing(p[0], p[1], s2[0], s2[1])))
                D = g.asymptotic_diameter(d1, d2, gam, eps)
                if d2 < 1e-6:
                    D = float("inf")
            if D > worst:
                worst = D
                info = {"r": r, "delta": d, "G": p, "sign2": sgn,
                        "theta2_hat": th2_hat, "D": D}
    return worst, info


def guard_feasible(s2, gset, r_guard=R_MIN):
    """True when S2 is within r_guard of every feasible source position."""
    for (_, _, p) in gset:
        if math.dist(s2, p) > r_guard + 1e-9:
            return False
    return True


# ---------------------------------------------------------------------------
# candidate grid in the local frame (S1 at origin, th1_hat along +x)
# ---------------------------------------------------------------------------
def local_to_world(p, s1, th1_hat):
    a = math.radians(th1_hat)
    x, y = p
    return (s1[0] + x * math.cos(a) - y * math.sin(a),
            s1[1] + x * math.sin(a) + y * math.cos(a))


def world_to_local(p, s1, th1_hat):
    a = math.radians(-th1_hat)
    dx, dy = p[0] - s1[0], p[1] - s1[1]
    return (dx * math.cos(a) - dy * math.sin(a),
            dx * math.sin(a) + dy * math.cos(a))


def candidate_grid(n_x=61, n_y=61, extent=2400.0):
    xs = [-extent + 2 * extent * i / (n_x - 1) for i in range(n_x)]
    ys = [-extent + 2 * extent * j / (n_y - 1) for j in range(n_y)]
    return [(x, y) for x in xs for y in ys]


def evaluate_grid(s1, th1_hat, gset, grid, r_guard=R_MIN, use_exact=True):
    """Evaluate J(S2) on a grid of candidate points given in world coordinates."""
    rows = []
    for s2 in grid:
        if not guard_feasible(s2, gset, r_guard):
            continue
        J, info = worst_region_diameter(s1, s2, th1_hat, gset, use_exact=use_exact)
        rows.append({"S2": s2, "J": J, "info": info})
    return rows


def main():
    import random
    rnd = random.Random(7)
    os.makedirs(OUT, exist_ok=True)

    # ---- a representative scenario: S1 inside the arena, source somewhere
    s1 = (-420.0, 260.0)
    th1_hat = 63.0
    gset = source_grid(s1, th1_hat)
    print("feasible source set size:", len(gset))
    r_hi = max(r for (r, _, _) in gset)
    print("r_hi along the measured bearing = %.1f m" % r_hi)

    # --- 1) one-dimensional study of the perpendicular family (small grid) ---
    print("\n--- perpendicular family: S2 = S1 + b*u(th1_hat +- 90) ---")
    print("   b(m)   J(m)     worst r(m)   gamma(deg)")
    for b in (400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200):
        for side in (+1, -1):
            loc = (b * math.cos(math.radians(90.0 * side)),
                   b * math.sin(math.radians(90.0 * side)))
            s2 = local_to_world(loc, s1, th1_hat)
            if not guard_feasible(s2, gset):
                print("   %6.0f  guard-infeasible (side %+d)" % (b, side))
                continue
            J, info = worst_region_diameter(s1, s2, th1_hat, gset)
            gam = g.region_intersection_angle(s1, s2, info["G"])
            print("   %6.0f  %8.3f  %8.1f   %8.3f   (side %+d)"
                  % (b, J, info["r"], gam, side))

    # --- 2) coarse global search over the plane -----------------------------
    print("\n--- coarse global search -------------------------------")
    grid = candidate_grid(n_x=81, n_y=81, extent=2400.0)
    rows = evaluate_grid(s1, th1_hat, gset, grid)
    rows.sort(key=lambda r: r["J"])
    print("feasible candidates:", len(rows))
    for r in rows[:10]:
        loc = world_to_local(r["S2"], s1, th1_hat)
        print("   S2=(%8.2f,%8.2f)  local=(%8.2f,%8.2f)  b=%7.2f  phi=%7.2f  J=%9.3f"
              % (r["S2"][0], r["S2"][1], loc[0], loc[1],
                 math.hypot(*loc), math.degrees(math.atan2(loc[1], loc[0])) % 360,
                 r["J"]))

    best = rows[0]
    with open(os.path.join(OUT, "q2_local_search.json"), "w", encoding="utf-8") as f:
        json.dump({"s1": s1, "th1_hat": th1_hat,
                   "best": {"S2": best["S2"], "J": best["J"]},
                   "top20": [{"S2": r["S2"], "J": r["J"]} for r in rows[:20]]},
                  f, ensure_ascii=False, indent=1)
    print("\nbest J = %.3f m at S2 = (%.2f, %.2f)" % (best["J"], *best["S2"]))
    print("saved", os.path.join(OUT, "q2_local_search.json"))


if __name__ == "__main__":
    main()
