#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
optimize_q34.py -- coordinate descent on the strategy parameters of problem 3
and problem 4.

  python optimize_q34.py q3 [n_cases] [passes]
  python optimize_q34.py q4 [n_cases] [passes]

Case pool
---------
Cases are regenerated from their seed for EVERY evaluation.  This matters:
`sim.Arena` keeps the Source objects it is handed and marks them cleared during
the run, so a pool built once and reused scores every candidate after the first
one on already-neutralised sources (ratio 1.0, absurdly small times).  An earlier
version of this script had exactly that defect and produced a fake 44 % gain;
the guard below makes the mistake impossible to repeat silently.

Score (lexicographic): 1) clear ratio, 2) worst case ratio, 3) mean time.
"""
import io
import json
import os
import random
import sys
import time

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))

GRIDS = {
    "q3": {
        "ring_radius": [1180.0, 1220.0, 1250.0, 1280.0, 1320.0],
        "probe_spacing": [450.0, 650.0, 850.0],
        "locate_sigma": [220.0, 320.0, 440.0],
        "clear_bonus": [0.0, 260.0, 450.0],
        "probe_min_angle": [12.0, 22.0, 35.0],
        "search_cost_bias": [30.0, 70.0, 150.0],
        "term_cap": [300.0, 420.0, 600.0],
        "endgame_radius": [70.0, 90.0, 130.0],
    },
    "q4": {
        "survey_spacing": [850.0, 1000.0, 1150.0, 1300.0],
        "probe_spacing": [450.0, 650.0, 850.0],
        "locate_sigma": [220.0, 320.0, 440.0],
        "clear_bonus": [0.0, 260.0, 450.0],
        "probe_min_angle": [12.0, 22.0, 35.0],
        "search_cost_bias": [30.0, 70.0, 150.0],
        "max_attempts": [4, 6, 10],
        "rim_step": [100.0, 130.0, 180.0],
        "max_rim_patrols": [4, 8, 14],
    },
}

BASE = {
    "q3": dict(rc.DEFAULT_PARAMS, survey_mode="ring"),
    "q4": dict(rc.DEFAULT_PARAMS, survey_mode="lattice", survey_spacing=1000.0,
               directional=True),
}

MIX = {"q3": 0.0, "q4": 0.5}


def evaluate(params, seeds, mix):
    """Score a candidate.  The cases are rebuilt from the seeds every time."""
    rs, ts, tr = [], [], []
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        st, _ = rc.run_case(srcs, params=params, seed=sd)
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
    return {"ratio": sum(rs) / len(rs), "ratio_min": min(rs),
            "time": sum(ts) / len(ts), "travel": sum(tr) / len(tr)}


def better(a, b):
    if b is None:
        return True
    for k in ("ratio", "ratio_min"):
        if a[k] > b[k] + 1e-9:
            return True
        if a[k] < b[k] - 1e-9:
            return False
    return a["time"] < b["time"] - 1e-9


def self_check(params, seeds, mix):
    """The same configuration must score the same twice.  This is the guard
    against the pool-reuse defect described in the module docstring."""
    a = evaluate(params, seeds[:3], mix)
    b = evaluate(params, seeds[:3], mix)
    same = (abs(a["ratio"] - b["ratio"]) < 1e-12
            and abs(a["time"] - b["time"]) < 1e-9)
    if not same:
        print("[guard] FAILED: re-evaluating the same parameters changed the "
              "score (%.4f/%.1f vs %.4f/%.1f).  The case pool is being mutated."
              % (a["ratio"], a["time"], b["ratio"], b["time"]), flush=True)
        sys.exit(2)
    print("[guard] ok: repeated evaluation is reproducible (%.4f, %.1f s)"
          % (a["ratio"], a["time"]), flush=True)


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "q3"
    n_cases = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    n_pass = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    mix = MIX[tag]
    seeds = [70000 + i for i in range(n_cases)] if tag == "q3" \
        else [90000 + i for i in range(n_cases)]
    grid = GRIDS[tag]
    self_check(BASE[tag], seeds, mix)

    best_p = dict(BASE[tag])
    best_s = evaluate(best_p, seeds, mix)
    print("[%s] baseline ratio=%.4f min=%.4f time=%.2f travel=%.0f"
          % (tag, best_s["ratio"], best_s["ratio_min"], best_s["time"],
             best_s["travel"]), flush=True)
    t0 = time.time()
    for k in range(n_pass):
        improved_any = False
        for name, values in grid.items():
            cur = best_p.get(name)
            for v in values:
                if v == cur:
                    continue
                cand = dict(best_p)
                cand[name] = v
                sc = evaluate(cand, seeds, mix)
                print("[%s] pass%d %-18s = %-8s -> ratio=%.4f min=%.4f time=%.2f"
                      % (tag, k, name, v, sc["ratio"], sc["ratio_min"], sc["time"]),
                      flush=True)
                if better(sc, best_s):
                    best_s, best_p = sc, cand
                    improved_any = True
                    with io.open(os.path.join(OUT, "optimize_%s.json" % tag),
                                 "w", encoding="utf-8") as f:
                        json.dump({"tag": tag, "cases": n_cases, "pass": k,
                                   "score": best_s, "params": best_p,
                                   "elapsed_s": round(time.time() - t0, 1)},
                                  f, ensure_ascii=False, indent=1)
        print("[%s] pass %d done, improved=%s, elapsed=%.0f s"
              % (tag, k, improved_any, time.time() - t0), flush=True)
        if not improved_any:
            break
    print("[%s] FINAL ratio=%.4f min=%.4f time=%.2f travel=%.0f"
          % (tag, best_s["ratio"], best_s["ratio_min"], best_s["time"],
             best_s["travel"]), flush=True)
    print("[%s] PARAMS %s" % (tag, json.dumps(best_p, sort_keys=True)), flush=True)


if __name__ == "__main__":
    main()
