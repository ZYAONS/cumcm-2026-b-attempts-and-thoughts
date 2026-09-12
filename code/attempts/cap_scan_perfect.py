#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cap_scan_perfect.py -- s=900 纯扫描下扫描站位上限，约束是"每个算例都必须清完"。

perfect_scan 的结果（24 例，纯扫描 + relocate + exhaustive + cb500/ls400）：
    s=850   3 个算例未清完   542.7 s
    s=900   0 个算例未清完   **540.3 s**   <- 唯一"完美"的一档
    s=950   4 个算例未清完   506.7 s
    s=1000  4 个算例未清完   509.2 s
    s=1050 13 个算例未清完   429.4 s

s=900 是唯一的甜点，但 540 s 离 500 s 还差 40 s。
每少一个站位约省 1114 m 行程（223 s）与约 15 次检测（90 s），折合约 25 s/源，
所以只要能在**不丢完成率**的前提下少 2 个站位，就能进入 500 s。

本脚本用 max_survey_stops 扫描 14~18 个站位（最远点采样排序，保证覆盖均匀）。

usage: python cap_scan_perfect.py [n_cases] [seed0]
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
BASE.update({"survey_spacing": 900.0, "max_search_stops": 0, "verify_margin": 900.0,
             "periodic_cert_every": 1, "spread_stops": True,
             "clear_bonus": 500.0, "locate_sigma": 400.0})

CAPS = [13, 14, 15, 16, 17, 18, 0]


def ev(cap, seeds):
    p = dict(BASE)
    p["max_survey_stops"] = cap
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
    return {"cap": cap, "ratio": sum(rs) / n, "min": min(rs),
            "fails": sum(1 for r in rs if r < 0.9999),
            "time": statistics.mean(ts), "median": statistics.median(ts),
            "travel": sum(tr) / n, "stops": sum(stops) / n,
            "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d, s=900 pure sweep" % (n, seeds[0], seeds[-1]))
    print("%6s %7s %8s %8s %6s %8s %8s"
          % ("cap", "stops", "ratio", "min", "fails", "time", "median"))
    out = []
    for c in CAPS:
        r = ev(c, seeds)
        out.append(r)
        print("%6d %7.1f %8.4f %8.4f %6d %8.1f %8.1f"
              % (c, r["stops"], r["ratio"], r["min"], r["fails"], r["time"],
                 r["median"]), flush=True)
    with open(os.path.join(DATA, "cap_scan_perfect.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    good = [r for r in out if r["fails"] == 0]
    if good:
        b = min(good, key=lambda r: r["time"])
        print("\nPERFECT and fastest: cap=%d -> %.1f s/source (%d stops)"
              % (b["cap"], b["time"], b["stops"]))
    print("report -> data/cap_scan_perfect.json")
