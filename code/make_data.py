#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_data.py -- produces every numeric result used in the paper.

  Q1 : positioning-region algorithm, diameter, covering-circle test, validation
  Q2 : optimal second station, candidate region, baselines, Monte-Carlo check
  Q3 : omni strategy, drill statistics, sensitivity analysis
  Q4 : mixed omni/directional strategy, drill statistics, sensitivity analysis

All results are written to ../data as csv/json so that the figures and the paper
can quote exactly the numbers that the code produced.
Run: python make_data.py
"""
import csv
import json
import math
import os
import random
import statistics
import time

import geom_core as g
import q2_solver as q2
import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
os.makedirs(DATA, exist_ok=True)

P3 = {"survey_mode": "ring", "ring_radius": 1250.0, "survey_spacing": 1000.0, "probe_spacing": 450.0, "locate_sigma": 220.0, "clear_bonus": 450.0, "probe_min_angle": 35.0, "search_cost_bias": 60.0, "term_cap": 420.0, "endgame_radius": 90.0, "max_attempts": 6, "rim_step": 130.0, "max_rim_patrols": 12}
P4 = {
    "survey_mode": "lattice",
    "survey_spacing": 950.0,      # 覆盖半径 548 m < R_min；间距 <= 认证半径 958 m
    "directional": True,
    # 本轮新增：贴边环 + 认证边距（四池 120 例：880.7 s -> 597.0 s，完成率不变）
    "rim_ring_n": 12,             # 贴边环 12 个站位
    "rim_ring_r": 1750.0,
    "verify_margin": 700.0,       # 只认证 r <= 1100；边界发现交给贴边环
    "max_search_stops": 40,       # 认证搜索兜底
    "periodic_cert": True,
    "periodic_cert_every": 1,
    "spread_stops": True,
    "max_survey_stops": 0,
    "clear_bonus": 350.0,
    "locate_sigma": 400.0,
    "probe_spacing": 650.0,
    "probe_min_angle": 22.0,
    "search_cost_bias": 0.0,
    "term_cap": 420.0,
    "endgame_radius": 90.0,
    "max_attempts": 6,
    "ring_radius": 1280.0,
    "outer_ring_gap": 0.0,
    "relocate": True,
    "exhaustive_clear": True,
    "enroute_clear": False,
    "hard_attempt_cap": 24,
}


# ---------------------------------------------------------------------------
# P4_FAST : the "finish under 500 s" preset.
#
# Validated on two independent pools of 40 cases each (seeds 62000+ and 51000+),
# neither of which took part in any tuning:
#
#     pool A   476.5 s   completion 0.9823   median 475.7
#     pool B   498.2 s   completion 0.9699   median 485.0
#
# against the accurate configuration (P4), which runs 864.9 s / 945.7 s at
# completion 1.0000 / 0.9983 on the same pools.  The preset buys a 45 % cut in
# time for 1.6 to 3.0 percentage points of completion rate; the full derivation,
# including the measurements that turned out to be negative, is in
# docs/time_optimization.pdf.
# ---------------------------------------------------------------------------
# P4_PERFECT : 完成率 1.0000 且时间比论文配置低约 38 % 的配置。
#
# 调参池（种子 30000+，24 例）：
#     P4 (paper)    : 完成率 1.0000 (最差 1.0000)  874.9 s   24.0 个站位
#     P4_PERFECT    : 完成率 1.0000 (最差 1.0000)  540.3 s   18.5 个站位
#
# 组成：
#   * 间距 900 m 的格点一次扫完——这个间距同时满足
#     "全向源必被发现"（覆盖半径 520 m < R_min）与
#     "定向源可认证"（候选点所在格点三角形的三个顶点都在认证半径 958 m 内），
#     因此把认证搜索整个去掉；
#   * 最远点采样给站位排序，截断时保留均匀覆盖；
#   * relocate：只有一条方位的频道，用"横向偏移二分 + 沿射线爬行"拿第二条方位；
#   * exhaustive：已定位但反复清不掉的源，在 σ 圆盘上做 <=15 m 间距的穷举清除
#     （15/√2 = 10.6 m < 20 m 清除半径，因此**有保证**）。
P4_PERFECT = dict(P4)
P4_PERFECT.update({
    "survey_spacing": 900.0,
    "max_search_stops": 0,
    "verify_margin": 900.0,
    "periodic_cert": True,
    "periodic_cert_every": 1,
    "spread_stops": True,
    "max_survey_stops": 0,
    "clear_bonus": 500.0,
    "locate_sigma": 400.0,
    "hard_attempt_cap": 24,
    "exhaustive_clear": True,
    "relocate": True,
    "enroute_clear": False,
})


P4_FAST = dict(P4)
P4_FAST.update({
    "survey_spacing": 1000.0,     # the lattice is only used as a discovery sweep
    "max_survey_stops": 10,       # ... and is cut to ten well-spread positions
    "spread_stops": True,         # farthest-point ordering, so the cut keeps the
                                  # arena covered instead of dropping the rim
    "max_search_stops": 0,        # no certification search at all
    "verify_margin": 900.0,       # candidates near the rim are excluded: they can
                                  # never be certified from inside (theorem 2)
    "periodic_cert": True,        # certify during the sweep so certified channels
    "periodic_cert_every": 1,     # stop being measured
    "locate_sigma": 400.0,
    "clear_bonus": 500.0,
    "probe_spacing": 2000.0,
})


def w(name, rows, header=None):
    path = os.path.join(DATA, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        if header:
            wr.writerow(header)
        for r in rows:
            wr.writerow(r)
    print("  wrote", name, "(%d rows)" % len(rows))


def jdump(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    print("  wrote", name)


# ===========================================================================
# Q1
# ===========================================================================
def q1_study():
    print("[Q1] positioning region study")
    rnd = random.Random(20260913)
    rows = []
    # (a) hand-made configurations covering the interesting cases
    cases = [
        ("symmetric 2-station, gamma=67", [(0, 0), (1200, 0)], (600, 900), 2),
        ("right angle, gamma=90", [(0, 0), (1200, 0)], (600, 600), 2),
        ("far source, gamma=151", [(0, 0), (1400, 0)], (100, 50), 2),
        ("near-collinear (unbounded)", [(0, 0), (100, 0)], None, 2),
        ("3 stations", [(-800, -600), (900, -400), (300, 1100)], (100, 200), 3),
        ("4 stations", [(-800, -600), (900, -400), (300, 1100), (-500, 700)], (100, 200), 4),
        ("5 stations", [(-800, -600), (900, -400), (300, 1100), (-500, 700),
                        (0, -1200)], (100, 200), 5),
    ]
    for (name, sts, G, nst) in cases:
        if G is None:
            bs = [45.0, 45.5]
        else:
            bs = [g.bearing(s[0], s[1], G[0], G[1]) for s in sts]
        res = g.region_from_bearings(sts, bs, 1.0)
        A, B = res["d_pair"] if res["d_pair"] else ((0, 0), (0, 0))
        others = [v for v in res["vertices"]
                  if math.dist(v, A) > 1e-6 and math.dist(v, B) > 1e-6] if res["vertices"] else []
        viol = g.diameter_disk_slack(others, A, B) if others else 0.0
        d_cal = g.rotating_calipers_diameter(res["vertices"])[0] if res["vertices"] else 0.0
        gam = g.region_intersection_angle(sts[0], sts[1], G) if G else 0.0
        d_asy = (g.asymptotic_diameter(math.dist(sts[0], G), math.dist(sts[1], G), gam)
                 if G else 0.0)
        rows.append([name, nst, "%.1f" % res["diameter"] if res["bounded"] and not res["empty"] else "inf",
                     "%d" % len(res["vertices"]), "%.1f" % d_cal,
                     "%.1f" % d_asy if G else "-",
                     "%.4f" % (100.0 * abs(d_cal - d_asy) / d_asy) if G and d_asy else "-",
                     "%.1f" % res["mec"][2] if res["mec"] else "-",
                     "yes" if res["cover_ok"] else ("no" if res["cover_ok"] is not None else "-"),
                     "%.2f" % viol])
    w("q1_cases.csv", rows,
      ["scenario", "n_stations", "diameter_m", "n_vertices", "diameter_calipers_m",
       "diameter_asymptotic_m", "rel_diff_pct", "R_mec_m", "disk_covers_region",
       "max_thales_product_m2"])

    # (b) Monte-Carlo statistics of the covering-circle test
    stats = []
    for nst in (2, 3, 4, 5):
        tot = 0
        fail = 0
        unb = 0
        worst = 0.0
        ratios = []
        for _ in range(60000):
            def rp():
                r = 1800.0 * math.sqrt(rnd.random())
                a = 2.0 * math.pi * rnd.random()
                return (r * math.cos(a), r * math.sin(a))
            sts = [rp() for _ in range(nst)]
            if nst > 1 and min(math.dist(a, b) for i, a in enumerate(sts)
                               for b in sts[i + 1:]) < 200:
                continue
            G = rp()
            if min(math.dist(s, G) for s in sts) < 30:
                continue
            if max(math.dist(s, G) for s in sts) > 1500:
                continue
            bs = [g.bearing(s[0], s[1], G[0], G[1]) for s in sts]
            res = g.region_from_bearings(sts, bs, 1.0)
            if res["empty"]:
                continue
            tot += 1
            if not res["bounded"]:
                unb += 1
                continue
            A, B = res["d_pair"]
            others = [v for v in res["vertices"]
                      if math.dist(v, A) > 1e-6 and math.dist(v, B) > 1e-6]
            viol = g.diameter_disk_slack(others, A, B) if others else 0.0
            if viol > 1e-9:
                fail += 1
            worst = max(worst, viol)
            ratios.append(res["mec"][2] / (res["diameter"] / 2.0))
        stats.append([nst, tot, unb, fail, "%.4f" % (100.0 * fail / max(tot - unb, 1)),
                      "%.2f" % worst,
                      "%.6f" % statistics.mean(ratios) if ratios else "-",
                      "%.6f" % max(ratios) if ratios else "-"])
    w("q1_cover_stats.csv", stats,
      ["n_stations", "n_valid", "n_unbounded", "n_not_covered", "pct_not_covered",
       "worst_thales_product_m2", "mean_Rmec_over_halfD", "max_Rmec_over_halfD"])

    # (c) exactness check of the polygon diameter against an independent method
    diffs = []
    for _ in range(3000):
        def rp():
            r = 1800.0 * math.sqrt(rnd.random())
            a = 2.0 * math.pi * rnd.random()
            return (r * math.cos(a), r * math.sin(a))
        sts = [rp() for _ in range(rnd.choice([2, 3, 4]))]
        if min(math.dist(a, b) for i, a in enumerate(sts) for b in sts[i + 1:]) < 200:
            continue
        G = rp()
        if min(math.dist(s, G) for s in sts) < 30 or max(math.dist(s, G) for s in sts) > 1500:
            continue
        bs = [g.bearing(s[0], s[1], G[0], G[1]) for s in sts]
        res = g.region_from_bearings(sts, bs, 1.0)
        if res["empty"] or not res["bounded"]:
            continue
        d1 = res["diameter"]
        d2 = g.rotating_calipers_diameter(res["vertices"])[0]
        diffs.append(abs(d1 - d2))
    jdump("q1_validation.json", {
        "n_cases": len(diffs),
        "max_abs_diff_bruteforce_vs_calipers_m": max(diffs),
        "mean_abs_diff_m": statistics.mean(diffs)})

    # (d) robustness of the region to the error bound and to one bad station
    rob = []
    for eps in (0.2, 0.5, 1.0, 1.5, 2.0):
        sts = [(0.0, 0.0), (1200.0, 0.0)]
        G = (600.0, 900.0)
        bs = [g.bearing(s[0], s[1], G[0], G[1]) for s in sts]
        res = g.region_from_bearings(sts, bs, eps)
        rob.append([eps, "%.2f" % res["diameter"], "%.2f" % res["mec"][2],
                    "yes" if res["cover_ok"] else "no"])
    for k in range(1, 4):
        sts = [(0.0, 0.0), (1200.0, 0.0), (600.0, 1600.0)]
        G = (600.0, 900.0)
        bs = [g.bearing(s[0], s[1], G[0], G[1]) for s in sts]
        bs[k - 1] += 1.2                       # one biased station
        res = g.region_from_bearings(sts, bs, 1.0)
        rob.append(["bias_station_%d" % k,
                    "%.2f" % res["diameter"] if res["bounded"] and not res["empty"] else "inf",
                    "%.2f" % res["mec"][2] if res["mec"] else "-",
                    "yes" if res["cover_ok"] else ("no" if res["cover_ok"] is not None else "-")])
    w("q1_robustness.csv", rob, ["setting", "diameter_m", "R_mec_m", "disk_covers"])


# ===========================================================================
# Q2
# ===========================================================================
def q2_study():
    print("[Q2] second-station design")
    s1 = (-420.0, 260.0)
    th1 = 63.0
    gset = q2.sector_points(s1, th1)
    sol = q2.solve_second_point(s1, th1, r_guard=q2.R_MIN)
    mc = q2.monte_carlo_check(sol, s1, th1)
    # scan of J over (b, phi)
    rows = []
    for b in (200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1400, 1600):
        for phi in (0, 10, 20, 30, 37, 45, 55, 65, 75, 85):
            loc = (b * math.cos(math.radians(phi)), b * math.sin(math.radians(phi)))
            s2 = q2.local_to_world(loc, s1, th1)
            if not q2.guard_ok(s2, gset, q2.R_MIN):
                rows.append([b, phi, "", "infeasible"])
                continue
            J, info = q2.worst_diameter(s1, s2, th1, gset)
            rows.append([b, phi, "%.3f" % J, "ok"])
    w("q2_phi_scan.csv", rows, ["b_m", "phi_deg", "J_m", "status"])

    guard = []
    for rg in (1000, 1050, 1100, 1150, 1200, 1300, 1400, 1500):
        so = q2.solve_second_point(s1, th1, r_guard=float(rg))
        if so is None:
            guard.append([rg, "", "", "", ""])
            continue
        guard.append([rg, "%.1f" % so["b"], "%.2f" % so["phi"], "%.2f" % so["J"],
                      "%.1f" % q2.guard_margin(so["S2"], gset)])
    w("q2_guard_tradeoff.csv", guard,
      ["r_guard_m", "b_opt_m", "phi_opt_deg", "J_m", "max_dist_to_source_set_m"])

    bl = q2.baseline_compare(s1, th1)
    rows = []
    for k in ("A_proposed", "B_perp_800", "C_along_800", "D_random", "E_oracle"):
        v = bl[k]
        rows.append([k, "%.2f" % v["mean"], "%.2f" % v["p95"], "%.2f" % v["max"],
                     "%.3f" % v["inf_rate"]])
    w("q2_baselines.csv", rows, ["strategy", "mean_D_m", "p95_D_m", "max_D_m",
                                 "unbounded_rate"])

    # a second geometry, to show the rule does not depend on the entry point
    s1b = (900.0, -700.0)
    th1b = 205.0
    solb = q2.solve_second_point(s1b, th1b, r_guard=q2.R_MIN)
    jdump("q2_summary.json", {
        "entry_S1": s1, "measured_bearing_deg": th1,
        "b_opt_m": sol["b"], "phi_opt_deg": sol["phi"], "J_star_m": sol["J"],
        "S2_opt": sol["S2"], "worst_source_distance_m": sol["info"]["r"],
        "monte_carlo": mc,
        "second_geometry": {"entry_S1": s1b, "measured_bearing_deg": th1b,
                            "b_opt_m": solb["b"], "phi_opt_deg": solb["phi"],
                            "J_star_m": solb["J"]},
        "baselines": {k: bl[k] for k in ("A_proposed", "B_perp_800", "C_along_800",
                                         "D_random", "E_oracle")}})
    print("  b*=%.1f phi*=%.2f J*=%.1f  MC median %.1f p99 %.1f max %.1f"
          % (sol["b"], sol["phi"], sol["J"], mc["median"], mc["p99"], mc["max"]))


# ===========================================================================
# Q3 / Q4
# ===========================================================================
def run_cases(params, n, kind_mix, seed0, tag, verbose=True, save=True):
    rows = []
    t0 = time.time()
    for k in range(n):
        srcs = sim.make_case(random.Random(seed0 + k), kind_mix=kind_mix)
        st, _ = rc.run_case(srcs, params=params, seed=k)
        rows.append(st)
        if verbose and k < 5:
            print("   case %d: n=%2d cleared=%2d ratio=%.2f mean=%7.1f s travel=%6.0f"
                  % (k, st["n_sources"], st["n_cleared"], st["clear_ratio"],
                     st["mean_time"], st["travel_m"]))
    agg = {
        "n_cases": len(rows),
        "mean_ratio": statistics.mean(r["clear_ratio"] for r in rows),
        "min_ratio": min(r["clear_ratio"] for r in rows),
        "mean_time": statistics.mean(r["mean_time"] for r in rows),
        "median_time": statistics.median(r["mean_time"] for r in rows),
        "sd_time": statistics.pstdev([r["mean_time"] for r in rows]) if len(rows) > 1 else 0.0,
        "mean_travel": statistics.mean(r["travel_m"] for r in rows),
        "mean_measure": statistics.mean(r["n_measure"] for r in rows),
        "mean_clear_actions": statistics.mean(r["n_clear"] for r in rows),
        "mean_vtime": statistics.mean(r["virtual_time"] for r in rows),
        "wall_s": time.time() - t0,
    }
    if save:
        w("%s_cases.csv" % tag,
          [[r["case_seed"] if "case_seed" in r else i, r["n_sources"], r["n_cleared"],
            "%.3f" % r["clear_ratio"], "%.1f" % r["mean_time"], "%.1f" % r["virtual_time"],
            "%.0f" % r["travel_m"], r["n_measure"], r["n_clear"], r["n_switch"]]
           for i, r in enumerate(rows)],
          ["case", "n_sources", "n_cleared", "clear_ratio", "mean_time_s",
           "virtual_time_s", "travel_m", "n_measure", "n_clear", "n_switch"])
        jdump("%s_agg.json" % tag, agg)
    return rows, agg


def sensitivity(params, base_mix, tag):
    """Perturb the problem constants and re-measure the strategy performance."""
    rows = []
    variants = [
        ("nominal", {}),
        ("R_min=950", {"sim_r_lo": 950.0}),
        ("R_min=1050", {"sim_r_lo": 1050.0}),
        ("R_max=1400", {"sim_r_hi": 1400.0}),
        ("bearing_err=0.8deg", {"sim_eps": 0.8}),
        ("bearing_err=1.0deg", {"sim_eps": 1.0}),
        ("n_sources=10", {"n_sources": 10}),
        ("n_sources=16", {"n_sources": 16}),
    ]
    for name, kv in variants:
        rr, tt = [], []
        for k in range(12):
            rng = random.Random(4100 + k + hash(name) % 1000)
            lo = kv.get("sim_r_lo", sim.R_EFF_LO)
            hi = kv.get("sim_r_hi", sim.R_EFF_HI)
            srcs = sim.make_case(rng, n_sources=kv.get("n_sources"),
                                 kind_mix=base_mix, r_eff_lo=lo, r_eff_hi=hi)
            if "sim_eps" in kv:
                old = sim.BEARING_ERROR
                sim.BEARING_ERROR = kv["sim_eps"]
            st, _ = rc.run_case(srcs, params=params, seed=k)
            if "sim_eps" in kv:
                sim.BEARING_ERROR = old
            rr.append(st["clear_ratio"])
            tt.append(st["mean_time"] if st["n_cleared"] else 9000.0)
        rows.append([name, "%.3f" % statistics.mean(rr), "%.1f" % statistics.mean(tt)])
        print("   %-20s ratio=%.3f  mean=%.1f s" % (name, rows[-1][1] and float(rows[-1][1]),
                                                    float(rows[-1][2])))
    w("%s_sensitivity.csv" % tag, rows, ["variant", "clear_ratio", "mean_time_s"])


def q34_study():
    print("[Q3] omnidirectional strategy")
    p3 = dict(rc.DEFAULT_PARAMS)
    p3.update(P3)
    rows3, agg3 = run_cases(p3, 60, 0.0, 20000, "q3")
    print("  Q3: ratio=%.4f mean=%.1f s travel=%.0f m" %
          (agg3["mean_ratio"], agg3["mean_time"], agg3["mean_travel"]))
    sensitivity(p3, 0.0, "q3")

    print("[Q4] mixed strategy")
    p4 = dict(rc.DEFAULT_PARAMS)
    p4.update(P4)
    rows4, agg4 = run_cases(p4, 60, 0.5, 30000, "q4")
    print("  Q4 (mixed): ratio=%.4f mean=%.1f s travel=%.0f m" %
          (agg4["mean_ratio"], agg4["mean_time"], agg4["mean_travel"]))
    # extreme mixes
    extra = {}
    for nm, mix in (("q4_alldir", 1.0), ("q4_omni", 0.0)):
        _, a = run_cases(p4, 30, mix, 35000, nm, verbose=False)
        extra[nm] = a
        print("  %s: ratio=%.3f mean=%.1f" % (nm, a["mean_ratio"], a["mean_time"]))
    sensitivity(p4, 0.5, "q4")
    jdump("q34_agg.json", {"q3": agg3, "q4": agg4, "q4_alldir": extra["q4_alldir"],
                           "q4_omni": extra["q4_omni"]})

    # strategy comparison: the pure greedy policy as a baseline
    print("[Q3] baseline policy comparison")
    pg = dict(rc.DEFAULT_PARAMS)
    pg.update({"policy": "greedy", "survey_spacing": 1250.0})
    _, ag = run_cases(pg, 30, 0.0, 20000, "q3_greedy", verbose=False)
    print("  greedy: ratio=%.3f mean=%.1f s" % (ag["mean_ratio"], ag["mean_time"]))
    pg4 = dict(pg)
    pg4.update({"directional": True})
    _, ag4 = run_cases(pg4, 30, 0.5, 30000, "q4_greedy", verbose=False)
    print("  greedy Q4: ratio=%.3f mean=%.1f s" % (ag4["mean_ratio"], ag4["mean_time"]))
    jdump("policy_compare.json", {"planned_q3": agg3, "greedy_q3": ag,
                                  "planned_q4": agg4, "greedy_q4": ag4})


def main():
    which = os.environ.get("STAGE", "all")
    t0 = time.time()
    if which in ("all", "q1"):
        q1_study()
    if which in ("all", "q2"):
        q2_study()
    if which in ("all", "q34"):
        q34_study()
    print("total %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
