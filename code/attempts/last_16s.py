#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
last_16s.py -- 在 s=900 纯扫描配置上省下最后 16 s/源。

该配置：18.4 个站位、21640 m 行程、352 次检测、516.0 s/源、完成率 0.9928。
时间构成（12 例实测均值）：探测行程 12642 m、清除行程 7642 m、补测行程 2370 m、
检测 352 次。站立巡回已经是 2-opt 质量（实际探测行程甚至小于同样站位的 2-opt 巡回）。

因此剩下的可调项只有三个：
  * clear_bonus   —— 清除任务的排序权重（当前 0：完全按距离排）
  * probe_spacing —— 行进途中的机会式补测间隔（每次补测都是 20 次检测）
  * locate_sigma  —— 进入清除阶段的不确定度门槛（影响清除行程）

本脚本把它们扫一遍，看能否在保持 0.99 以上完成率的同时进入 500 s。

usage: python last_16s.py [n_cases] [seed0]
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
BASE.update({"survey_spacing": 900.0, "max_search_stops": 0,
             "verify_margin": 900.0, "periodic_cert_every": 1})

VARIANTS = [
    ("nominal", {}),
    ("clear_bonus 200", {"clear_bonus": 200.0}),
    ("clear_bonus 500", {"clear_bonus": 500.0}),
    ("probe_spacing 1200", {"probe_spacing": 1200.0}),
    ("probe_spacing 2000", {"probe_spacing": 2000.0}),
    ("locate_sigma 400", {"locate_sigma": 400.0}),
    ("locate_sigma 150", {"locate_sigma": 150.0}),
    ("cb200 + ps2000", {"clear_bonus": 200.0, "probe_spacing": 2000.0}),
    ("cb500 + ps2000 + ls400", {"clear_bonus": 500.0, "probe_spacing": 2000.0,
                                "locate_sigma": 400.0}),
]


def ev(ov, seeds):
    p = dict(BASE)
    p.update(ov)
    rs, ts, tr, meas, stops = [], [], [], [], []
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
        stops.append(len(br.visited_stops))
    n = float(len(seeds))
    return {"tag": None, "ratio": sum(rs) / n, "min": min(rs),
            "time": sum(ts) / n, "travel": sum(tr) / n,
            "measure": sum(meas) / n, "stops": sum(stops) / n,
            "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d, s=900 pure sweep" % (n, seeds[0], seeds[-1]))
    print("%-26s %8s %8s %8s %8s %8s"
          % ("variant", "ratio", "min", "time", "travel", "measure"))
    out = []
    for tag, ov in VARIANTS:
        r = ev(ov, seeds)
        r["tag"] = tag
        out.append(r)
        mark = "  <== under 500 s" if r["time"] < 500.0 else ""
        print("%-26s %8.4f %8.4f %8.1f %8.0f %8.0f%s"
              % (tag, r["ratio"], r["min"], r["time"], r["travel"], r["measure"],
                 mark), flush=True)
    with open(os.path.join(DATA, "last_16s.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    ok = [r for r in out if r["time"] < 500.0]
    if ok:
        b = max(ok, key=lambda r: r["ratio"])
        print("\nBEST UNDER 500 s: %s -> %.4f at %.1f s (min %.4f)"
              % (b["tag"], b["ratio"], b["time"], b["min"]))
    print("report -> data/last_16s.json")
