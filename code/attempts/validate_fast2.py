#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
validate_fast2.py -- 在独立池上寻找真正能稳定低于 500 s 的配置。

第一次独立验证（validate_fast.py）显示调参池上的 498.1 s 没有复现：
    池 A(62000+, 40 例)：538.9 s，中位数 501.4，完成率 0.9884
    池 B(51000+, 40 例)：597.0 s，中位数 550.1，完成率 0.9856
调参池（30000+, 20 例）偏易，因此必须以独立池为准。

本脚本在独立池上扫描"扫描站位上限"（12/10/8）与间距，
寻找**在独立池上也能稳定低于 500 s** 的工作点，并给出对应的完成率。

usage: python validate_fast2.py [n_cases]
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

BASE = dict(P4)
BASE.update({"max_search_stops": 0, "verify_margin": 900.0,
             "periodic_cert_every": 1, "spread_stops": True,
             "clear_bonus": 500.0, "probe_spacing": 2000.0, "locate_sigma": 400.0})

VARIANTS = [
    ("s900 cap14", {"survey_spacing": 900.0, "max_survey_stops": 14}),
    ("s900 cap12", {"survey_spacing": 900.0, "max_survey_stops": 12}),
    ("s900 cap10", {"survey_spacing": 900.0, "max_survey_stops": 10}),
    ("s1000 cap12", {"survey_spacing": 1000.0, "max_survey_stops": 12}),
    ("s1000 cap10", {"survey_spacing": 1000.0, "max_survey_stops": 10}),
    ("s1100 cap9", {"survey_spacing": 1100.0, "max_survey_stops": 9}),
]


def ev(ov, seeds):
    cfg = dict(BASE)
    cfg.update(ov)
    rs, ts, tr = [], [], []
    t0 = time.time()
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=dict(rc.DEFAULT_PARAMS, **cfg),
                      seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
    n = float(len(seeds))
    t = sorted(ts)
    return {"ratio": sum(rs) / n, "min": min(rs), "time": sum(ts) / n,
            "median": statistics.median(t), "p90": t[9 * len(t) // 10],
            "travel": sum(tr) / n, "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    pools = [("A(62k)", list(range(62000, 62000 + n))),
             ("B(51k)", list(range(51000, 51000 + n)))]
    print("%d cases per pool" % n)
    print("%-14s %-8s %8s %8s %8s %8s %8s"
          % ("variant", "pool", "ratio", "min", "time", "median", "p90"))
    out = []
    for tag, ov in VARIANTS:
        for pname, seeds in pools:
            r = ev(ov, seeds)
            r["tag"] = tag
            r["pool"] = pname
            out.append(r)
            mark = "  <== under 500 s" if r["time"] < 500.0 else ""
            print("%-14s %-8s %8.4f %8.4f %8.1f %8.1f %8.1f%s"
                  % (tag, pname, r["ratio"], r["min"], r["time"], r["median"],
                     r["p90"], mark), flush=True)
        print()
    with open(os.path.join(DATA, "validate_fast2.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    ok = [r for r in out if r["time"] < 500.0]
    if ok:
        b = max(ok, key=lambda r: r["ratio"])
        print("BEST UNDER 500 s on independent pools: %s %s -> ratio %.4f "
              "(min %.4f) time %.1f s"
              % (b["tag"], b["pool"], b["ratio"], b["min"], b["time"]))
    else:
        print("no configuration is under 500 s on BOTH independent pools")
    print("report -> data/validate_fast2.json")
