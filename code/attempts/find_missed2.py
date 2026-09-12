#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
find_missed2.py -- 纯扫描配置（s=1000）到底漏在什么地方、慢在什么地方。

已知：s=1000 纯扫描 533.8 s、最差完成率 0.9833（120 例 14 例失败）；
      而 P4+rim12 是 753.1 s、0.9978（1/120）。
若能查清纯扫描"漏"的具体机理，就有机会用很小的代价补上，
从而同时拿到低时间与高完成率。

本脚本对每个失败源输出：半径、类型、朝向、是否受光于已访站位、
观测条数、状态，以及"该源到最近访问站位的距离"。

usage: python find_missed2.py [n_per_pool] [spacing]
"""
import json
import math
import os
import random
import statistics
import sys

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
from make_data import P4  # noqa: E402

POOLS = [("A", 62000), ("B", 51000), ("C", 12000), ("D", 30000)]


def cfg(spacing):
    return dict(P4, survey_spacing=spacing, max_search_stops=0,
                verify_margin=900.0, periodic_cert_every=1, spread_stops=True,
                max_survey_stops=0, clear_bonus=500.0, locate_sigma=400.0)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    spacing = float(sys.argv[2]) if len(sys.argv) > 2 else 1000.0
    missed, tot, times, stops = [], 0, [], []
    for pname, s0 in POOLS:
        for sd in range(s0, s0 + n):
            srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
            ar = sim.Arena(srcs, seed=sd)
            br = rc.Brain(rc.LocalClient(ar), params=dict(rc.DEFAULT_PARAMS,
                                                          **cfg(spacing)), seed=sd)
            st = br.run()
            tot += len(srcs)
            times.append(st["mean_time"])
            stops.append(len(br.visited_stops))
            for s in srcs:
                if not s.cleared:
                    near = min((math.hypot(s.x - q[0], s.y - q[1])
                                for q in br.visited_stops), default=1e9)
                    lit_near = sum(1 for q in br.visited_stops
                                   if s.covers(q[0], q[1])
                                   and math.hypot(s.x - q[0], s.y - q[1]) <= s.r_eff)
                    missed.append({
                        "pool": pname, "seed": sd, "ch": s.channel,
                        "r": round(math.hypot(s.x, s.y)), "kind": s.kind,
                        "dir": None if s.direction is None else round(s.direction),
                        "r_eff": round(s.r_eff),
                        "status": br.status.get(s.channel),
                        "obs": len(br.obs.get(s.channel, [])),
                        "d_nearest_stop": round(near),
                        "lit_stops_within_Reff": lit_near})
    print("spacing %.0f : %d sources, %d missed (%.3f%%), mean time %.1f s, "
          "mean stops %.1f"
          % (spacing, tot, len(missed), 100.0 * len(missed) / tot,
             statistics.mean(times), statistics.mean(stops)))
    print("%-5s %-7s %-4s %6s %-11s %-6s %6s %-9s %5s %8s %6s"
          % ("pool", "seed", "ch", "r", "kind", "dir", "R_eff", "status", "obs",
             "d_near", "lit"))
    for m in missed:
        print("%-5s %-7d %-4d %6d %-11s %-6s %6d %-9s %5d %8d %6d"
              % (m["pool"], m["seed"], m["ch"], m["r"], m["kind"], m["dir"],
                 m["r_eff"], m["status"], m["obs"], m["d_nearest_stop"],
                 m["lit_stops_within_Reff"]))
    with open(os.path.join(DATA, "find_missed2.json"), "w", encoding="utf-8") as f:
        json.dump({"spacing": spacing, "total": tot, "missed": missed}, f,
                  ensure_ascii=False, indent=1)
    print("report -> data/find_missed2.json")
