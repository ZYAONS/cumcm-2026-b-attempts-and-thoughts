#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tune_q4.py -- random search of the parameters of the mixed omni/directional
strategy (problem 4).  Score = mean time per cleared source + heavy penalty for
uncleared sources.
usage: python tune_q4.py [n_samples] [n_cases]
"""
import json
import os
import random
import statistics
import sys
import time

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))

GRID = {
    "survey_spacing": [800.0, 950.0, 1100.0, 1250.0],
    "probe_spacing": [300.0, 450.0, 650.0, 900.0],
    "locate_sigma": [120.0, 200.0, 320.0, 500.0],
    "clear_try_radius": [25.0, 42.0, 60.0],
    "endgame_radius": [60.0, 90.0, 140.0],
    "endgame_step": [8.0, 11.0, 16.0],
    "term_iters": [9, 14, 20],
    "term_cap": [300.0, 420.0, 600.0],
    "max_attempts": [6, 12, 25],
    "probe_min_angle": [10.0, 22.0, 40.0],
    "search_cost_bias": [30.0, 60.0, 120.0],
}


def score(params, seeds, mix=1.0):
    ts, rs = [], []
    for i, sd in enumerate(seeds):
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        st, _ = rc.run_case(srcs, params=params, seed=i)
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"] if st["n_cleared"] else 9000.0)
    mis = sum(1.0 - r for r in rs) / len(rs)
    return statistics.mean(ts) + 6000.0 * mis, statistics.mean(ts), mis, statistics.mean(rs)


def main():
    n_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    n_cases = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    rnd = random.Random(7)
    seeds = [3000 + k for k in range(n_cases)]
    base = dict(rc.DEFAULT_PARAMS)
    base.update({"survey_mode": "lattice", "directional": True})
    s0, m0, mis0, r0 = score(base, seeds)
    print("baseline: score=%.1f mean=%.1f ratio=%.3f" % (s0, m0, r0), flush=True)
    best = (s0, dict(base))
    t0 = time.time()
    for it in range(n_samples):
        p = dict(base)
        for k in rnd.sample(list(GRID.keys()), rnd.randint(2, 5)):
            p[k] = rnd.choice(GRID[k])
        s, m, mis, r = score(p, seeds)
        if s < best[0]:
            best = (s, p)
            print("  [%3d] score=%.1f mean=%.1f ratio=%.3f  %s" %
                  (it, s, m, r, {k: p[k] for k in GRID if p[k] != base[k]}), flush=True)
    cur, cur_s = best[1], best[0]
    for rounds in range(3):
        improved = False
        for k, vals in GRID.items():
            for v in vals:
                if v == cur[k]:
                    continue
                cand = dict(cur)
                cand[k] = v
                s, m, mis, r = score(cand, seeds)
                if s < cur_s - 1e-9:
                    cur_s, cur, improved = s, cand, True
                    print("  refine %-16s=%-8s score=%.1f mean=%.1f ratio=%.3f"
                          % (k, v, s, m, r), flush=True)
        if not improved:
            break
    print("elapsed %.0f s" % (time.time() - t0))
    test = [9000 + k for k in range(12)]
    s, m, mis, r = score(cur, test)
    sb, mb, misb, rb = score(base, test)
    print("hold-out: tuned mean=%.1f ratio=%.3f | baseline mean=%.1f ratio=%.3f"
          % (m, r, mb, rb))
    with open(os.path.join(OUT, "tuned_params_q4.json"), "w", encoding="utf-8") as f:
        json.dump({"params": cur, "holdout_mean": m, "holdout_ratio": r,
                   "base_mean": mb, "base_ratio": rb}, f, indent=1)


if __name__ == "__main__":
    main()
