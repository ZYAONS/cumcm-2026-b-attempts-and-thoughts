#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tradeoff_q4.py -- the completion/time trade-off of problem 4.

The previous numbers (ratio 0.957 at 661 s) came from a certification scan that
silently truncated its "not yet certified" list, so the robot gave up early: a
high ratio was never reached and the time looked good.  With a correct scan the
ratio rises but so does the search cost, so the honest thing to report is the
whole trade-off curve rather than one operating point.

usage: python tradeoff_q4.py [n_cases]
"""
import json
import os
import random
import sys
import time

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
SEEDS = list(range(62000, 62000 + N))

TUNED = {}
p = os.path.join(OUT, "optimize_q4.json")
if os.path.exists(p):
    with open(p, encoding="utf-8") as f:
        TUNED = json.load(f)["params"]

BASE = dict(rc.DEFAULT_PARAMS, survey_mode="lattice", survey_spacing=1000.0,
            directional=True)
for k in ("survey_spacing", "probe_spacing", "locate_sigma", "clear_bonus",
          "probe_min_angle", "search_cost_bias", "max_attempts", "rim_step",
          "max_rim_patrols"):
    if k in TUNED:
        BASE[k] = TUNED[k]

VARIANTS = [
    ("full certification (tuned)", {}),
    ("no rim patrol", {"rim_patrol": False}),
    ("rim trips <= 4", {"max_rim_patrols": 4}),
    ("rim trips = 0", {"max_rim_patrols": 0}),
    ("search budget 10 stops", {"max_search_stops": 10}),
    ("search budget 4 stops", {"max_search_stops": 4}),
    ("dense lattice 850 m", {"survey_spacing": 850.0}),
    ("sparse lattice 1500 m", {"survey_spacing": 1500.0}),
]


def ev(params, tag):
    rs, ts, tr = [], [], []
    t0 = time.time()
    for sd in SEEDS:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        s, _ = rc.run_case(srcs, params=params, seed=sd)
        rs.append(s["clear_ratio"])
        ts.append(s["mean_time"])
        tr.append(s["travel_m"])
    r = {"tag": tag, "ratio": sum(rs) / N, "min": min(rs),
         "time": sum(ts) / N, "travel": sum(tr) / N, "wall": time.time() - t0}
    print("%-28s ratio=%.4f min=%.4f time=%7.1f travel=%7.0f  (%.0f s)"
          % (tag, r["ratio"], r["min"], r["time"], r["travel"], r["wall"]),
          flush=True)
    return r


if __name__ == "__main__":
    out = []
    for tag, ov in VARIANTS:
        out.append(ev(dict(BASE, **ov), tag))
    with open(os.path.join(OUT, "q4_tradeoff.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/q4_tradeoff.json")
