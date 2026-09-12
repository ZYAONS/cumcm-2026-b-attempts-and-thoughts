#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
relocate_budget.py -- relocate 的预算可能是一项隐藏的大开销。

当前设置 `relocate_deltas` 有 7 档、每档两侧，加上 `relocate_crawls=4`，
意味着一
个"始终拿不到第二条方位"的频道最多要跑 14+4 = 18 趟观测，
每趟往返数百米——**单频道可能就是上万米行程**。

本脚本扫描 relocate 的档位数与爬行次数，在保持完成率 1.0000 的前提下压缩行程。

usage: python relocate_budget.py [n_cases] [seed0]
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

BASE = dict(rc.DEFAULT_PARAMS)
BASE.update(P4)
BASE.update({"survey_spacing": 900.0, "max_search_stops": 0, "verify_margin": 900.0,
             "periodic_cert_every": 1, "spread_stops": True, "max_survey_stops": 0,
             "clear_bonus": 500.0, "locate_sigma": 400.0})

ALLD = [400.0, 250.0, 150.0, 90.0, 55.0, 33.0, 20.0]
VARIANTS = [
    ("levels 7 crawl 4 (now)", ALLD, 4),
    ("levels 5 crawl 2", ALLD[:5], 2),
    ("levels 4 crawl 1", ALLD[:4], 1),
    ("levels 3 crawl 1", ALLD[:3], 1),
    ("levels 7 crawl 0", ALLD, 0),
    ("levels 4 crawl 0", ALLD[:4], 0),
]


def ev(deltas, crawls, seeds):
    p = dict(BASE)
    p["relocate_deltas"] = list(deltas)
    p["relocate_crawls"] = crawls
    rs, ts, tr, loc = [], [], [], []
    t0 = time.time()
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=p, seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
        loc.append(st["task_travel"].get("localise", 0.0))
    n = float(len(seeds))
    return {"ratio": sum(rs) / n, "min": min(rs),
            "fails": sum(1 for r in rs if r < 0.9999),
            "time": statistics.mean(ts), "travel": sum(tr) / n,
            "localise": sum(loc) / n, "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("%d cases, seeds %d..%d" % (n, seeds[0], seeds[-1]))
    print("%-24s %8s %8s %6s %8s %8s %9s"
          % ("variant", "ratio", "min", "fails", "time", "travel", "localise"))
    out = []
    for tag, d, cr in VARIANTS:
        r = ev(d, cr, seeds)
        r["tag"] = tag
        out.append(r)
        print("%-24s %8.4f %8.4f %6d %8.1f %8.0f %9.0f"
              % (tag, r["ratio"], r["min"], r["fails"], r["time"], r["travel"],
                 r["localise"]), flush=True)
    with open(os.path.join(DATA, "relocate_budget.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    good = [r for r in out if r["fails"] == 0]
    if good:
        b = min(good, key=lambda r: r["time"])
        print("\nPERFECT and fastest: %s -> %.1f s/source" % (b["tag"], b["time"]))
    print("report -> data/relocate_budget.json")
