#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
rim_min.py -- 贴边环到底需要几个点？它是 12 站 ≈ 110 s/源的成本。

时间预算分解（问题四，13.1 个源/例）：
    行程 23323 m = 4665 s（61%）   检测 443 次 = 2658 s（35%）
    其中探测任务 24.4 站（13 格点 + 12 贴边环）

要压到 300 s/源，必须把站位数从 24.4 降下来。
贴边环的 12 个点是"边界源发现"专用的；若能用更少的点达到同样的发现率，
或者让认证搜索按需补（只在真正需要的地方去），就能省下可观的行程。

本脚本扫描贴边环点数 0/2/4/6/8/12，配合更细的沿途测量（probe_spacing 250），
看"少布环 + 沿路采样"能否替代"多布环"。

usage: python rim_min.py [n_cases] [seed0]
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
BASE.update({"survey_spacing": 950.0, "verify_margin": 700.0,
             "periodic_cert_every": 1, "clear_bonus": 500.0,
             "locate_sigma": 400.0, "relocate": True, "exhaustive_clear": True,
             "max_search_stops": 40, "max_survey_stops": 0, "spread_stops": True})

VARIANTS = [
    ("rim12 ps650 (now)", {"rim_ring_n": 12, "probe_spacing": 650.0}),
    ("rim12 ps250", {"rim_ring_n": 12, "probe_spacing": 250.0}),
    ("rim8 ps250", {"rim_ring_n": 8, "probe_spacing": 250.0}),
    ("rim6 ps250", {"rim_ring_n": 6, "probe_spacing": 250.0}),
    ("rim4 ps250", {"rim_ring_n": 4, "probe_spacing": 250.0}),
    ("rim2 ps250", {"rim_ring_n": 2, "probe_spacing": 250.0}),
    ("rim0 ps250", {"rim_ring_n": 0, "probe_spacing": 250.0}),
    ("rim0 ps250 m400", {"rim_ring_n": 0, "probe_spacing": 250.0,
                         "verify_margin": 400.0}),
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
    print("%-20s %7s %8s %8s %6s %8s %8s %6s"
          % ("variant", "stops", "ratio", "min", "fails", "time", "travel",
             "meas"))
    out = []
    for tag, ov in VARIANTS:
        r = ev(ov, seeds)
        r["tag"] = tag
        out.append(r)
        print("%-20s %7.1f %8.4f %8.4f %6d %8.1f %8.0f %6.0f"
              % (tag, r["stops"], r["ratio"], r["min"], r["fails"], r["time"],
                 r["travel"], r["measure"]), flush=True)
    with open(os.path.join(DATA, "rim_min.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/rim_min.json")
