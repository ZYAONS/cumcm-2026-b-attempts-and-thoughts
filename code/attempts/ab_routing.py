#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ab_routing.py -- measure the two routing couplings of §10.2 item 2.

  base   : nearest neighbour + 2-opt, fixed probe interval (as reported)
  C1     : clear located sources that sit next to a search stop we already visit
  C2     : shorten the opportunistic probe interval while many channels are open
  C1+C2  : both

usage: python ab_routing.py [n_cases] [seed0] [mix]
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
    ("base (no coupling)", {"enroute_clear": False, "adaptive_probe": False}),
    ("C1 clear on the way", {"enroute_clear": True, "adaptive_probe": False}),
    ("C2 adaptive probe", {"enroute_clear": False, "adaptive_probe": True}),
    ("C1 + C2", {"enroute_clear": True, "adaptive_probe": True}),
]


def ev(params, seeds, mix):
    rs, ts, tr = [], [], []
    t0 = time.time()
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        st, _ = rc.run_case(srcs, params=params, seed=sd)
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
    n = float(len(seeds))
    return {"ratio": sum(rs) / n, "min": min(rs), "time": sum(ts) / n,
            "travel": sum(tr) / n, "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 62000
    mix = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    seeds = list(range(seed0, seed0 + n))
    print("pool: %d cases, seeds %d..%d, mix %.1f" % (n, seeds[0], seeds[-1], mix),
          flush=True)
    out = []
    for tag, ov in VARIANTS:
        r = ev(dict(BASE, **ov), seeds, mix)
        r["tag"] = tag
        out.append(r)
        print("%-22s ratio=%.4f min=%.4f time=%7.1f travel=%7.0f  (%.0f s)"
              % (tag, r["ratio"], r["min"], r["time"], r["travel"], r["wall"]),
              flush=True)
    with open(os.path.join(OUT, "ab_routing.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/ab_routing.json")
