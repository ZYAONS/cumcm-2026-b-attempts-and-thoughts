#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pure_vs_search.py -- 在"完成率优先"的前提下，比较三种站位数配置。

背景：P4（论文配置）每例访问约 24 个站位，其中只有约 10 个是格点，
其余 14 个是认证搜索补出来的。而间距 900 m 的格点自身就有 18.4 个站位，
几何上已足以认证（候选点所在格点三角形的三个顶点都在认证半径 958 m 内）。
也就是说：**可能用更少的站位同时完成发现与认证**。

本脚本比较：
  A 论文配置      : s=1100 + 认证搜索不限
  B 纯扫描 s=900  : s=900，不做认证搜索
  C 纯扫描 s=1000 : s=1000，不做认证搜索
三种都带上本轮新增的 relocate（贴边定向）与 exhaustive（末段兜底），
因此完成率应当都不差——那就比时间。

usage: python pure_vs_search.py [n_cases] [seed0]
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
from make_data import P4  # noqa: E402

CONFIGS = [
    ("A paper (s1100 + search)", {}),
    ("B pure sweep s900", {"survey_spacing": 900.0, "max_search_stops": 0,
                           "verify_margin": 900.0, "periodic_cert_every": 1,
                           "spread_stops": True, "max_survey_stops": 0}),
    ("C pure sweep s1000", {"survey_spacing": 1000.0, "max_search_stops": 0,
                            "verify_margin": 900.0, "periodic_cert_every": 1,
                            "spread_stops": True, "max_survey_stops": 0}),
    ("D pure sweep s900 + cb500", {"survey_spacing": 900.0, "max_search_stops": 0,
                                   "verify_margin": 900.0, "periodic_cert_every": 1,
                                   "spread_stops": True, "max_survey_stops": 0,
                                   "clear_bonus": 500.0, "locate_sigma": 400.0}),
]


def ev(ov, seeds):
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
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
            "time": statistics.mean(ts), "median": statistics.median(ts),
            "travel": sum(tr) / n, "measure": sum(meas) / n,
            "stops": sum(stops) / n, "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d" % (n, seeds[0], seeds[-1]))
    print("%-28s %7s %8s %8s %8s %8s %8s %7s"
          % ("config", "stops", "ratio", "min", "time", "median", "travel",
             "measure"))
    out = []
    for tag, ov in CONFIGS:
        r = ev(ov, seeds)
        r["tag"] = tag
        out.append(r)
        print("%-28s %7.1f %8.4f %8.4f %8.1f %8.1f %8.0f %7.0f"
              % (tag, r["stops"], r["ratio"], r["min"], r["time"], r["median"],
                 r["travel"], r["measure"]), flush=True)
    with open(os.path.join(DATA, "pure_vs_search.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/pure_vs_search.json")
