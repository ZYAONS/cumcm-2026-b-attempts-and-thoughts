#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
stop_cap_scan.py -- 在 s=900 的甜点上，把"扫描站位数量"截断到 12~19 个。

final_scan 的结果：
    s=750  487.6 s  完成率 0.9677
    s=900  516.0 s  完成率 0.9928      <- 甜点，但超 500 s
    s=950  493.2 s  完成率 0.9782
    s=1000 495.2 s  完成率 0.9729

s=900 的格点给出 18~19 个站位、完成率明显最好，只超出 500 s 约 16 s/源。
每少一个站位约省 1114 m 行程（223 s）与约 17 次检测（100 s），
折合约 26 s/源——所以截断到 16~17 个站位应当正好落到 500 s 以内。

本实验扫描站位上限，给出"500 s 以内可达到的最高完成率"。

usage: python stop_cap_scan.py [n_cases] [seed0]
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

CAPS = [10, 12, 14, 16, 17, 18, 19, 0]     # 0 = 不限制


def ev(cap, seeds, spacing=900.0):
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    p.update({"survey_spacing": spacing, "max_search_stops": 0,
              "verify_margin": 900.0, "periodic_cert_every": 1,
              "max_survey_stops": cap})
    rs, ts, tr, stops, meas = [], [], [], [], []
    t0 = time.time()
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=p, seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
        stops.append(len(br.visited_stops))
        meas.append(st["n_measure"])
    n = float(len(seeds))
    return {"cap": cap, "ratio": sum(rs) / n, "min": min(rs),
            "time": sum(ts) / n, "travel": sum(tr) / n,
            "stops": sum(stops) / n, "measure": sum(meas) / n,
            "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("spacing 900, pure sweep, %d cases; cap = max survey stops" % n)
    print("%6s %7s %8s %8s %8s %8s %8s"
          % ("cap", "stops", "ratio", "min", "time", "travel", "measure"))
    out = []
    for c in CAPS:
        r = ev(c, seeds)
        out.append(r)
        print("%6d %7.1f %8.4f %8.4f %8.1f %8.0f %8.0f"
              % (r["cap"], r["stops"], r["ratio"], r["min"], r["time"],
                 r["travel"], r["measure"]), flush=True)
    with open(os.path.join(DATA, "stop_cap_scan.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/stop_cap_scan.json")
