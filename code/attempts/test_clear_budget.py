#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_clear_budget.py -- the loss is not a search problem.

For the failing case (seed 30017) the diagnosis shows the missed source was
LOCATED (estimate 20.6 m from the truth) but the clear-attempt budget
(max_attempts = 6) was exhausted before the target was neutralised.  The same
pattern shows up whenever a near miss keeps the estimate just outside the 20 m
clear radius while sigma is small.

This script sweeps the three knobs that govern that budget.
"""
import json
import math
import os
import random
import sys
import time

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))
TUNED = {}
p = os.path.join(OUT, "optimize_q4.json")
if os.path.exists(p):
    with open(p, encoding="utf-8") as f:
        TUNED = json.load(f)["params"]
BASE = dict(rc.DEFAULT_PARAMS, survey_mode="lattice", survey_spacing=1100.0,
            directional=True)
for k in ("survey_spacing", "probe_spacing", "locate_sigma", "clear_bonus",
          "probe_min_angle", "search_cost_bias", "max_attempts"):
    if k in TUNED:
        BASE[k] = TUNED[k]

VARIANTS = [
    ("current (max_attempts=6)", {}),
    ("max_attempts=10", {"max_attempts": 10}),
    ("max_attempts=16", {"max_attempts": 16}),
    ("hard cap 24", {"max_attempts": 16, "hard_attempt_cap": 24}),
    ("hard cap 40", {"max_attempts": 20, "hard_attempt_cap": 40}),
    ("progress_ratio 0.9", {"progress_ratio": 0.9}),
    ("progress_ratio 0.99", {"progress_ratio": 0.99}),
    ("endgame radius 130", {"endgame_radius": 130.0}),
    ("endgame radius 130 + cap40", {"endgame_radius": 130.0, "max_attempts": 20,
                                    "hard_attempt_cap": 40}),
]


def ev(params, seeds, mix=0.5):
    rs, ts, tr = [], [], []
    t0 = time.time()
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        s, _ = rc.run_case(srcs, params=params, seed=sd)
        rs.append(s["clear_ratio"])
        ts.append(s["mean_time"])
        tr.append(s["travel_m"])
    n = float(len(seeds))
    return {"ratio": sum(rs) / n, "min": min(rs), "time": sum(ts) / n,
            "travel": sum(tr) / n, "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("pool: %d cases, seeds %d..%d" % (n, seeds[0], seeds[-1]), flush=True)
    out = []
    for tag, ov in VARIANTS:
        r = ev(dict(BASE, **ov), seeds)
        r["tag"] = tag
        out.append(r)
        print("%-28s ratio=%.4f min=%.4f time=%7.1f travel=%7.0f  (%.0f s)"
              % (tag, r["ratio"], r["min"], r["time"], r["travel"], r["wall"]),
              flush=True)
    with open(os.path.join(OUT, "clear_budget.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/clear_budget.json")
