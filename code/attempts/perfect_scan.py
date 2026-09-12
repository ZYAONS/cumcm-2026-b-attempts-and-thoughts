#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
perfect_scan.py -- 在"完成率必须 1.0000"的约束下，扫描纯扫描配置的间距。

pure_vs_search 的关键结果（24 例）：
    A 论文配置 s1100 + 认证搜索 : 完成率 1.0000（最差 1.0000）/ 874.9 s
    B 纯扫描 s900              : 0.9974（最差 0.9375）/ 547.8 s
    C 纯扫描 s1000             : 0.9914（最差 0.9231）/ 522.2 s
    D 纯扫描 s900 + cb500/ls400 : **1.0000（最差 1.0000）/ 540.3 s**

配置 D 用 38% 的时间拿到了与论文配置**完全相同**的完成率。
本脚本在 D 的参数基础上扫描间距，目标：**保持 1.0000 的同时把时间压到 500 s 附近**。

usage: python perfect_scan.py [n_cases] [seed0]
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
BASE.update({"max_search_stops": 0, "verify_margin": 900.0,
             "periodic_cert_every": 1, "spread_stops": True,
             "max_survey_stops": 0, "clear_bonus": 500.0, "locate_sigma": 400.0})

SPACINGS = [850.0, 900.0, 950.0, 1000.0, 1050.0, 1100.0]


def ev(spacing, seeds):
    p = dict(BASE)
    p["survey_spacing"] = spacing
    rs, ts, tr, meas, stops = [], [], [], [], []
    t0 = time.time()
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=p, seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
        meas.append(st["n_measure"])
        stops.append(len(br.visited_stops))
    n = float(len(seeds))
    # a case with ratio < 1 counts as a failure regardless of the mean
    fails = sum(1 for r in rs if r < 0.9999)
    return {"spacing": spacing, "ratio": sum(rs) / n, "min": min(rs),
            "fails": fails, "time": statistics.mean(ts),
            "median": statistics.median(ts), "travel": sum(tr) / n,
            "measure": sum(meas) / n, "stops": sum(stops) / n,
            "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d ; pure sweep + relocate + exhaustive + cb500"
          % (n, seeds[0], seeds[-1]))
    print("%8s %7s %8s %8s %6s %8s %8s %7s"
          % ("spacing", "stops", "ratio", "min", "fails", "time", "median",
             "travel"))
    out = []
    for sp in SPACINGS:
        r = ev(sp, seeds)
        out.append(r)
        print("%8.0f %7.1f %8.4f %8.4f %6d %8.1f %8.1f %7.0f"
              % (sp, r["stops"], r["ratio"], r["min"], r["fails"], r["time"],
                 r["median"], r["travel"]), flush=True)
    with open(os.path.join(DATA, "perfect_scan.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    good = [r for r in out if r["fails"] == 0]
    if good:
        b = min(good, key=lambda r: r["time"])
        print("\nPERFECT (no failing case) and fastest: spacing %.0f -> %.1f s/source"
              % (b["spacing"], b["time"]))
    print("report -> data/perfect_scan.json")
