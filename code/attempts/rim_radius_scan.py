#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
rim_radius_scan.py -- 贴边环的半径必须大于源的半径，否则永远发现不了"朝外"的源。

几何事实（此前一直被忽略）
--------------------------
设源在半径 rq 处、沿朝外径向 û 辐射。观测点 p 能听到它，当且仅当
    (p - q)·û >= 0   且   |p - q| <= R_eff
对朝外辐射（û 即径向），第一个条件在径向上要求 |p| >= rq —— 
也就是说**观测点必须比源更靠外**。

于是：**半径 1750 m 的贴边环永远听不到 r > 1750 且朝外的源**。
而源可以一直贴到 1800 m，所以环必须推到接近边界（1790+）才有意义。

这也解释了此前"贴边环有效但补不满"的现象：它只能覆盖 r < 1750 那一部分。

本脚本扫描环半径与个数。

usage: python rim_radius_scan.py [n_per_pool]
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


def cfg(rim_r, rim_n, spacing=950.0, margin=700.0):
    return dict(P4, survey_spacing=spacing, rim_ring_n=rim_n, rim_ring_r=rim_r,
                verify_margin=margin, max_search_stops=40,
                periodic_cert_every=1, spread_stops=True, max_survey_stops=0,
                clear_bonus=500.0, locate_sigma=400.0)


CANDS = [
    ("r1750 n12", cfg(1750.0, 12)),
    ("r1780 n12", cfg(1780.0, 12)),
    ("r1790 n12", cfg(1790.0, 12)),
    ("r1795 n12", cfg(1795.0, 12)),
    ("r1790 n16", cfg(1790.0, 16)),
    ("r1795 n16", cfg(1795.0, 16)),
    ("r1795 n20", cfg(1795.0, 20)),
    ("r1795 n24", cfg(1795.0, 24)),
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
        print("%-12s worst=%.4f  mean_time=%6.1f s  stops=%5.1f  failing=%2d/%d"
              % (tag, min(rs), statistics.mean(ts), statistics.mean(st), fl,
                 n * len(POOLS)), flush=True)
    with open(os.path.join(DATA, "rim_radius_scan.json"), "w",
              encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("report -> data/rim_radius_scan.json")
