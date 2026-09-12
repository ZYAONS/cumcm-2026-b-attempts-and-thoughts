#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
spread_scan.py -- 用最远点采样排序后，重新扫描"扫描站位上限"。

目标：在 500 s 以内取得尽可能高的完成率。
基线（s=900、半径排序、不截断）：516.0 s、完成率 0.9928。
s=950（13 站）：493.2 s、0.9782。

最远点采样应当让"截断到 14~16 个站位"保留完整覆盖，
从而在 500 s 以内取得高于 0.9782 的完成率。

usage: python spread_scan.py [n_cases] [seed0]
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


def ev(spacing, cap, seeds, extra=None):
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    p.update({"survey_spacing": spacing, "max_search_stops": 0,
              "verify_margin": 900.0, "periodic_cert_every": 1,
              "spread_stops": True, "max_survey_stops": cap,
              "clear_bonus": 500.0, "probe_spacing": 2000.0,
              "locate_sigma": 400.0})
    if extra:
        p.update(extra)
    rs, ts, tr, stops = [], [], [], []
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
    n = float(len(seeds))
    return {"spacing": spacing, "cap": cap, "ratio": sum(rs) / n, "min": min(rs),
            "time": sum(ts) / n, "travel": sum(tr) / n,
            "stops": sum(stops) / n, "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d, farthest-point ordered survey" % (n, seeds[0],
                                                                     seeds[-1]))
    print("%8s %6s %7s %8s %8s %8s %8s"
          % ("spacing", "cap", "stops", "ratio", "min", "time", "travel"))
    out = []
    for sp in (900.0, 850.0, 800.0):
        for cap in (12, 14, 15, 16, 18, 0):
            r = ev(sp, cap, seeds)
            r["tag"] = "s%.0f/cap%d" % (sp, cap)
            out.append(r)
            mark = "  <== under 500 s" if r["time"] < 500.0 else ""
            print("%8.0f %6d %7.1f %8.4f %8.4f %8.1f %8.0f%s"
                  % (sp, cap, r["stops"], r["ratio"], r["min"], r["time"],
                     r["travel"], mark), flush=True)
        print()
    with open(os.path.join(DATA, "spread_scan.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    ok = [r for r in out if r["time"] < 500.0]
    if ok:
        b = max(ok, key=lambda r: r["ratio"])
        print("BEST UNDER 500 s: %s -> ratio %.4f (min %.4f) at %.1f s"
              % (b["tag"], b["ratio"], b["min"], b["time"]))
    print("report -> data/spread_scan.json")
