#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
margin_rim_scan.py -- 认证边距 × 贴边环规模：寻找"完整完成率 + 最少站位"的组合。

目前的最好结果（四池 120 例，按最差池判定）：
    s950 + 贴边环 16 + 边距 90 : 0.9978  623.2 s  28.9 站  1/120 失败
    s1100 + 贴边环 16 + 边距 90: 0.9978  645.7 s  24.5 站  1/120 失败
    s950 纯扫描（边距 900）    : 0.9803  515.1 s  12.9 站 21/120 失败

站位数 29 ≈ 13（认证所需的最小三角格点）+ 16（贴边环）。
要把时间压到 200~300 s，必须同时削减**行程**与**检测次数**，二者都正比于站位数。

认证边距的作用：它决定"必须认证到多远"。
    边距 90  -> 认证 r <= 1710（几乎全域），因此需要贴边环才能在边界附近完成认证；
    边距 900 -> 只认证 r <= 900，格点站位可大幅减少，但边界源的发现要靠贴边环。

本脚本扫描 (边距, 贴边环规模) 的组合，寻找"最差完成率仍 >= 0.99 且时间最低"的工作点。

usage: python margin_rim_scan.py [n_per_pool]
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


def cfg(spacing, rim_n, margin, rim_r=1750.0, budget=40):
    return dict(P4, survey_spacing=spacing, rim_ring_n=rim_n, rim_ring_r=rim_r,
                verify_margin=margin, max_search_stops=budget,
                periodic_cert_every=1, spread_stops=True, max_survey_stops=0,
                clear_bonus=500.0, locate_sigma=400.0)


CANDS = [
    ("s950 r12 m700", cfg(950.0, 12, 700.0)),
    ("s1100 r12 m700", cfg(1100.0, 12, 700.0)),
    ("s1300 r12 m700", cfg(1300.0, 12, 700.0)),
    ("s1500 r12 m700", cfg(1500.0, 12, 700.0)),
    ("s1100 r16 m700", cfg(1100.0, 16, 700.0)),
    ("s1300 r16 m700", cfg(1300.0, 16, 700.0)),
    ("s1300 r12 m900", cfg(1300.0, 12, 900.0)),
    ("s1500 r16 m900", cfg(1500.0, 16, 900.0)),
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
    with open(os.path.join(DATA, "margin_rim_scan.json"), "w",
              encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("report -> data/margin_rim_scan.json")
