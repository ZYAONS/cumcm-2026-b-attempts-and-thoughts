#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
evaluate.py -- Monte-Carlo evaluation of the robot strategy.

usage:  python evaluate.py [n_cases] [kind_mix] [seed]
"""
import json
import math
import os
import random
import statistics
import sys
import time

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))


def evaluate(params=None, n_cases=30, seed0=1000, kind_mix=0.0, n_sources=None,
             verbose=True, t_limit=None):
    rows = []
    t0 = time.time()
    for k in range(n_cases):
        rng = random.Random(seed0 + k)
        srcs = sim.make_case(rng, n_sources=n_sources, kind_mix=kind_mix)
        st, brain = rc.run_case(srcs, params=params, seed=seed0 + k)
        st["case_seed"] = seed0 + k
        st["n_dir"] = sum(1 for s in srcs if s.kind == "directional")
        rows.append(st)
        if verbose:
            print("  case %3d: n=%2d dir=%2d cleared=%2d ratio=%.2f mean=%7.1f s "
                  "vtime=%8.1f travel=%7.0f meas=%4d"
                  % (k, st["n_sources"], st["n_dir"], st["n_cleared"], st["clear_ratio"],
                     st["mean_time"], st["virtual_time"], st["travel_m"], st["n_measure"]))
        if t_limit and time.time() - t0 > t_limit:
            break
    ok = [r for r in rows if r["clear_ratio"] > 0.999]
    agg = {
        "n_cases": len(rows),
        "full_clear_cases": len(ok),
        "mean_ratio": statistics.mean(r["clear_ratio"] for r in rows),
        "min_ratio": min(r["clear_ratio"] for r in rows),
        "mean_time_all": statistics.mean(r["mean_time"] for r in rows),
        "median_time": statistics.median(r["mean_time"] for r in rows),
        "mean_vtime": statistics.mean(r["virtual_time"] for r in rows),
        "mean_travel": statistics.mean(r["travel_m"] for r in rows),
        "mean_measure": statistics.mean(r["n_measure"] for r in rows),
        "wall_s": time.time() - t0,
    }
    if ok:
        agg["mean_time_fullclear"] = statistics.mean(r["mean_time"] for r in ok)
        agg["sd_time_fullclear"] = (statistics.pstdev([r["mean_time"] for r in ok])
                                    if len(ok) > 1 else 0.0)
    return rows, agg


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    mix = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    sd = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    rows, agg = evaluate(n_cases=n, kind_mix=mix, seed0=sd)
    print(json.dumps(agg, indent=1, ensure_ascii=False))
    with open(os.path.join(OUT, "eval_p3_baseline.json"), "w", encoding="utf-8") as f:
        json.dump({"agg": agg, "rows": rows}, f, ensure_ascii=False, indent=1)
