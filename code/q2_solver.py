#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
q2_solver.py -- PROBLEM 2 (complete study)

Contents
  1. solve_second_point()  : the robust (minimax) design of the second station
  2. study_guard_tradeoff(): how the optimum depends on the assumed worst-case
                             reception radius (the "risk" parameter)
  3. candidate_region()    : the eta-sub-level set, i.e. the answer to
                             "give the candidate region for the second point"
  4. monte_carlo_check()   : Monte-Carlo verification against the true errors
  5. baseline comparison   : the proposed rule vs naive rules and the oracle
Outputs: ../data/q2_*.csv, ../data/q2_summary.json
Run: python q2_solver.py
"""
import csv
import json
import math
import os
import random

import geom_core as g

EPS = 1.0
R_MAX = 1500.0
R_MIN = 1000.0
R_NEAR = 5.0
ARENA_R = 1800.0
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))


# ---------------------------------------------------------------------------
# geometry helpers in the local frame of S1 (bearing direction = +x axis)
# ---------------------------------------------------------------------------
def local_to_world(p, s1, th1_hat):
    a = math.radians(th1_hat)
    return (s1[0] + p[0] * math.cos(a) - p[1] * math.sin(a),
            s1[1] + p[0] * math.sin(a) + p[1] * math.cos(a))


def world_to_local(p, s1, th1_hat):
    a = math.radians(-th1_hat)
    dx, dy = p[0] - s1[0], p[1] - s1[1]
    return (dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a))


def sector_points(s1, th1_hat, r_lo=R_NEAR + 1.0, r_hi=R_MAX, n_r=32, n_d=7, eps=EPS):
    pts = []
    for i in range(n_r):
        f = i / float(n_r - 1)
        r = r_lo * (r_hi / r_lo) ** f
        for j in range(n_d):
            d = -eps + 2.0 * eps * j / float(n_d - 1)
            a = math.radians(th1_hat + d)
            p = (s1[0] + r * math.cos(a), s1[1] + r * math.sin(a))
            if math.hypot(p[0], p[1]) <= ARENA_R:
                pts.append((r, d, p))
    return pts


def worst_diameter(s1, s2, th1_hat, gset, eps=EPS):
    """Worst-case diameter of the two-station cross-fixing region."""
    worst = 0.0
    info = None
    for (r, d, p) in gset:
        th2 = g.bearing(s2[0], s2[1], p[0], p[1])
        for sgn in (-1.0, 1.0):
            res = g.region_from_bearings([s1, s2], [th1_hat, th2 + sgn * eps], eps)
            if res["empty"] or not res["bounded"]:
                D = float("inf")
            else:
                D = res["diameter"]
            if D > worst:
                worst = D
                info = {"r": r, "delta": d, "G": p, "sign2": sgn, "D": D}
    return worst, info


def guard_ok(s2, gset, r_guard):
    return all(math.dist(s2, p) <= r_guard + 1e-9 for (_, _, p) in gset)


def guard_margin(s2, gset):
    return max(math.dist(s2, p) for (_, _, p) in gset)


# ---------------------------------------------------------------------------
# 1. solve the design problem
# ---------------------------------------------------------------------------
def solve_second_point(s1, th1_hat, r_guard=R_MIN, r_hi=R_MAX,
                       n_b=61, n_phi=121, phi_span=75.0, refine=True):
    """
    Grid + local refinement minimisation of J(S2) = worst-case region diameter
    over the polar family (b, phi) centred on the measured bearing direction.
    Returns a dict describing the optimum.
    """
    gset = sector_points(s1, th1_hat, r_hi=r_hi)
    best = None
    for ib in range(n_b):
        b = 60.0 + (r_guard + 120.0 - 60.0) * ib / float(n_b - 1)
        for ip in range(n_phi):
            phi = -phi_span + 2.0 * phi_span * ip / float(n_phi - 1)
            loc = (b * math.cos(math.radians(phi)), b * math.sin(math.radians(phi)))
            s2 = local_to_world(loc, s1, th1_hat)
            if not guard_ok(s2, gset, r_guard):
                continue
            J, info = worst_diameter(s1, s2, th1_hat, gset)
            if best is None or J < best["J"]:
                best = {"b": b, "phi": phi, "S2": s2, "J": J, "info": info,
                        "guard_margin": guard_margin(s2, gset)}
    if best is None:
        return None
    # local refinement (coordinate descent on (b, phi))
    if refine:
        step_b, step_p = 25.0, 4.0
        for _ in range(40):
            improved = False
            for db, dp in ((step_b, 0), (-step_b, 0), (0, step_p), (0, -step_p)):
                b, phi = best["b"] + db, best["phi"] + dp
                if b <= 20.0 or abs(phi) > 88.0:
                    continue
                loc = (b * math.cos(math.radians(phi)), b * math.sin(math.radians(phi)))
                s2 = local_to_world(loc, s1, th1_hat)
                if not guard_ok(s2, gset, r_guard):
                    continue
                J, info = worst_diameter(s1, s2, th1_hat, gset)
                if J < best["J"] - 1e-9:
                    best = {"b": b, "phi": phi, "S2": s2, "J": J, "info": info,
                            "guard_margin": guard_margin(s2, gset)}
                    improved = True
            if not improved:
                step_b *= 0.5
                step_p *= 0.5
                if step_b < 0.5:
                    break
    best["gset"] = gset
    best["r_guard"] = r_guard
    return best


# ---------------------------------------------------------------------------
# 2. trade-off between the risk parameter and the attainable accuracy
# ---------------------------------------------------------------------------
def study_guard_tradeoff(s1=(-420.0, 260.0), th1_hat=63.0):
    rows = []
    for rg in (1000, 1050, 1100, 1150, 1200, 1300, 1400, 1500):
        sol = solve_second_point(s1, th1_hat, r_guard=float(rg))
        if sol is None:
            rows.append({"r_guard": rg, "feasible": 0})
            continue
        rows.append({"r_guard": rg, "feasible": 1, "b": sol["b"], "phi": sol["phi"],
                     "J": sol["J"], "worst_r": sol["info"]["r"],
                     "S2_x": sol["S2"][0], "S2_y": sol["S2"][1]})
        print("  r_guard=%4d  b=%7.1f  phi=%+6.2f  J=%8.3f m (worst source r=%6.1f m)"
              % (rg, sol["b"], sol["phi"], sol["J"], sol["info"]["r"]))
    return rows


# ---------------------------------------------------------------------------
# 3. candidate region = eta sub-level set
# ---------------------------------------------------------------------------
def candidate_region(sol, eta=0.15, n_b=41, n_phi=81, phi_span=75.0):
    gset = sol["gset"]
    s1 = None
    rows = []
    for ib in range(n_b):
        b = 200.0 + 1400.0 * ib / float(n_b - 1)
        for ip in range(n_phi):
            phi = -phi_span + 2.0 * phi_span * ip / float(n_phi - 1)
            rows.append((b, phi))
    return rows


def candidate_region_map(s1, th1_hat, r_guard, Jstar, eta=0.15,
                         n_b=45, n_phi=91, phi_span=80.0):
    """Return a list of (b, phi, J) with the feasibility flag, for plotting."""
    gset = sector_points(s1, th1_hat)
    out = []
    for ib in range(n_b):
        b = 100.0 + 1600.0 * ib / float(n_b - 1)
        for ip in range(n_phi):
            phi = -phi_span + 2.0 * phi_span * ip / float(n_phi - 1)
            loc = (b * math.cos(math.radians(phi)), b * math.sin(math.radians(phi)))
            s2 = local_to_world(loc, s1, th1_hat)
            if not guard_ok(s2, gset, r_guard):
                out.append((b, phi, float("nan"), 0))
                continue
            J, _ = worst_diameter(s1, s2, th1_hat, gset)
            out.append((b, phi, J, 1 if J <= (1.0 + eta) * Jstar else 0))
    return out


# ---------------------------------------------------------------------------
# 4. Monte-Carlo verification
# ---------------------------------------------------------------------------
def monte_carlo_check(sol, s1, th1_hat, n=4000, seed=2026):
    """
    Draw the true source uniformly in the feasible sector and the two reading
    errors uniformly in [-eps, eps]; build the real two-station region and
    record its diameter.  The prescribed point must never exceed J*.
    """
    rnd = random.Random(seed)
    r_hi = max(r for (r, _, _) in sol["gset"])
    s2 = sol["S2"]
    Ds = []
    violations = 0
    for _ in range(n):
        r = R_NEAR + 1.0 + (r_hi - R_NEAR - 1.0) * rnd.random()
        a_true = th1_hat + rnd.uniform(-EPS, EPS)
        G = (s1[0] + r * math.cos(math.radians(a_true)), s1[1] + r * math.sin(math.radians(a_true)))
        th2_hat = g.bearing(s2[0], s2[1], G[0], G[1]) + rnd.uniform(-EPS, EPS)
        res = g.region_from_bearings([s1, s2], [th1_hat, th2_hat], EPS)
        if res["empty"] or not res["bounded"]:
            D = float("inf")
        else:
            D = res["diameter"]
        if D > sol["J"] + 1e-6:
            violations += 1
        Ds.append(D)
    Ds.sort()
    return {"n": n, "max": Ds[-1], "p99": Ds[int(0.99 * n)], "median": Ds[n // 2],
            "mean": sum(Ds) / n, "violations_of_Jstar": violations,
            "Jstar": sol["J"]}


# ---------------------------------------------------------------------------
# 5. baseline comparison
# ---------------------------------------------------------------------------
def baseline_compare(s1, th1_hat, r_guard=R_MIN, n=3000, seed=99):
    """
    Compare the proposed second point with four alternatives under the same
    random source/error draws:
      A proposed  : the minimax point of this section
      B perp_800  : 800 m perpendicular to the bearing (a common intuition)
      C along     : 800 m further along the bearing
      D random    : a uniformly random point of the guard-feasible set
      E oracle    : the point at the true source position (upper bound)
    Metric: mean and 95th percentile of the realised region diameter.
    """
    sol = solve_second_point(s1, th1_hat, r_guard=r_guard)
    gset = sol["gset"]
    rnd = random.Random(seed)
    draws = []
    r_hi = max(r for (r, _, _) in gset)
    for _ in range(n):
        r = R_NEAR + 1.0 + (r_hi - R_NEAR - 1.0) * rnd.random()
        a_true = th1_hat + rnd.uniform(-EPS, EPS)
        G = (s1[0] + r * math.cos(math.radians(a_true)),
             s1[1] + r * math.sin(math.radians(a_true)))
        e1 = rnd.uniform(-EPS, EPS)
        e2 = rnd.uniform(-EPS, EPS)
        draws.append((G, e1, e2))

    def eval_point(get_s2):
        vals = []
        for (G, e1, e2) in draws:
            s2 = get_s2(G)
            if s2 is None:
                vals.append(float("inf"))
                continue
            th1_hat_used = th1_hat
            th2_hat = g.bearing(s2[0], s2[1], G[0], G[1]) + e2
            res = g.region_from_bearings([s1, s2], [th1_hat_used, th2_hat], EPS)
            if res["empty"] or not res["bounded"]:
                vals.append(float("inf"))
            else:
                vals.append(res["diameter"])
        vals.sort()
        fin = [v for v in vals if math.isfinite(v)]
        return {"mean": sum(fin) / max(len(fin), 1),
                "p95": vals[int(0.95 * len(vals)) - 1] if vals else float("inf"),
                "max": vals[-1], "inf_rate": 1.0 - len(fin) / float(len(vals))}

    def pt(b, phi):
        loc = (b * math.cos(math.radians(phi)), b * math.sin(math.radians(phi)))
        return local_to_world(loc, s1, th1_hat)

    out = {}
    out["A_proposed"] = eval_point(lambda G: sol["S2"])
    out["B_perp_800"] = eval_point(lambda G: pt(800.0, 90.0))
    out["C_along_800"] = eval_point(lambda G: pt(800.0, 0.0))
    out["D_random"] = eval_point(
        lambda G: (random.Random(hash(G) & 0xffff).choice(
            [p for (_, _, p) in gset]) if gset else None))
    out["E_oracle"] = eval_point(lambda G: G)
    out["_solution"] = {"b": sol["b"], "phi": sol["phi"], "J": sol["J"],
                        "S2": sol["S2"]}
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    s1 = (-420.0, 260.0)
    th1_hat = 63.0
    summary = {"s1": s1, "th1_hat": th1_hat}

    print("=== 1) optimal second point, guaranteed detection (r_guard=1000 m) ===")
    sol = solve_second_point(s1, th1_hat, r_guard=R_MIN)
    print("  b*=%8.2f m   phi*=%+7.2f deg   J*=%9.3f m" % (sol["b"], sol["phi"], sol["J"]))
    print("  worst case uses source at r=%8.2f m, error sign %+d"
          % (sol["info"]["r"], int(sol["info"]["sign2"])))
    summary["solution_guard1000"] = {"b": sol["b"], "phi": sol["phi"], "J": sol["J"],
                                     "S2": sol["S2"],
                                     "worst_r": sol["info"]["r"],
                                     "guard_margin": sol["guard_margin"]}
    mc = monte_carlo_check(sol, s1, th1_hat)
    print("  Monte-Carlo: median %.2f m, p99 %.2f m, max %.2f m, violations of J*: %d/%d"
          % (mc["median"], mc["p99"], mc["max"], mc["violations_of_Jstar"], mc["n"]))
    summary["monte_carlo_guard1000"] = mc

    print("\n=== 2) sensitivity of the optimum to the assumed worst-case radius ===")
    rows = study_guard_tradeoff(s1, th1_hat)
    with open(os.path.join(OUT, "q2_guard_tradeoff.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    summary["guard_tradeoff"] = rows

    print("\n=== 3) candidate region (eta sub-level set) ===")
    cmap = candidate_region_map(s1, th1_hat, R_MIN, sol["J"], eta=0.15)
    with open(os.path.join(OUT, "q2_candidate_region.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["b_m", "phi_deg", "J_m", "in_region_eta15"])
        for (b, phi, J, ok) in cmap:
            w.writerow(["%.3f" % b, "%.3f" % phi,
                        "" if not math.isfinite(J) else "%.4f" % J, ok])
    ok_pts = [(b, phi) for (b, phi, J, ok) in cmap if ok]
    if ok_pts:
        print("  candidate region spans b in [%.0f, %.0f] m, phi in [%.1f, %.1f] deg"
              % (min(p[0] for p in ok_pts), max(p[0] for p in ok_pts),
                 min(p[1] for p in ok_pts), max(p[1] for p in ok_pts)))
        summary["candidate_region_bounds"] = {
            "b_min": min(p[0] for p in ok_pts), "b_max": max(p[0] for p in ok_pts),
            "phi_min": min(p[1] for p in ok_pts), "phi_max": max(p[1] for p in ok_pts)}

    print("\n=== 4) baseline comparison ===")
    bl = baseline_compare(s1, th1_hat)
    for k, v in bl.items():
        if k.startswith("_"):
            continue
        print("  %-12s mean=%9.3f  p95=%9.3f  max=%9.3f  inf_rate=%.3f"
              % (k, v["mean"], v["p95"], v["max"], v["inf_rate"]))
    summary["baselines"] = {k: v for k, v in bl.items() if not k.startswith("_")}
    summary["baseline_solution"] = bl["_solution"]

    with open(os.path.join(OUT, "q2_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print("\nsaved:", os.path.join(OUT, "q2_summary.json"))


if __name__ == "__main__":
    main()
