#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sparse_plus_rim.py -- 13 站格点 + 少量贴边环：能否在 500 s 附近拿到 0.99+。

离线几何结论（ring_design.py）：
    纯环组最多只认证 88.6% 的候选点（环上点角度太稀疏，无法从各方向包围），
    **三角格点才是认证的正确结构**：间距 s <= 认证半径 958 m 时，
    任意候选点所在格点三角形的三个顶点都在半径内且包围它。
    所需站位数 = pi*1800^2/(0.866*958^2) = 12.8 ≈ 13。

实测也印证：s=950 的纯扫描正好是 12.9 站、515.1 s。
但它的最差完成率只有 0.9803（120 例 21 例失败），
失败原因是**贴边朝外的定向源没被听到**（其域内受光区是薄月牙）。

因此最优结构应当是：**13 站密格点（保证认证）+ 少量贴边站位（保证发现边界源）**。
本脚本扫描这个组合。

usage: python sparse_plus_rim.py [n_per_pool]
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

POOLS = [("A", 62000), ("B", 51000), ("C", 12000), ("D", 30000)]


def cfg(spacing, rim_n, rim_r=1750.0, budget=0):
    return dict(P4, survey_spacing=spacing, rim_ring_n=rim_n, rim_ring_r=rim_r,
                max_search_stops=budget, verify_margin=900.0,
                periodic_cert_every=1, spread_stops=True, max_survey_stops=0,
                clear_bonus=500.0, locate_sigma=400.0)


CANDS = [
    ("s950 rim0", cfg(950.0, 0)),
    ("s950 rim4", cfg(950.0, 4)),
    ("s950 rim6", cfg(950.0, 6)),
    ("s950 rim8", cfg(950.0, 8)),
    ("s950 rim12", cfg(950.0, 12)),
    ("s950 rim6 r1650", cfg(950.0, 6, 1650.0)),
    ("s950 rim8 r1650", cfg(950.0, 8, 1650.0)),
    ("s900 rim6", cfg(900.0, 6)),
]


def ev(c, seeds):
    p = dict(rc.DEFAULT_PARAMS)
    p.update(c)
    rs, ts, stops = [], [], []
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=p, seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        stops.append(len(br.visited_stops))
    return {"ratio": sum(rs) / len(rs), "min": min(rs),
            "fails": sum(1 for r in rs if r < 0.9999),
            "time": statistics.mean(ts), "stops": sum(stops) / len(seeds)}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    res = {}
    for tag, c in CANDS:
        rs, ts, fl, st = [], [], 0, []
        for pname, s0 in POOLS:
            r = ev(c, list(range(s0, s0 + n)))
            rs.append(r["ratio"])
            ts.append(r["time"])
            fl += r["fails"]
            st.append(r["stops"])
        res[tag] = {"worst": min(rs), "time": statistics.mean(ts), "fails": fl,
                    "stops": statistics.mean(st), "per_pool": rs}
        print("%-16s worst=%.4f  mean_time=%6.1f s  stops=%5.1f  failing=%2d/%d"
              % (tag, min(rs), statistics.mean(ts), statistics.mean(st), fl,
                 n * len(POOLS)), flush=True)
    with open(os.path.join(DATA, "sparse_plus_rim.json"), "w",
              encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("report -> data/sparse_plus_rim.json")
