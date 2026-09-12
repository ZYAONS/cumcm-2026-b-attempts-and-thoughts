#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
confirm_rim.py -- decide the default of rim_patrol with a proper A/B.

Evidence so far: on 20 untouched cases both settings reach ratio 1.0000, the
patrol costing 19 % more time; on the four failing drill cases the patrol changes
nothing but the time.  This script repeats the comparison on the 60 case drill
pool (the one the paper reports) so the default can be set on evidence.
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
BASE = dict(rc.DEFAULT_PARAMS, survey_mode="lattice", survey_spacing=1000.0,
            directional=True)
for k in ("survey_spacing", "probe_spacing", "locate_sigma", "clear_bonus",
          "probe_min_angle", "search_cost_bias", "max_attempts", "rim_step",
          "max_rim_patrols"):
    if k in TUNED:
        BASE[k] = TUNED[k]

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
MIX = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
SEED0 = int(sys.argv[3]) if len(sys.argv) > 3 else 30000


def ev(params, tag):
    rs, ts, tr = [], [], []
    t0 = time.time()
    for i in range(N):
        srcs = sim.make_case(random.Random(SEED0 + i), kind_mix=MIX)
        s, _ = rc.run_case(srcs, params=params, seed=SEED0 + i)
        rs.append(s["clear_ratio"])
        ts.append(s["mean_time"])
        tr.append(s["travel_m"])
    print("%-18s ratio=%.4f min=%.4f time=%7.1f travel=%7.0f  (%.0f s)"
          % (tag, sum(rs) / N, min(rs), sum(ts) / N, sum(tr) / N, time.time() - t0),
          flush=True)
    return {"ratio": sum(rs) / N, "min": min(rs), "time": sum(ts) / N,
            "travel": sum(tr) / N}


if __name__ == "__main__":
    print("pool: seeds %d..%d, directional mix %.1f, %d cases"
          % (SEED0, SEED0 + N - 1, MIX, N), flush=True)
    a = ev(dict(BASE, rim_patrol=True), "rim patrol ON")
    b = ev(dict(BASE, rim_patrol=False), "rim patrol OFF")
    print("delta: time %+.1f %%  ratio %+.4f  travel %+.1f %%"
          % (100.0 * (b["time"] / a["time"] - 1.0), b["ratio"] - a["ratio"],
             100.0 * (b["travel"] / a["travel"] - 1.0)), flush=True)
    with open(os.path.join(OUT, "confirm_rim.json"), "w", encoding="utf-8") as f:
        json.dump({"seeds": [SEED0, SEED0 + N - 1], "mix": MIX,
                   "on": a, "off": b}, f, ensure_ascii=False, indent=1)
