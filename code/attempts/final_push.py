#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
final_push.py -- 在 500 s 以内把完成率拿回来。

已测得的两个端点：
    s=900 全量扫描（18.4 站）  516.0 s   完成率 0.9928     <- 完成率高，超时 16 s
    s=950         （13.0 站）  493.2 s   完成率 0.9782     <- 达标，完成率低 1.5 个点

差异的来源是**站位数量**（18.4 对 13.0）：少 5.4 个站位省下约 16 s/源，
同时少发现一部分源。若能只补回"最值钱的那几个额外站位"，
就有机会同时拿到 500 s 以内与高完成率。

本脚本在 s=950 上扫描 max_search_stops（额外认证/搜索站位预算），
并在 s=900/950 上对比，寻找 500 s 以内的最高完成率。

usage: python final_push.py [n_cases] [seed0]
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

CONFIGS = []
for sp in (950.0, 900.0):
    for b in (0, 1, 2, 3, 5):
        CONFIGS.append((sp, b))


def ev(spacing, budget, seeds):
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    p.update({"survey_spacing": spacing, "max_search_stops": budget,
              "verify_margin": 900.0, "periodic_cert_every": 1})
    rs, ts, tr, stops = [], [], [], []
    t0 = time.time()
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=p, seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
        stops.append(len(br.visited_stops))
    n = float(len(seeds))
    return {"spacing": spacing, "budget": budget, "ratio": sum(rs) / n,
            "min": min(rs), "time": sum(ts) / n, "travel": sum(tr) / n,
            "stops": sum(stops) / n, "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d" % (n, seeds[0], seeds[-1]))
    print("%8s %7s %7s %8s %8s %8s %8s"
          % ("spacing", "budget", "stops", "ratio", "min", "time", "travel"))
    out = []
    for sp, b in CONFIGS:
        r = ev(sp, b, seeds)
        out.append(r)
        mark = "  <== under 500 s" if r["time"] < 500.0 else ""
        print("%8.0f %7d %7.1f %8.4f %8.4f %8.1f %8.0f%s"
              % (r["spacing"], r["budget"], r["stops"], r["ratio"], r["min"],
                 r["time"], r["travel"], mark), flush=True)
    with open(os.path.join(DATA, "final_push.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    best = max([r for r in out if r["time"] < 500.0], key=lambda r: r["ratio"],
               default=None)
    if best:
        print("\nBEST UNDER 500 s: spacing %.0f, budget %d -> %.4f completion at "
              "%.1f s/source (min %.4f)"
              % (best["spacing"], best["budget"], best["ratio"], best["time"],
                 best["min"]))
    print("report -> data/final_push.json")
