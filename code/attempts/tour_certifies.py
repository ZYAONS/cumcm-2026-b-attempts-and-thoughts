#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tour_certifies.py -- 清除巡回本身能否完成认证？

下界核算（floor.py）：2-opt 巡回 8635 m = 1727 s、加上普查/检测/清除动作共
**188 s/源**。所以 200~300 s 的目标在原理上可达，问题全在"为了发现与认证
而额外付出的采样行程"。

而机器人**必须**走到 13 个源附近，这条巡回穿过全城；
若沿途持续测量，它本身就构成一次覆盖式的采样。
换句话说：**认证所需的读数，可能大部分可以由"本来就要走的路"免费提供。**

本实验检验这个假设：把"额外认证站位"的预算直接设为 0，
只靠普查 + 清除巡回沿途的测量，看认证能覆盖多少、完成率还剩多少。

usage: python tour_certifies.py [n_cases] [seed0]
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
BASE.update({"survey_mode": "adaptive", "periodic_cert_every": 1,
             "clear_bonus": 500.0, "locate_sigma": 400.0, "adaptive_batch": 1})

VARIANTS = [
    ("search0 probe400", {"max_search_stops": 0, "probe_spacing": 400.0,
                          "verify_margin": 90.0}),
    ("search0 probe800", {"max_search_stops": 0, "probe_spacing": 800.0,
                          "verify_margin": 90.0}),
    ("search0 probe200", {"max_search_stops": 0, "probe_spacing": 200.0,
                          "verify_margin": 90.0}),
    ("search2 probe400", {"max_search_stops": 2, "probe_spacing": 400.0,
                          "verify_margin": 90.0}),
    ("search4 probe400", {"max_search_stops": 4, "probe_spacing": 400.0,
                          "verify_margin": 90.0}),
]


def ev(ov, seeds):
    p = dict(BASE)
    p.update(ov)
    rs, ts, tr, meas, stops, unc = [], [], [], [], [], []
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
        unresolved = [c for c in br.channels
                      if br.status[c] not in ("cleared", "empty")]
        ok, uncov, flags = br.certification_scan(unresolved) if unresolved else \
            (True, [], {})
        unc.append(len(uncov))
    n = float(len(seeds))
    return {"ratio": sum(rs) / n, "min": min(rs),
            "fails": sum(1 for r in rs if r < 0.9999),
            "time": statistics.mean(ts), "travel": sum(tr) / n,
            "measure": sum(meas) / n, "stops": sum(stops) / n,
            "uncov": sum(unc) / n}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d ; adaptive, certification stops almost off"
          % (n, seeds[0], seeds[-1]))
    print("%-20s %8s %8s %5s %8s %7s %7s %6s %7s"
          % ("variant", "ratio", "min", "fails", "time", "travel", "measure",
             "stops", "uncov"))
    out = []
    for tag, ov in VARIANTS:
        r = ev(ov, seeds)
        r["tag"] = tag
        out.append(r)
        print("%-20s %8.4f %8.4f %5d %8.1f %7.0f %7.0f %6.1f %7.0f"
              % (tag, r["ratio"], r["min"], r["fails"], r["time"], r["travel"],
                 r["measure"], r["stops"], r["uncov"]), flush=True)
    with open(os.path.join(DATA, "tour_certifies.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/tour_certifies.json")
