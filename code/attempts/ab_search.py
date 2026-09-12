# -*- coding: utf-8 -*-
"""ab_search.py -- the search stops, not the clearing, dominate problem 4
(89 % of travel and time, 65 probe tasks against 12 clear tasks).  Test what
bounds the useless ones.

Variants
  cur      : as is
  cap12    : max_search_stops 40 -> 12
  cap6     : max_search_stops 40 -> 6
  nofb     : the "plain coverage" fallback stop is disabled in directional runs
             (such a stop can never certify a rim candidate)
"""
import random
import sys
import time

import robot_core as rc
import simulator as sim

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
SEEDS = list(range(90000, 90000 + N))
BASE = dict(rc.DEFAULT_PARAMS, survey_mode="lattice", survey_spacing=1000.0,
            directional=True)


def ev(params, tag):
    rs, ts, tr, npr = [], [], [], []
    for sd in SEEDS:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        st, _ = rc.run_case(srcs, params=params, seed=sd)
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
        npr.append(st["task_count"].get("probe", 0))
    print("%-8s ratio=%.4f min=%.4f time=%7.1f travel=%7.0f probes=%4.1f"
          % (tag, sum(rs) / N, min(rs), sum(ts) / N, sum(tr) / N, sum(npr) / N),
          flush=True)


if __name__ == "__main__":
    t0 = time.time()
    ev(BASE, "cur")
    ev(dict(BASE, max_search_stops=12), "cap12")
    ev(dict(BASE, max_search_stops=6), "cap6")
    ev(dict(BASE, no_plain_fallback=True), "nofb")
    ev(dict(BASE, max_search_stops=12, no_plain_fallback=True), "both")
    print("elapsed %.0f s" % (time.time() - t0))
