#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
margin_scan.py -- 认证要多大边距，才能"一次格点扫描即完成认证"？

periodic_cert 已接入，但实测 9 次认证评估一个频道都没判定为"不存在"。
原因是几何的：候选点离边界越近，其所在格点三角形的**外侧顶点会落到目标域之外**
而被排除，剩下的点无法从各个方向包围它，于是永远认证不了。

本实验扫描 verify_margin，观察
  * 有多少频道在一次扫描后即被判定为"不存在"
  * 完成率与时间如何变化
从而找到"扫描 + 认证"合一的最小代价。

usage: python margin_scan.py [n_cases] [seed0] [spacing]
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

MARGINS = [90.0, 200.0, 350.0, 500.0, 700.0, 900.0]


def evaluate(margin, spacing, seeds, budget=0, mix=0.5):
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    p["survey_spacing"] = spacing
    p["max_search_stops"] = budget
    p["verify_margin"] = margin
    rs, ts, tr, stops, meas, emptied = [], [], [], [], [], []
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
        emptied.append(sum(1 for c in br.channels if br.status[c] == "empty"))
    n = float(len(seeds))
    return {"margin": margin, "spacing": spacing, "ratio": sum(rs) / n,
            "min": min(rs), "time": sum(ts) / n, "travel": sum(tr) / n,
            "stops": sum(stops) / n, "measure": sum(meas) / n,
            "emptied": sum(emptied) / n, "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    spacing = float(sys.argv[3]) if len(sys.argv) > 3 else 900.0
    seeds = list(range(seed0, seed0 + n))
    print("spacing %.0f, pure sweep (no search stops), %d cases" % (spacing, n))
    print("%8s %8s %8s %8s %8s %8s %8s %8s"
          % ("margin", "empty/ch", "stops", "ratio", "min", "time", "travel",
             "measure"))
    out = []
    for m in MARGINS:
        r = evaluate(m, spacing, seeds)
        out.append(r)
        print("%8.0f %8.2f %8.1f %8.4f %8.4f %8.1f %8.0f %8.0f"
              % (r["margin"], r["emptied"], r["stops"], r["ratio"], r["min"],
                 r["time"], r["travel"], r["measure"]), flush=True)
    with open(os.path.join(DATA, "margin_scan.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/margin_scan.json")
