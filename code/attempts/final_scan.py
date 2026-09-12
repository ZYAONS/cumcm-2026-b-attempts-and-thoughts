#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
final_scan.py -- 配置 F（每站认证 + 无边距限制 + 纯扫描）下的最优间距。

push_under_500 显示 F 配置在 s=900 时给出 516 s / 完成率 0.9928，
离 500 s 只差 16 s。剩下的唯一大杠杆是**站位数量**：
s=1000 只有 13 个站位（对比 s=900 的 19 个），每少一个站位就少
约 1114 m 行程与 20 次检测。本脚本在 F 配置下把间距扫一遍，
寻找"500 s 以内且完成率不低于 0.99"的工作点。

usage: python final_scan.py [n_cases] [seed0]
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

BASE = dict(rc.DEFAULT_PARAMS)
BASE.update(P4)
BASE.update({"max_search_stops": 0, "verify_margin": 900.0,
             "periodic_cert_every": 1})

SPACINGS = [750.0, 800.0, 850.0, 900.0, 950.0, 1000.0, 1050.0, 1100.0, 1200.0]


def ev(spacing, seeds):
    p = dict(BASE)
    p["survey_spacing"] = spacing
    rs, ts, tr, stops, meas = [], [], [], [], []
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
        meas.append(st["n_measure"])
    n = float(len(seeds))
    return {"spacing": spacing, "ratio": sum(rs) / n, "min": min(rs),
            "time": sum(ts) / n, "travel": sum(tr) / n,
            "stops": sum(stops) / n, "measure": sum(meas) / n,
            "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("config F (cert every stop, margin 900, pure sweep), %d cases" % n)
    print("%8s %7s %8s %8s %8s %8s %8s"
          % ("spacing", "stops", "ratio", "min", "time", "travel", "measure"))
    out = []
    for sp in SPACINGS:
        r = ev(sp, seeds)
        out.append(r)
        print("%8.0f %7.1f %8.4f %8.4f %8.1f %8.0f %8.0f"
              % (r["spacing"], r["stops"], r["ratio"], r["min"], r["time"],
                 r["travel"], r["measure"]), flush=True)
    with open(os.path.join(DATA, "final_scan.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/final_scan.json")
