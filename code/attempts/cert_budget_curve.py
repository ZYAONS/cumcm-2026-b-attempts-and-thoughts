#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cert_budget_curve.py -- 额外认证站位的预算 ↔ 完成率 ↔ 时间。

每例有约 18 个额外站位在为主扫描留下的未认证候选点服务。
主扫描（间距 1100 m，约 7~10 个站位）之后仍有大量候选点距离任何站位都超过
认证半径 958 m，因此认证必须靠额外站位补齐。

本实验把"允许的额外站位数量"扫一遍，看完成率与时间如何交换：
这是"能不能做到 500 s 以内"以及"代价是什么"的直接答案。

usage: python cert_budget_curve.py [n_cases] [seed0]
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

BUDGETS = [0, 2, 4, 8, 40]
SPACINGS = [1100.0, 900.0]


def evaluate(budget, spacing, seeds, mix=0.5):
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    p["survey_spacing"] = spacing
    p["max_search_stops"] = budget
    rs, ts, tr, stops = [], [], [], []
    t0 = time.time()
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=p, seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
        stops.append(len(br.visited_stops))
    n = float(len(seeds))
    return {"budget": budget, "spacing": spacing, "ratio": sum(rs) / n,
            "min": min(rs), "time": sum(ts) / n, "travel": sum(tr) / n,
            "stops": sum(stops) / n, "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d" % (n, seeds[0], seeds[-1]))
    print("%8s %8s %8s %8s %8s %8s %8s"
          % ("spacing", "budget", "ratio", "min", "time", "travel", "stops"))
    out = []
    for sp in SPACINGS:
        for b in BUDGETS:
            r = evaluate(b, sp, seeds)
            out.append(r)
            print("%8.0f %8d %8.4f %8.4f %8.1f %8.0f %8.1f"
                  % (r["spacing"], r["budget"], r["ratio"], r["min"], r["time"],
                     r["travel"], r["stops"]), flush=True)
        print()
    with open(os.path.join(DATA, "cert_budget_curve.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/cert_budget_curve.json")
