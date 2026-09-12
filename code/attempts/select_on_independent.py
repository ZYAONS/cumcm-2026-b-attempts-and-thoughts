#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
select_on_independent.py -- 直接在**独立算例池**上选型（不再用调参池）。

教训（本项目第三次遇到）：调参池（种子 30000+）系统性地比独立池容易。
    P4_PERFECT 在调参池上 1.0000 / 540.3 s，
    在独立池 A/B 上却是 0.9946 / 547.4 s 与 0.9866 / 593.2 s。
因此**只在独立池上做最终选择**。

本轮要回答的问题：纯格点扫描（省站位但"盲目"）与论文配置（24 站，含认证搜索）
之间的差距，能否靠"较疏格点 + 少量认证指认的补站"这种**混合**补回来。

usage: python select_on_independent.py [n_cases] [pool_seed0]
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
for sp in (900.0, 1000.0, 1100.0):
    for b in (0, 3, 6, 12, 40):
        CASES.append((sp, b))


def ev(spacing, budget, seeds):
    p = dict(BASE)
    p.update({"survey_spacing": spacing, "max_search_stops": budget})
    rs, ts, tr, stops = [], [], [], []
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
            "travel": sum(tr) / n, "stops": sum(stops) / n}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    s0 = int(sys.argv[2]) if len(sys.argv) > 2 else 62000
    seeds = list(range(s0, s0 + n))
    print("INDEPENDENT pool, %d cases, seeds %d..%d" % (n, seeds[0], seeds[-1]))
    print("%8s %7s %7s %8s %8s %6s %8s %8s"
          % ("spacing", "budget", "stops", "ratio", "min", "fails", "time",
             "median"))
    out = []
    for sp, b in CASES:
        r = ev(sp, b, seeds)
        out.append(r)
        print("%8.0f %7d %7.1f %8.4f %8.4f %6d %8.1f %8.1f"
              % (sp, b, r["stops"], r["ratio"], r["min"], r["fails"], r["time"],
                 r["median"]), flush=True)
    with open(os.path.join(DATA, "select_on_independent.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    good = [r for r in out if r["fails"] == 0]
    if good:
        b = min(good, key=lambda r: r["time"])
        print("\nPERFECT on the independent pool and fastest: spacing %.0f "
              "budget %d -> %.1f s/source (%d stops)"
              % (b["spacing"], b["budget"], b["time"], b["stops"]))
    else:
        best = max(out, key=lambda r: r["ratio"])
        print("\nno perfect configuration; best ratio %.4f (spacing %.0f, "
              "budget %d, %.1f s)"
              % (best["ratio"], best["spacing"], best["budget"], best["time"]))
    print("report -> data/select_on_independent.json")
