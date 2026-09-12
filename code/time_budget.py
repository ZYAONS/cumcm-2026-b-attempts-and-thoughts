#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
time_budget.py -- where does the virtual time actually go now?

Completion is saturated at 1.0000 for both problems, so the only remaining lever
is time.  Before proposing optimisations, measure the budget:

  * by task class (census / probe / localise / clear): count, travel, time, and
    the share of each
  * inside the clear task: how much is travel, how many clear actions, how many
    homing iterations
  * inside the probe task: how much is the 5 s detection itself versus switching
    versus travel between stops
  * the theoretical floor: travel of an optimal tour over the stops actually
    visited, and the detection time that cannot be avoided

usage: python time_budget.py [mode] [n_cases] [seed0]
"""
import json
import math
import os
import random
import sys

import geom_core as g
import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
from make_data import P3, P4  # noqa: E402


def nearest_tour_len(points, start=(0.0, 0.0)):
    """Nearest-neighbour tour length over `points` starting at `start`."""
    rest = list(points)
    cur, tot = start, 0.0
    while rest:
        i = min(range(len(rest)),
                key=lambda k: (rest[k][0] - cur[0]) ** 2 + (rest[k][1] - cur[1]) ** 2)
        nxt = rest.pop(i)
        tot += math.hypot(nxt[0] - cur[0], nxt[1] - cur[1])
        cur = nxt
    return tot


def analyse(mode, seeds):
    params = dict(rc.DEFAULT_PARAMS)
    params.update(P3 if mode == "q3" else P4)
    agg = {"cases": 0, "task": {}, "travel": 0.0, "vtime": 0.0,
           "stops": 0, "measure": 0, "switch": 0, "clear_actions": 0,
           "tour_floor": 0.0, "sources": 0}
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=(0.0 if mode == "q3" else 0.5))
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=params, seed=sd)
        st = br.run()
        agg["cases"] += 1
        agg["travel"] += st["travel_m"]
        agg["vtime"] += st["virtual_time"]
        agg["measure"] += st["n_measure"]
        agg["switch"] += st["n_switch"]
        agg["clear_actions"] += st["n_clear"]
        agg["sources"] += st["n_sources"]
        for k, v in st["task_count"].items():
            agg["task"].setdefault(k, {"count": 0, "travel": 0.0, "time": 0.0})
            agg["task"][k]["count"] += v
        for k, v in st["task_travel"].items():
            agg["task"].setdefault(k, {"count": 0, "travel": 0.0, "time": 0.0})
            agg["task"][k]["travel"] += v
        for k, v in st["task_time"].items():
            agg["task"].setdefault(k, {"count": 0, "travel": 0.0, "time": 0.0})
            agg["task"][k]["time"] += v
        # floor: the stops actually visited form a set; a nearest-neighbour tour
        # over them starting at the origin is a lower bound proxy for good routing
        pts = list(br.visited_stops)
        agg["stops"] += len(pts)
        agg["tour_floor"] += nearest_tour_len([(p[0], p[1]) for p in pts])
    return agg


def report(mode, a):
    c = float(a["cases"])
    print("=" * 78)
    print("%s : %d cases, %d sources, mean virtual time %.0f s, mean travel %.0f m"
          % (mode.upper(), a["cases"], a["sources"], a["vtime"] / c,
             a["travel"] / c))
    print("  detections %d (%.0f/case), switches %d, clear actions %d, stops %d "
          "(%.1f/case)"
          % (a["measure"], a["measure"] / c, a["switch"], a["clear_actions"],
             a["stops"], a["stops"] / c))
    vt = a["vtime"]
    print("  --- by task class ---")
    for k in sorted(a["task"], key=lambda x: -a["task"][x]["time"]):
        t = a["task"][k]
        print("   %-9s count=%6.1f  travel=%9.0f m (%4.1f%%)  time=%8.0f s (%4.1f%%)"
              % (k, t["count"] / c, t["travel"] / c, 100 * t["travel"] / a["travel"],
                 t["time"] / c, 100 * t["time"] / vt))
    det = a["measure"] * sim.MEASURE_TIME
    sw = a["switch"] * sim.SWITCH_TIME
    tr = a["travel"] / sim.SPEED
    cl = a["clear_actions"] * sim.CLEAR_TIME_HIT * 0.45 + a["clear_actions"] * sim.CLEAR_TIME_MISS * 0.55
    print("  --- by action type (mean per case) ---")
    print("   movement      %8.0f s (%4.1f%%)" % (tr / c, 100 * tr / vt))
    print("   detection     %8.0f s (%4.1f%%)" % (det / c, 100 * det / vt))
    print("   switch        %8.0f s (%4.1f%%)" % (sw / c, 100 * sw / vt))
    print("   clear pulse   %8.0f s (%4.1f%%)  (approx, hit/miss mix)"
          % (cl / c, 100 * cl / vt))
    print("  --- routing headroom ---")
    print("   visited stops %.1f/case; a nearest-neighbour tour over them from the "
          "origin would cost %.0f m (%.1f%% of the actual travel)"
          % (a["stops"] / c, a["tour_floor"] / c,
             100 * (a["tour_floor"] / c) / (a["travel"] / c)))
    print("=" * 78)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "q4"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    seed0 = int(sys.argv[3]) if len(sys.argv) > 3 else 30000
    a = analyse(mode, list(range(seed0, seed0 + n)))
    report(mode, a)
    with open(os.path.join(DATA, "time_budget_%s.json" % mode), "w",
              encoding="utf-8") as f:
        json.dump(a, f, ensure_ascii=False, indent=1)
