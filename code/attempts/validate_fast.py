#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
validate_fast.py -- 在独立算例池上验证"500 s 以内"的配置。

调参池：种子 30000--30019（20 例）  ->  498.1 s/源、完成率 0.9923
本脚本在**从未参与调参**的池子上复核：
    池 A 种子 62000--62039（40 例）
    池 B 种子 51000--51029（30 例）
并同时报告对照配置（原全认证搜索配置）在同一池上的结果。

usage: python validate_fast.py [n_cases]
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
from make_data import P4, P4_PERFECT  # noqa: E402

FAST = dict(P4)
FAST.update({"survey_spacing": 900.0, "max_search_stops": 0, "verify_margin": 900.0,
             "periodic_cert_every": 1, "spread_stops": True, "max_survey_stops": 14,
             "clear_bonus": 500.0, "probe_spacing": 2000.0, "locate_sigma": 400.0})

SAFE = dict(P4)          # the configuration the paper currently reports
PERFECT = dict(P4_PERFECT)   # 1.0000 completion at ~38 % less time


def ev(cfg, seeds, mix=0.5):
    rs, ts, tr = [], [], []
    t0 = time.time()
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
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
            "travel": sum(tr) / n, "missed": sum(
                1 for r in rs for _ in range(0)) or
            round(sum((1 - r) for r in rs) * 13, 1), "wall": time.time() - t0}


def show(tag, r):
    print("%-28s ratio=%.4f min=%.4f time=%7.1f median=%7.1f p90=%7.1f "
          "travel=%7.0f  (%.0f s)"
          % (tag, r["ratio"], r["min"], r["time"], r["median"], r["p90"],
             r["travel"], r["wall"]), flush=True)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    pools = [("A (62000+)", list(range(62000, 62000 + n))),
             ("B (51000+)", list(range(51000, 51000 + n)))]
    out = {}
    for name, seeds in pools:
        print("--- pool %s : %d cases" % (name, len(seeds)))
        a = ev(SAFE, seeds)
        show("   current (paper)", a)
        b = ev(FAST, seeds)
        show("   fast (<500 s target)", b)
        c = ev(PERFECT, seeds)
        show("   perfect (1.0000 target)", c)
        out[name] = {"current": a, "fast": b, "perfect": c}
        print("   delta: time %+.1f %%  ratio %+.4f"
              % (100.0 * (b["time"] / a["time"] - 1.0), b["ratio"] - a["ratio"]),
              flush=True)
    with open(os.path.join(DATA, "validate_fast.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/validate_fast.json")
