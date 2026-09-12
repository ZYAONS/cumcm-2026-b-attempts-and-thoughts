#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pure_sweep.py -- 只用格点扫描，不做额外的认证搜索。

cert_budget_curve 给出的结论很清楚：
    spacing 1100, 无额外站位 :  402 s, 完成率 0.9469
    spacing  900, 无额外站位 :  532 s, 完成率 0.9928
    spacing  900, 有额外站位 :  844 s, 完成率 0.9967

也就是说额外认证搜索花掉 ~310 s 只买到 0.4 个百分点。问题在于间距 900 的格点
仍然不足以"一次扫描即完成认证"。

本实验把间距扫一遍（不做任何额外站位），找到"一次扫描"能同时完成
发现与认证的最优间距——如果存在，总时间应当落到 500 s 附近。

usage: python pure_sweep.py [n_cases] [seed0]
"""
import json
import os
import random
import sys
import time

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
from make_data import P4  # noqa: E402

SPACINGS = [500.0, 600.0, 700.0, 800.0, 900.0, 1000.0, 1100.0, 1300.0]


def evaluate(spacing, seeds, budget=0, mix=0.5):
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    p["survey_spacing"] = spacing
    p["max_search_stops"] = budget
    rs, ts, tr, stops, meas = [], [], [], [], []
    t0 = time.time()
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=p, seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
        stops.append(len(br.visited_stops))
        meas.append(st["n_measure"])
    n = float(len(seeds))
    return {"spacing": spacing, "budget": budget, "ratio": sum(rs) / n,
            "min": min(rs), "time": sum(ts) / n, "travel": sum(tr) / n,
            "stops": sum(stops) / n, "measure": sum(meas) / n,
            "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("pure lattice sweep, no certification search")
    print("%d cases, seeds %d..%d" % (n, seeds[0], seeds[-1]))
    print("%8s %7s %8s %8s %8s %8s %8s"
          % ("spacing", "stops", "ratio", "min", "time", "travel", "measure"))
    out = []
    for sp in SPACINGS:
        r = evaluate(sp, seeds)
        out.append(r)
        print("%8.0f %7.1f %8.4f %8.4f %8.1f %8.0f %8.0f"
              % (r["spacing"], r["stops"], r["ratio"], r["min"], r["time"],
                 r["travel"], r["measure"]), flush=True)
    with open(os.path.join(DATA, "pure_sweep.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/pure_sweep.json")
