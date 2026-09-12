#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
multi_pool.py -- 在四个独立池上同时验证候选配置，按"最差池"选型。

本轮教训：单一池选型会**双向误导**——
    调参池（30000+）上 s=900 最好（1.0000 / 540.3），s=1000 只有 0.9831；
    独立池 A（62000+）上恰好相反：s=1000 是 1.0000 / 539.3，s=900 只有 0.9928。
所以最终选型必须看**多个池的汇总**，并以**最差池**为准（保守）。

usage: python multi_pool.py [n_per_pool]
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
from make_data import P4, P4_PERFECT  # noqa: E402

POOLS = [("A", 62000), ("B", 51000), ("C", 12000), ("D", 30000)]

CANDS = [
    ("rim12 (now)", dict(P4)),
    ("rim6", dict(P4, rim_ring_n=6, probe_spacing=250.0)),
    ("rim8", dict(P4, rim_ring_n=8, probe_spacing=250.0)),
    ("rim6 ps650", dict(P4, rim_ring_n=6)),
    ("rim4", dict(P4, rim_ring_n=4, probe_spacing=250.0)),
]


def ev(cfg, seeds):
    p = dict(rc.DEFAULT_PARAMS)
    p.update(cfg)
    rs, ts = [], []
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=p, seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
    return {"ratio": sum(rs) / len(rs), "min": min(rs),
            "fails": sum(1 for r in rs if r < 0.9999),
            "time": statistics.mean(ts), "median": statistics.median(ts),
            "n": len(seeds)}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    res = {}
    for tag, cfg in CANDS:
        res[tag] = {}
        for pname, s0 in POOLS:
            seeds = list(range(s0, s0 + n))
            r = ev(cfg, seeds)
            res[tag][pname] = r
            print("%-12s pool %s : ratio=%.4f min=%.4f fails=%2d time=%7.1f "
                  "median=%7.1f" % (tag, pname, r["ratio"], r["min"], r["fails"],
                                    r["time"], r["median"]), flush=True)
        rs = [res[tag][p]["ratio"] for p, _ in POOLS]
        ts = [res[tag][p]["time"] for p, _ in POOLS]
        fl = sum(res[tag][p]["fails"] for p, _ in POOLS)
        print("   --> %-12s over 4 pools: worst ratio %.4f  mean time %.1f  "
              "total failing cases %d/%d" % (tag, min(rs), statistics.mean(ts),
                                             fl, n * len(POOLS)), flush=True)
        print()
    with open(os.path.join(DATA, "multi_pool.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("report -> data/multi_pool.json")
