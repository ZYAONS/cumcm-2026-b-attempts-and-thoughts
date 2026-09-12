#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
hybrid_scan.py -- 混合策略：较疏的格点扫一遍 + 少量"认证指认的疑点"补站。

思路（这是本轮最关键的算法改动）：
  * 格点扫描的疏密由**覆盖半径**决定：间距 s 的三角格点覆盖半径为 s/√3，
    全向源只要 s ≤ √3·R_min ≈ 1732 m 就保证被发现；
  * 但**定向源**要求格点落在它的受光半圆盘内，因此需要更密；
  * 而认证扫描本身会**精确指认**哪些候选点还没被排除——那些正是
    "定向源可能藏身"的位置。

于是最优组合不是"很密的格点"也不是"很疏的格点+无脑补站"，而是：
  较疏的格点（省站位） + **只补认证真正指认出来的那几个疑点**（省浪费）。

前面测过：s=1100 + 认证搜索不限 = 24 站、874.9 s、1.0000；
          s=1000 纯扫描         = 12.9 站、522.2 s、0.9914。
本脚本扫描 max_search_stops（补站预算），寻找"完成率 1.0000 且时间最低"的工作点。

usage: python hybrid_scan.py [n_cases] [seed0]
"""
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
from make_data import P4  # noqa: E402

BASE = dict(rc.DEFAULT_PARAMS)
BASE.update(P4)
BASE.update({"verify_margin": 900.0, "periodic_cert_every": 1,
             "spread_stops": True, "max_survey_stops": 0,
             "clear_bonus": 500.0, "locate_sigma": 400.0})

CASES = []
for sp in (1000.0, 950.0, 1100.0):
    for b in (0, 2, 4, 6, 10, 40):
        CASES.append((sp, b))


def ev(spacing, budget, seeds):
    p = dict(BASE)
    p.update({"survey_spacing": spacing, "max_search_stops": budget})
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
            "min": min(rs), "fails": sum(1 for r in rs if r < 0.9999),
            "time": statistics.mean(ts), "median": statistics.median(ts),
            "travel": sum(tr) / n, "stops": sum(stops) / n,
            "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d ; sparse lattice + targeted certification stops"
          % (n, seeds[0], seeds[-1]))
    print("%8s %7s %7s %8s %8s %6s %8s %8s"
          % ("spacing", "budget", "stops", "ratio", "min", "fails", "time", "median"))
    out = []
    for sp, b in CASES:
        r = ev(sp, b, seeds)
        out.append(r)
        print("%8.0f %7d %7.1f %8.4f %8.4f %6d %8.1f %8.1f"
              % (sp, b, r["stops"], r["ratio"], r["min"], r["fails"], r["time"],
                 r["median"]), flush=True)
    with open(os.path.join(DATA, "hybrid_scan.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    good = [r for r in out if r["fails"] == 0]
    if good:
        b = min(good, key=lambda r: r["time"])
        print("\nPERFECT and fastest: spacing %.0f budget %d -> %.1f s/source "
              "(%d stops)" % (b["spacing"], b["budget"], b["time"], b["stops"]))
    else:
        print("\nno (spacing, budget) combination is perfect on this pool")
    print("report -> data/hybrid_scan.json")
