# -*- coding: utf-8 -*-
"""ab_rim.py -- A/B test of the two algorithmic improvements."""
import random
import sys
import time

import robot_core as rc
import simulator as sim


def ev(params, seeds, mix=0.5, tag=""):
    rs, ts, tr = [], [], []
    t0 = time.time()
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        st, _ = rc.run_case(srcs, params=params, seed=sd)
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
    return {"tag": tag, "ratio": sum(rs) / len(rs), "min": min(rs),
            "time": sum(ts) / len(ts), "travel": sum(tr) / len(tr),
            "sec": time.time() - t0}


def show(r):
    print("%-12s ratio=%.4f min=%.4f time=%7.1f travel=%7.0f  (%.0f s)"
          % (r["tag"], r["ratio"], r["min"], r["time"], r["travel"], r["sec"]),
          flush=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "q4"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    if which == "q4":
        seeds = list(range(90000, 90000 + n))
        base = dict(rc.DEFAULT_PARAMS, survey_mode="lattice",
                    survey_spacing=1000.0, directional=True)
        show(ev(base, seeds, 0.5, "I1+I2"))
        show(ev(dict(base, rim_patrol=False), seeds, 0.5, "no patrol"))
    else:
        seeds = list(range(70000, 70000 + n))
        base = dict(rc.DEFAULT_PARAMS, survey_mode="ring")
        show(ev(base, seeds, 0.0, "I1+I2"))
        show(ev(dict(base, rim_patrol=False), seeds, 0.0, "no patrol"))
