#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tune.py -- random-search tuning of the strategy parameters.

A fixed pool of test cases (fixed seeds) is generated once; candidate parameter
vectors are scored with

        score = mean_time_per_cleared_source  (cases that fail to clear
                everything are penalised heavily)

The best vector is then re-validated on an independent pool of cases.
usage:  python tune.py [n_samples] [n_cases]
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

GRID = {
    "probe_spacing": [400.0, 600.0, 850.0, 1100.0, 1500.0, 2200.0],
    "ring_radius": [1050.0, 1150.0, 1280.0, 1400.0, 1550.0],
    "locate_sigma": [150.0, 220.0, 320.0, 450.0, 600.0],
    "vantage_b_local": [350.0, 450.0, 550.0, 700.0, 900.0],
    "vantage_phi_local": [35.0, 45.0, 55.0, 70.0, 85.0],
    "term_cap": [250.0, 350.0, 420.0, 600.0, 800.0],
    "clear_bonus": [0.0, 120.0, 260.0, 400.0, 600.0],
    "survey_spacing": [700.0, 900.0, 1100.0, 1400.0, 1800.0],
    "search_cost_bias": [20.0, 60.0, 120.0, 200.0],
    "probe_min_angle": [10.0, 18.0, 25.0, 35.0, 50.0],
    "use_ring": [False, True],
    "policy": ["planned", "greedy"],
}


def make_pool(n_cases, seed0, kind_mix=0.0):
    """A pool is a list of (seed, kind_mix): cases are rebuilt for every
    evaluation because clearing mutates the Source objects."""
    return [(seed0 + k, kind_mix) for k in range(n_cases)]


def score_params(params, pool, penalty=400.0):
    times, ratios = [], []
    for i, (sd, mix) in enumerate(pool):
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        st, _ = rc.run_case(srcs, params=params, seed=i)
        ratios.append(st["clear_ratio"])
        times.append(st["mean_time"] if st["n_cleared"] else 6000.0)
    mis = sum(1.0 - r for r in ratios) / len(ratios)
    return statistics.mean(times) + penalty * mis * 10.0, statistics.mean(times), mis


def main():
    n_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    n_cases = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    rnd = random.Random(2026)
    pool = make_pool(n_cases, 5000)
    t0 = time.time()

    best = None
    base = dict(rc.DEFAULT_PARAMS)
    s0, m0, mis0 = score_params(base, pool)
    print("baseline: score=%.2f mean=%.2f miscal=%.4f" % (s0, m0, mis0))
    best = (s0, base)

    for it in range(n_samples):
        p = dict(rc.DEFAULT_PARAMS)
        for k in rnd.sample(list(GRID.keys()), rnd.randint(1, 5)):
            p[k] = rnd.choice(GRID[k])
        s, m, mis = score_params(p, pool)
        if s < best[0]:
            best = (s, p)
            print("  [%4d] score=%.2f mean=%.2f miscal=%.4f  %s"
                  % (it, s, m, mis, {k: p[k] for k in GRID if p[k] != rc.DEFAULT_PARAMS[k]}))
    print("elapsed %.1f s" % (time.time() - t0))

    # coordinate refinement around the best vector
    cur = dict(best[1])
    cur_score = best[0]
    improved = True
    rounds = 0
    while improved and rounds < 4:
        improved = False
        rounds += 1
        for k, vals in GRID.items():
            for v in vals:
                if v == cur[k]:
                    continue
                cand = dict(cur)
                cand[k] = v
                s, m, mis = score_params(cand, pool)
                if s < cur_score - 1e-9:
                    cur_score, cur = s, cand
                    improved = True
                    print("  refine %-16s = %-8s -> score %.2f (mean %.2f)"
                          % (k, v, s, m))
    print("\nbest params:")
    for k in GRID:
        print("   %-16s %s" % (k, cur[k]))
    test_pool = make_pool(n_cases, 9000)
    s, m, mis = score_params(cur, test_pool)
    sb, mb, misb = score_params(dict(rc.DEFAULT_PARAMS), test_pool)
    print("\nhold-out (%d cases): tuned mean=%.2f miscal=%.4f | default mean=%.2f miscal=%.4f"
          % (n_cases, m, mis, mb, misb))
    with open(os.path.join(OUT, "tuned_params.json"), "w", encoding="utf-8") as f:
        json.dump({"params": cur, "holdout_mean": m, "holdout_mis": mis,
                   "default_mean": mb, "default_mis": misb}, f, indent=1)


if __name__ == "__main__":
    main()
