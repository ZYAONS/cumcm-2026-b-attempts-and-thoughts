#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
retune_rimoff.py -- one short coordinate pass with the rim patrol switched off,
because the earlier tuning was done with it on and the optimum may have moved.
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
            directional=True, rim_patrol=False)
for k in ("survey_spacing", "probe_spacing", "locate_sigma", "clear_bonus",
          "probe_min_angle", "search_cost_bias", "max_attempts"):
    if k in TUNED:
        BASE[k] = TUNED[k]

GRID = {
    "survey_spacing": [1100.0, 1300.0, 1500.0, 1700.0],
    "search_cost_bias": [0.0, 30.0, 90.0, 200.0],
    "probe_spacing": [450.0, 650.0, 900.0],
    "clear_bonus": [0.0, 200.0, 450.0],
    "probe_min_angle": [22.0, 35.0, 50.0],
    "locate_sigma": [150.0, 220.0, 350.0],
}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 16
SEEDS = list(range(30000, 30000 + N))


def ev(params):
    rs, ts, tr = [], [], []
    for sd in SEEDS:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        s, _ = rc.run_case(srcs, params=params, seed=sd)
        rs.append(s["clear_ratio"])
        ts.append(s["mean_time"])
        tr.append(s["travel_m"])
    return {"ratio": sum(rs) / N, "min": min(rs), "time": sum(ts) / N,
            "travel": sum(tr) / N}


def better(a, b):
    if b is None:
        return True
    if a["ratio"] > b["ratio"] + 1e-9:
        return True
    if a["ratio"] < b["ratio"] - 1e-9:
        return False
    return a["time"] < b["time"] - 1e-9


if __name__ == "__main__":
    t0 = time.time()
    best_p, best_s = dict(BASE), ev(BASE)
    print("baseline ratio=%.4f min=%.4f time=%.1f travel=%.0f"
          % (best_s["ratio"], best_s["min"], best_s["time"], best_s["travel"]),
          flush=True)
    for name, vals in GRID.items():
        for v in vals:
            if v == best_p.get(name):
                continue
            sc = ev(dict(best_p, **{name: v}))
            flag = ""
            if better(sc, best_s):
                best_s, best_p = sc, dict(best_p, **{name: v})
                flag = "  <== best"
            print("%-18s %-8s ratio=%.4f min=%.4f time=%7.1f%s"
                  % (name, v, sc["ratio"], sc["min"], sc["time"], flag), flush=True)
    print("FINAL ratio=%.4f min=%.4f time=%.1f travel=%.0f  (%.0f s)"
          % (best_s["ratio"], best_s["min"], best_s["time"], best_s["travel"],
             time.time() - t0), flush=True)
    print("PARAMS", json.dumps({k: best_p[k] for k in GRID}, sort_keys=True))
    with open(os.path.join(OUT, "optimize_q4_rimoff.json"), "w",
              encoding="utf-8") as f:
        json.dump({"score": best_s, "params": best_p}, f, ensure_ascii=False,
                  indent=1)
