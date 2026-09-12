#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
coarse_plus_path.py -- "最粗格点保证发现 + 沿途测量完成认证"。

上一轮的失败诊断
----------------
自适应（取消格点）虽然更快（486~570 s），完成率却掉到 0.956~0.979。
原因是**自举失败**：入场普查只听到少量源 → 清除巡回很短 → 沿途测量覆盖不足
→ 发现更少 → 巡回更短。巡回的长度与发现率互相拖累。

修正：**用"刚好够发现"的最粗格点做保底**。
  * 全向源的发现只需覆盖半径 <= R_min = 1000 m，即间距
    s <= sqrt(3)*1000 = 1732 m，约 7 个站位就够（同心六边形）；
  * 而**认证**需要间距 <= 958 m（约 13 站）—— 但认证可以由
    **清除巡回沿途的测量**来补：巡回 8635 m、按 250 m 测量就是 35 个采样点，
    覆盖全城绰绰有余，而这段路的行程本来就是免费的。

所以最优结构可能是"**7 站保底发现 + 巡回沿途采样认证**"，
而不是现在"13 站格点 + 12 站贴边环 = 24.4 站"的重型普查。

本脚本扫描保底格点的间距。

usage: python coarse_plus_path.py [n_cases] [seed0]
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
             "relocate": True, "exhaustive_clear": True,
             "survey_mode": "lattice", "max_search_stops": 40,
             "max_survey_stops": 0, "spread_stops": True})

VARIANTS = [
    ("s950 rim12 (now)", {"survey_spacing": 950.0, "rim_ring_n": 12,
                          "probe_spacing": 650.0}),
    ("s1300 rim12 ps250", {"survey_spacing": 1300.0, "rim_ring_n": 12,
                           "probe_spacing": 250.0}),
    ("s1300 rim12 ps400", {"survey_spacing": 1300.0, "rim_ring_n": 12,
                           "probe_spacing": 400.0}),
    ("s1500 rim12 ps250", {"survey_spacing": 1500.0, "rim_ring_n": 12,
                           "probe_spacing": 250.0}),
    ("s1700 rim12 ps250", {"survey_spacing": 1700.0, "rim_ring_n": 12,
                           "probe_spacing": 250.0}),
    ("s1300 rim16 ps250", {"survey_spacing": 1300.0, "rim_ring_n": 16,
                           "probe_spacing": 250.0}),
    ("s1300 rim12 ps250 m90", {"survey_spacing": 1300.0, "rim_ring_n": 12,
                               "probe_spacing": 250.0, "verify_margin": 90.0}),
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
    print("%-24s %7s %8s %8s %6s %8s %8s %6s"
          % ("variant", "stops", "ratio", "min", "fails", "time", "travel",
             "meas"))
    out = []
    for tag, ov in VARIANTS:
        r = ev(ov, seeds)
        r["tag"] = tag
        out.append(r)
        print("%-24s %7.1f %8.4f %8.4f %6d %8.1f %8.0f %6.0f"
              % (tag, r["stops"], r["ratio"], r["min"], r["fails"], r["time"],
                 r["travel"], r["measure"]), flush=True)
    with open(os.path.join(DATA, "coarse_plus_path.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/coarse_plus_path.json")
