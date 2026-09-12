#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
survey_cost_scan.py -- 普查行程 212 s/源 是最大单项，重扫"格点 × 贴边环"。

行程审计（10 例，本配置）：
    探测腿 22.8 段 × 581 m = 13246 m（60.7%）= 212 s/源   <- 普查
    清除腿 26.0 段 × 240 m =  6233 m（28.6%）= 100 s/源
    补测腿  5.9 段 × 396 m =  2336 m（10.7%）=  37 s/源
    合计 21815 m = 4363 s = **349 s/源**（还没算检测的 216 s/源）

要把总时间压到 300~400 s，必须把普查行程从 212 s/源 砍掉一半左右。
本站位集合 = 12.9 个格点（$s=950$）+ 12 个贴边环 = 24.5。

注意：此前几轮扫描时，"贴边环只在 lattice 分支生效"和"第二次调用丢失贴边环"
两个 bug 已经修好，因此**旧扫描结论需要用修正后的代码复核**。

usage: python survey_cost_scan.py [n_per_pool]
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

POOLS = [("A", 62000), ("B", 51000)]


def cfg(spacing, rim_n, rim_r=1750.0, margin=700.0, probe=400.0):
    return dict(P4, survey_mode="lattice", survey_spacing=spacing,
                rim_ring_n=rim_n, rim_ring_r=rim_r, verify_margin=margin,
                probe_spacing=probe, max_search_stops=40)


CANDS = [
    ("s950 rim12 (now)", cfg(950.0, 12)),
    ("s950 rim10", cfg(950.0, 10)),
    ("s950 rim8", cfg(950.0, 8)),
    ("s950 rim6", cfg(950.0, 6)),
    ("s1050 rim8", cfg(1050.0, 8)),
    ("s1050 rim10", cfg(1050.0, 10)),
    ("s1100 rim8", cfg(1100.0, 8)),
    ("s1100 rim10", cfg(1100.0, 10)),
    ("s950 rim8 m400", cfg(950.0, 8, margin=400.0)),
    ("s950 rim6 m400", cfg(950.0, 6, margin=400.0)),
]


def ev(c, seeds):
    p = dict(rc.DEFAULT_PARAMS)
    p.update(c)
    rs, ts, tr, meas, stops = [], [], [], [], []
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
    return {"ratio": statistics.mean(rs), "min": min(rs),
            "fails": sum(1 for r in rs if r < 0.9999),
            "time": statistics.mean(ts), "travel": statistics.mean(tr),
            "measure": statistics.mean(meas), "stops": statistics.mean(stops)}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    res = {}
    for tag, c in CANDS:
        acc = {"ratio": [], "time": [], "fails": 0, "stops": [], "travel": [],
               "measure": []}
        for pname, s0 in POOLS:
            r = ev(c, list(range(s0, s0 + n)))
            acc["ratio"].append(r["ratio"])
            acc["time"].append(r["time"])
            acc["stops"].append(r["stops"])
            acc["travel"].append(r["travel"])
            acc["measure"].append(r["measure"])
            acc["fails"] += r["fails"]
        res[tag] = {"worst": min(acc["ratio"]),
                    "time": statistics.mean(acc["time"]),
                    "fails": acc["fails"],
                    "stops": statistics.mean(acc["stops"]),
                    "travel": statistics.mean(acc["travel"]),
                    "measure": statistics.mean(acc["measure"])}
        print("%-18s worst=%.4f  time=%6.1f s  stops=%5.1f  travel=%6.0f  "
              "meas=%5.0f  failing=%d/%d"
              % (tag, res[tag]["worst"], res[tag]["time"], res[tag]["stops"],
                 res[tag]["travel"], res[tag]["measure"], res[tag]["fails"],
                 n * len(POOLS)), flush=True)
    with open(os.path.join(DATA, "survey_cost_scan.json"), "w",
              encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("report -> data/survey_cost_scan.json")
