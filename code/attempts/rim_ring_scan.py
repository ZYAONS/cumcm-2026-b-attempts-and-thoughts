#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
rim_ring_scan.py -- 贴边环的规模扫描（四池联合，按最差池判定）。

要在"完成率完整"与"少用时间"之间取得真正可用的折中，
唯一还没试过的结构性手段就是**用少量贴边站位专门覆盖"朝外定向源"**。

候选：
    s1000 纯扫描 + 贴边环 n = 0 / 6 / 9 / 12 / 16（r = 1750 m）
    s1100 纯扫描 + 贴边环 n = 12 / 16
参照：
    P4（论文，24 站）  最差 0.9978  880.7 s  1/120 失败
    s1000 纯扫描       最差 0.9833  533.8 s 14/120 失败

usage: python rim_ring_scan.py [n_per_pool]
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

POOLS = [("A", 62000), ("B", 51000), ("C", 12000), ("D", 30000)]


def cfg(spacing, rim_n, rim_r=1750.0):
    return dict(P4, survey_spacing=spacing, max_search_stops=0,
                verify_margin=900.0, periodic_cert_every=1, spread_stops=True,
                max_survey_stops=0, clear_bonus=500.0, locate_sigma=400.0,
                rim_ring_n=rim_n, rim_ring_r=rim_r)


CANDS = [
    ("s1000 rim0", cfg(1000.0, 0)),
    ("s1000 rim6", cfg(1000.0, 6)),
    ("s1000 rim9", cfg(1000.0, 9)),
    ("s1000 rim12", cfg(1000.0, 12)),
    ("s1000 rim16", cfg(1000.0, 16)),
    ("s1100 rim12", cfg(1100.0, 12)),
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
        res[tag] = {}
        for pname, s0 in POOLS:
            seeds = list(range(s0, s0 + n))
            r = ev(c, seeds)
            res[tag][pname] = r
        rs = [res[tag][p]["ratio"] for p, _ in POOLS]
        ts = [res[tag][p]["time"] for p, _ in POOLS]
        fl = sum(res[tag][p]["fails"] for p, _ in POOLS)
        st = statistics.mean([res[tag][p]["stops"] for p, _ in POOLS])
        print("%-12s worst ratio %.4f  mean time %7.1f  stops %5.1f  failing %2d/%d"
              "   [per pool: %s]"
              % (tag, min(rs), statistics.mean(ts), st, fl, n * len(POOLS),
                 " ".join("%.3f" % x for x in rs)), flush=True)
    with open(os.path.join(DATA, "rim_ring_scan.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("report -> data/rim_ring_scan.json")
