# -*- coding: utf-8 -*-
"""validate_opt.py -- check the tuned parameters on an independent case pool.

usage: python validate_opt.py q3|q4 [n_cases]
"""
import random
import sys
import time

import robot_core as rc
import simulator as sim


def ev(params, seeds, mix):
    rs, ts, tr = [], [], []
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        st, _ = rc.run_case(srcs, params=params, seed=sd)
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
    n = float(len(seeds))
    return {"ratio": sum(rs) / n, "min": min(rs), "time": sum(ts) / n,
            "travel": sum(tr) / n}


def show(tag, r):
    print("%-26s ratio=%.4f  min=%.4f  time=%7.1f  travel=%7.0f"
          % (tag, r["ratio"], r["min"], r["time"], r["travel"]), flush=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "q3"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    if which == "q3":
        seeds = list(range(31000, 31000 + n))
        base = dict(rc.DEFAULT_PARAMS, survey_mode="ring", ring_radius=1280.0)
        tuned = dict(rc.DEFAULT_PARAMS, survey_mode="ring", ring_radius=1250.0)
        t0 = time.time()
        show("Q3 baseline (rho=1280)", ev(base, seeds, 0.0))
        show("Q3 tuned    (rho=1250)", ev(tuned, seeds, 0.0))
    else:
        seeds = list(range(51000, 51000 + n))
        base = dict(rc.DEFAULT_PARAMS, survey_mode="lattice",
                    survey_spacing=1000.0, directional=True)
        tuned = dict(rc.DEFAULT_PARAMS, survey_mode="lattice",
                     survey_spacing=850.0, directional=True)
        t0 = time.time()
        show("Q4 baseline (spacing=1000)", ev(base, seeds, 0.5))
        show("Q4 tuned    (spacing=850)", ev(tuned, seeds, 0.5))
    print("elapsed %.0f s" % (time.time() - t0))
