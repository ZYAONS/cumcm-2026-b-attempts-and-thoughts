#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
push_under_500.py -- 把 s=900、纯扫描、margin 500 的 527 s/源 压到 500 s 以内。

已知的余量（12 例实测）：
    实际行程 21966 m，同样站位的 NN 巡回 20026 m，2-opt 巡回 16200 m
    即 2-opt 质量的路由可省约 5766 m ≈ 1153 s ≈ 92 s/源
以及若干小项：
    * 入场普查 20 个频道 ≈ 119 s/例 ≈ 9.5 s/源
    * 认证评估频率（每 2 站 → 每站）
    * 认证边距（350 → 900：候选点更少，认证更快成立）

本脚本把这几项逐个叠加，看哪一个组合能真正落到 500 s 以内，
并同时报告完成率——目标是 500 s 以内且完成率不低于 0.99。

usage: python push_under_500.py [n_cases] [seed0]
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
BASE.update({"survey_spacing": 900.0, "max_search_stops": 0, "verify_margin": 500.0})

VARIANTS = [
    ("A baseline (sp900/m500)", {}),
    ("B + cert every stop", {"periodic_cert_every": 1}),
    ("C + no entry census", {"census": False}),
    ("D + margin 900", {"verify_margin": 900.0}),
    ("E + better tour", {"oropt_limit_batch": 60, "replan_mode": "each"}),
    ("F = B+C+D", {"periodic_cert_every": 1, "census": False,
                   "verify_margin": 900.0}),
    ("G = B+C+D+E", {"periodic_cert_every": 1, "census": False,
                     "verify_margin": 900.0, "oropt_limit_batch": 60}),
]


def ev(ov, seeds):
    p = dict(BASE)
    p.update(ov)
    rs, ts, tr, meas = [], [], [], []
    t0 = time.time()
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
    return {"ratio": sum(rs) / n, "min": min(rs), "time": sum(ts) / n,
            "travel": sum(tr) / n, "measure": sum(meas) / n,
            "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d, pure sweep at 900 m" % (n, seeds[0], seeds[-1]))
    print("%-26s %8s %8s %8s %8s %8s"
          % ("variant", "ratio", "min", "time", "travel", "measure"))
    out = []
    for tag, ov in VARIANTS:
        r = ev(ov, seeds)
        r["tag"] = tag
        out.append(r)
        print("%-26s %8.4f %8.4f %8.1f %8.0f %8.0f"
              % (tag, r["ratio"], r["min"], r["time"], r["travel"], r["measure"]),
              flush=True)
    with open(os.path.join(DATA, "push_under_500.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/push_under_500.json")
