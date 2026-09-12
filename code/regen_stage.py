#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
regen_stage.py -- regenerate the problem 3/4 drill data one stage at a time.

`make_data.py` does everything in one go (about ten minutes) and the background
harness kills a job at that point, so the work is split into short stages:

  python regen_stage.py q3      # 60 problem-3 cases + sensitivity
  python regen_stage.py q4      # 60 mixed cases
  python regen_stage.py q4ext   # all-directional and all-omni scenarios
  python regen_stage.py q4sens  # problem-4 sensitivity sweep
  python regen_stage.py agg     # aggregate file + greedy comparison
"""
import csv
import io
import json
import os
import random
import statistics
import sys
import time

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))

from make_data import P3, P4, run_cases, sensitivity, jdump  # noqa: E402


def q3():
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P3)
    rows, agg = run_cases(p, 60, 0.0, 20000, "q3")
    print("  Q3: ratio=%.4f mean=%.1f travel=%.0f"
          % (agg["mean_ratio"], agg["mean_time"], agg["mean_travel"]))
    sensitivity(p, 0.0, "q3")


def q4():
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    rows, agg = run_cases(p, 60, 0.5, 30000, "q4")
    print("  Q4 (mixed): ratio=%.4f mean=%.1f travel=%.0f"
          % (agg["mean_ratio"], agg["mean_time"], agg["mean_travel"]))


def q4ext():
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    for nm, mix in (("q4_alldir", 1.0), ("q4_omni", 0.0)):
        _, a = run_cases(p, 30, mix, 35000, nm, verbose=False)
        print("  %s: ratio=%.4f mean=%.1f" % (nm, a["mean_ratio"], a["mean_time"]))


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "q3"
    t0 = time.time()
    if which == "q3":
        q3()
    elif which == "q4":
        q4()
    elif which == "q4ext":
        q4ext()
    elif which == "q4sens":
        p = dict(rc.DEFAULT_PARAMS)
        p.update(P4)
        sensitivity(p, 0.5, "q4")
    elif which == "agg":
        def jl(n):
            with io.open(os.path.join(DATA, n), encoding="utf-8") as f:
                return json.load(f)
        agg = {k: jl("%s_agg.json" % k)
               for k in ("q3", "q4", "q4_alldir", "q4_omni")}
        jdump("q34_agg.json", agg)

        def run(params, n, mix, seed0, tag):
            rs, ts, tr = [], [], []
            for i in range(n):
                srcs = sim.make_case(random.Random(seed0 + i), kind_mix=mix)
                st, _ = rc.run_case(srcs, params=params, seed=seed0 + i)
                rs.append(st["clear_ratio"])
                ts.append(st["mean_time"] if st["n_cleared"] else float("inf"))
                tr.append(st["travel_m"])
            a = {"n_cases": n, "mean_ratio": sum(rs) / n,
                 "mean_time": sum(ts) / n, "mean_travel": sum(tr) / n}
            print("  %-12s ratio=%.4f mean=%7.1f travel=%7.0f"
                  % (tag, a["mean_ratio"], a["mean_time"], a["mean_travel"]),
                  flush=True)
            return a

        p3 = dict(rc.DEFAULT_PARAMS)
        p3.update(P3)
        pg = dict(rc.DEFAULT_PARAMS)
        pg.update({"policy": "greedy", "survey_spacing": 1250.0})
        out = {"planned_q3": agg["q3"], "greedy_q3": run(pg, 30, 0.0, 20000, "greedy_q3"),
               "planned_q4": agg["q4"],
               "greedy_q4": run(dict(pg, directional=True), 30, 0.5, 30000, "greedy_q4")}
        jdump("policy_compare.json", out)
    print("stage %s done in %.0f s" % (which, time.time() - t0))
