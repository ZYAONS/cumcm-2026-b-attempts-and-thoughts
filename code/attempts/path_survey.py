#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
path_survey.py -- 让"清除巡回"兼任普查：取消固定格点，让沿途测量完成发现与认证。

下界核算里最弱的一个假设是"13 个认证站位必须独立于清除巡回"。
但清除巡回本身要走 8635 m 穿越全城；若**每隔 250 m 测量一次**，
那就是 35 个散布在全域的采样点 —— 认证所需的"三向环绕读数"很可能已经够了，
而这些点的**行程是本来就是免费的**（那段路无论如何都要走）。

实测线索：自适应 batch8 曾给出 **474.1 s**（最快的记录），但完成率只有 0.9609。
本轮的目标就是**把它的完成率补回来**，同时保住 474 s 这个量级。

补完成率的三件工具：
  1. **贴边环**（12 点 @1750）——自适应模式此前没有它，而边界源的发现正需要它；
  2. **认证边距 700**——只要求认证到 r<=1100，避免为"不可认证的贴边候选点"白跑；
  3. **relocate + exhaustive**——单条方位的频道与清不掉的源。

usage: python path_survey.py [n_cases] [seed0]
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
BASE.update({"verify_margin": 700.0, "periodic_cert_every": 1,
             "clear_bonus": 500.0, "locate_sigma": 400.0,
             "relocate": True, "exhaustive_clear": True})

VARIANTS = [
    ("lattice s950 rim12 (now)", {"survey_mode": "lattice", "survey_spacing": 950.0,
                                  "rim_ring_n": 12, "max_search_stops": 40,
                                  "probe_spacing": 650.0}),
    ("path batch4 rim12", {"survey_mode": "adaptive", "adaptive_batch": 4,
                           "rim_ring_n": 12, "max_search_stops": 40,
                           "probe_spacing": 250.0}),
    ("path batch8 rim12", {"survey_mode": "adaptive", "adaptive_batch": 8,
                           "rim_ring_n": 12, "max_search_stops": 40,
                           "probe_spacing": 250.0}),
    ("path batch8 rim12 ps400", {"survey_mode": "adaptive", "adaptive_batch": 8,
                                 "rim_ring_n": 12, "max_search_stops": 40,
                                 "probe_spacing": 400.0}),
    ("path batch8 rim16 ps250", {"survey_mode": "adaptive", "adaptive_batch": 8,
                                 "rim_ring_n": 16, "max_search_stops": 40,
                                 "probe_spacing": 250.0}),
    ("path batch12 rim12 ps250", {"survey_mode": "adaptive", "adaptive_batch": 12,
                                  "rim_ring_n": 12, "max_search_stops": 40,
                                  "probe_spacing": 250.0}),
]


def ev(ov, seeds):
    p = dict(BASE)
    p.update(ov)
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
    n = float(len(seeds))
    return {"ratio": sum(rs) / n, "min": min(rs),
            "fails": sum(1 for r in rs if r < 0.9999),
            "time": statistics.mean(ts), "travel": sum(tr) / n,
            "measure": sum(meas) / n, "stops": sum(stops) / n}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d" % (n, seeds[0], seeds[-1]))
    print("%-26s %7s %8s %8s %6s %8s %8s %6s"
          % ("variant", "stops", "ratio", "min", "fails", "time", "travel",
             "meas"))
    out = []
    for tag, ov in VARIANTS:
        r = ev(ov, seeds)
        r["tag"] = tag
        out.append(r)
        print("%-26s %7.1f %8.4f %8.4f %6d %8.1f %8.0f %6.0f"
              % (tag, r["stops"], r["ratio"], r["min"], r["fails"], r["time"],
                 r["travel"], r["measure"]), flush=True)
    with open(os.path.join(DATA, "path_survey.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/path_survey.json")
