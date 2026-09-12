#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
detect_min.py -- 检测次数是最后一个大项：443 次 = 2658 s，占 35%。

已确认的事实
------------
* 路由已近最优：实测路径 21583 m，对同一批点的 2-opt 巡回是 19964 m，**只差 8%**（25 s/源）；
* 清除行程 8633 m 与 13 个源的 TSP（8635 m）**完全相同**——也已最优；
* 于是剩下的唯一大项就是**检测次数**。

443 次检测的构成（估算）：
    入场普查               20
    格点站位 12.9 × 11  ≈  142
    贴边环   12   ×  7  ≈   84
    清除归航 13   ×  9  ≈  117
    补测站位  5   × 12  ≈   60

其中**清除归航（117）与补测（60）合计占 40%**，而它们与"站位采样"无关，
属于定位/清除流程内部的开销。本脚本扫描与它们相关的参数。

usage: python detect_min.py [n_cases] [seed0]
"""
import json
import os
import random
import statistics
import sys

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
from make_data import P4  # noqa: E402

BASE = dict(rc.DEFAULT_PARAMS)
BASE.update(P4)
BASE.update({"clear_bonus": 250.0})          # 实测优于 500

VARIANTS = [
    ("baseline (cb250)", {}),
    ("locate_sigma 300", {"locate_sigma": 300.0}),
    ("locate_sigma 250", {"locate_sigma": 250.0}),
    ("term_cap 260", {"term_cap": 260.0}),
    ("relocate_sigma 700", {"relocate_sigma": 700.0}),
    ("locate_sigma 300 + cap260", {"locate_sigma": 300.0, "term_cap": 260.0}),
    ("endgame_radius 60", {"endgame_radius": 60.0}),
    ("exhaustive_after 1", {"exhaustive_after": 1}),
]


def ev(ov, seeds):
    p = dict(BASE)
    p.update(ov)
    rs, ts, tr, meas = [], [], [], []
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=p, seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
        meas.append(st["n_measure"])
    n = float(len(seeds))
    return {"ratio": sum(rs) / n, "min": min(rs),
            "fails": sum(1 for r in rs if r < 0.9999),
            "time": statistics.mean(ts), "travel": sum(tr) / n,
            "measure": sum(meas) / n}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d" % (n, seeds[0], seeds[-1]))
    print("%-28s %8s %8s %5s %8s %8s %6s"
          % ("variant", "ratio", "min", "fails", "time", "travel", "meas"))
    out = []
    for tag, ov in VARIANTS:
        r = ev(ov, seeds)
        r["tag"] = tag
        out.append(r)
        print("%-28s %8.4f %8.4f %5d %8.1f %8.0f %6.0f"
              % (tag, r["ratio"], r["min"], r["fails"], r["time"], r["travel"],
                 r["measure"]), flush=True)
    with open(os.path.join(DATA, "detect_min.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/detect_min.json")
