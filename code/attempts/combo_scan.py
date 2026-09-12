#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
combo_scan.py -- 组合搜索：格点间距 × 贴边环 × 认证搜索预算。

已测得的关键事实（四池 120 例，按最差池判定）：
    P4（s1100 + 认证搜索，无贴边环）      最差 0.9978   880.7 s
    P4 + 贴边环 12                        最差 0.9978   753.1 s
    P4 + 贴边环 16                        最差 0.9978   **650.5 s**
    P4 + 贴边环 20/24                     最差 0.9974/0.9972  666/682 s（变差）

贴边环为什么能大幅省时？因为**边界候选点最难认证**——要认证 r≈1780 的候选点，
必须在边界附近、从多个方位取读数，认证搜索为此外出很多趟、每趟只认证很少的点。
预先按环布站把这些点一次认证掉，就省下了那些昂贵的自适应站位；而且环是
规划好的，能被 2-opt 排出好路线。

那么同一个道理应当也适用于"格点间距不足"造成的昂贵补站：
    s=1100 时格点不满足"三维环绕"，认证搜索要补 17 站；
    s≤958 时格点自身即可认证，补站为 0（但格点站位更多）。
本脚本把这三者（间距、贴边环、搜索预算）联合扫描，寻找最优组合。

usage: python combo_scan.py [n_per_pool]
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


def cfg(spacing, rim_n, budget, rim_r=1750.0):
    return dict(P4, survey_spacing=spacing, rim_ring_n=rim_n, rim_ring_r=rim_r,
                max_search_stops=budget, verify_margin=90.0,
                periodic_cert_every=1, spread_stops=True, max_survey_stops=0,
                clear_bonus=500.0, locate_sigma=400.0)


CANDS = [
    ("s1100 rim16 b40", cfg(1100.0, 16, 40)),
    ("s1100 rim16 b12", cfg(1100.0, 16, 12)),
    ("s1100 rim16 b6", cfg(1100.0, 16, 6)),
    ("s1000 rim16 b40", cfg(1000.0, 16, 40)),
    ("s950 rim16 b40", cfg(950.0, 16, 40)),
    ("s900 rim16 b40", cfg(900.0, 16, 40)),
    ("s1000 rim16 b0", cfg(1000.0, 16, 0)),
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
        res[tag] = {"worst": min(rs), "time": statistics.mean(ts),
                    "fails": fl, "stops": statistics.mean(st),
                    "per_pool": rs}
        print("%-18s worst=%.4f  mean_time=%6.1f s  stops=%5.1f  failing=%2d/%d"
              % (tag, min(rs), statistics.mean(ts), statistics.mean(st), fl,
                 n * len(POOLS)), flush=True)
    with open(os.path.join(DATA, "combo_scan.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("report -> data/combo_scan.json")
