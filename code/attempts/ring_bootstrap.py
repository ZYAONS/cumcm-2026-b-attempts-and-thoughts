#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
ring_bootstrap.py -- 挑战"305 s 不可达"证明里最可疑的一环。

那条证明的关键前提是"必须访问 55.6 个点，其中 24.4 个是普查站位"。
但机器**本来就要走到 13 个源**——源的位置本身就是 13 个散布全城的采样点，
而且沿途按 probe_spacing 测量还会再产生一批。
也就是说：**认证所需的读数，可能大部分由"必须走的路"提供**，
普查站位不需要那么多。

此前"自适应采样"（完全取消格点）失败的原因是**自举失败**：
入场普查只听到朝向中心的源 → 清除巡回很短 → 沿途覆盖不足 → 发现更少。
但自举可以**用最少的站位保证**：全向源的发现只需覆盖半径 <= R_min = 1000 m，
而 6 个位于半径 rho 的环点 + 圆心，其覆盖半径是 rho*cos(30)，
故 rho*cos(30) <= 1000 即 rho <= 1155。取 rho = 1000~1150 即 7 个站位。

于是理想结构是：
    7 站环（保证发现）  ->  清除巡回（沿途测量，兼作认证）  ->  按需补认证站位
而不是现在的"13 格点 + 12 贴边环 = 24.4 站"。

usage: python ring_bootstrap.py [n_cases] [seed0]
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
BASE.update({"periodic_cert_every": 1, "clear_bonus": 350.0,
             "locate_sigma": 400.0, "relocate": True, "exhaustive_clear": True,
             "max_search_stops": 40, "max_survey_stops": 0, "spread_stops": True,
             "verify_margin": 700.0})

VARIANTS = [
    ("s950 rim12 (now)", {"survey_mode": "lattice", "survey_spacing": 950.0,
                          "rim_ring_n": 12, "probe_spacing": 650.0}),
    ("ring1250 rim0 ps250", {"survey_mode": "ring", "ring_radius": 1250.0,
                             "rim_ring_n": 0, "probe_spacing": 250.0}),
    ("ring1155 rim0 ps250", {"survey_mode": "ring", "ring_radius": 1155.0,
                             "rim_ring_n": 0, "probe_spacing": 250.0}),
    ("ring1000 rim0 ps250", {"survey_mode": "ring", "ring_radius": 1000.0,
                             "rim_ring_n": 0, "probe_spacing": 250.0}),
    ("ring1155 rim6 ps250", {"survey_mode": "ring", "ring_radius": 1155.0,
                             "rim_ring_n": 6, "probe_spacing": 250.0}),
    ("ring1155 rim12 ps250", {"survey_mode": "ring", "ring_radius": 1155.0,
                              "rim_ring_n": 12, "probe_spacing": 250.0}),
    ("s1300 rim0 ps250", {"survey_mode": "lattice", "survey_spacing": 1300.0,
                          "rim_ring_n": 0, "probe_spacing": 250.0}),
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
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d" % (n, seeds[0], seeds[-1]))
    print("%-22s %7s %8s %8s %6s %8s %8s %6s"
          % ("variant", "stops", "ratio", "min", "fails", "time", "travel",
             "meas"))
    out = []
    for tag, ov in VARIANTS:
        r = ev(ov, seeds)
        r["tag"] = tag
        out.append(r)
        print("%-22s %7.1f %8.4f %8.4f %6d %8.1f %8.0f %6.0f"
              % (tag, r["stops"], r["ratio"], r["min"], r["fails"], r["time"],
                 r["travel"], r["measure"]), flush=True)
    with open(os.path.join(DATA, "ring_bootstrap.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/ring_bootstrap.json")
