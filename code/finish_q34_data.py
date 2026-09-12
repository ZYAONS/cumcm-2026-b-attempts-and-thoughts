#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
finish_q34_data.py -- complete the pieces that the interrupted run left over.

The full make_data run takes about ten minutes and the background harness kills a
job at that point, so the remaining pieces are done here in two short stages:

  stage 1 : the problem 4 sensitivity sweep (12 cases x 8 variants)
  stage 2 : the aggregate file and the greedy-policy comparison

usage: python finish_q34_data.py [1|2|all]
"""
import csv
import io
import json
import os
import random
import statistics
import sys
import time

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))

P3 = {"survey_mode": "ring", "ring_radius": 1250.0, "survey_spacing": 1000.0,
      "probe_spacing": 450.0, "locate_sigma": 220.0, "clear_bonus": 450.0,
      "probe_min_angle": 35.0, "search_cost_bias": 60.0, "term_cap": 420.0,
      "endgame_radius": 90.0, "max_attempts": 6}
P4 = {"survey_mode": "lattice", "survey_spacing": 1100.0, "directional": True,
      "outer_ring_gap": 0.0, "probe_spacing": 650.0, "locate_sigma": 220.0,
      "clear_bonus": 0.0, "probe_min_angle": 22.0, "search_cost_bias": 0.0,
      "term_cap": 420.0, "endgame_radius": 90.0, "max_attempts": 6}

VARIANTS = [
    ("nominal", {}),
    ("R_min=950", {"sim_r_lo": 950.0}),
    ("R_min=1050", {"sim_r_lo": 1050.0}),
    ("R_max=1400", {"sim_r_hi": 1400.0}),
    ("bearing_err=0.8deg", {"sim_eps": 0.8}),
    ("bearing_err=1.0deg", {"sim_eps": 1.0}),
    ("n_sources=10", {"n_sources": 10}),
    ("n_sources=16", {"n_sources": 16}),
]


def stage1():
    params = dict(rc.DEFAULT_PARAMS)
    params.update(P4)
    rows = []
    for name, kv in VARIANTS:
        rr, tt = [], []
        for k in range(12):
            rng = random.Random(4100 + k + (abs(hash(name)) % 1000))
            lo = kv.get("sim_r_lo", sim.R_EFF_LO)
            hi = kv.get("sim_r_hi", sim.R_EFF_HI)
            srcs = sim.make_case(rng, n_sources=kv.get("n_sources"),
                                 kind_mix=0.5, r_eff_lo=lo, r_eff_hi=hi)
            old = sim.BEARING_ERROR
            if "sim_eps" in kv:
                sim.BEARING_ERROR = kv["sim_eps"]
            st, _ = rc.run_case(srcs, params=params, seed=k)
            sim.BEARING_ERROR = old
            rr.append(st["clear_ratio"])
            tt.append(st["mean_time"] if st["n_cleared"] else 9000.0)
        rows.append([name, "%.3f" % statistics.mean(rr),
                     "%.1f" % statistics.mean(tt)])
        print("   %-20s ratio=%s  mean=%s s" % (name, rows[-1][1], rows[-1][2]),
              flush=True)
    with io.open(os.path.join(DATA, "q4_sensitivity.csv"), "w", newline="",
                 encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["variant", "clear_ratio", "mean_time_s"])
        for r in rows:
            w.writerow(r)
    print("  wrote q4_sensitivity.csv (%d rows)" % len(rows))


def stage2():
    def jl(n):
        with io.open(os.path.join(DATA, n), encoding="utf-8") as f:
            return json.load(f)
    agg = {k: jl("%s_agg.json" % k) for k in ("q3", "q4", "q4_alldir", "q4_omni")}
    with io.open(os.path.join(DATA, "q34_agg.json"), "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=1)
    print("  wrote q34_agg.json")

    p3 = dict(rc.DEFAULT_PARAMS)
    p3.update(P3)
    pg = dict(rc.DEFAULT_PARAMS)
    pg.update({"policy": "greedy", "survey_spacing": 1250.0})

    def run(params, n, mix, seed0, tag):
        rs, ts, tr = [], [], []
        for i in range(n):
            srcs = sim.make_case(random.Random(seed0 + i), kind_mix=mix)
            st, _ = rc.run_case(srcs, params=params, seed=seed0 + i)
            rs.append(st["clear_ratio"])
            ts.append(st["mean_time"] if st["n_cleared"] else float("inf"))
            tr.append(st["travel_m"])
        a = {"n_cases": n, "mean_ratio": sum(rs) / n,
             "mean_time": sum(ts) / n, "mean_travel": sum(tr) / n}
        print("  %-14s ratio=%.4f mean=%7.1f travel=%7.0f"
              % (tag, a["mean_ratio"], a["mean_time"], a["mean_travel"]), flush=True)
        return a

    out = {"planned_q3": agg["q3"],
           "greedy_q3": run(pg, 30, 0.0, 20000, "greedy_q3"),
           "planned_q4": agg["q4"]}
    pg4 = dict(pg, directional=True)
    out["greedy_q4"] = run(pg4, 30, 0.5, 30000, "greedy_q4")
    with io.open(os.path.join(DATA, "policy_compare.json"), "w",
                 encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("  wrote policy_compare.json")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    t0 = time.time()
    if which in ("all", "1"):
        stage1()
    if which in ("all", "2"):
        stage2()
    print("total %.0f s" % (time.time() - t0))
