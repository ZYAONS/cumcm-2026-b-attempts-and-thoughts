#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ab_relocate.py -- 论文配置下，relocate 与穷举兜底的净收益（四池联合）。

本轮新增的两个机制：
  * relocate  ：只有一条方位的频道，用"横向偏移二分 + 沿射线爬行"拿第二条方位；
  * exhaustive：已定位但反复清不掉的源，在 σ 圆盘上做 <=15 m 间距的穷举清除。
两者都只影响**正确性路径**，理论上不改变正常算例的行为。

本脚本在四个池上 A/B，并列出仍然失败的算例。

usage: python ab_relocate.py [n_per_pool]
"""
import json
import math
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

POOLS = [("A", 62000), ("B", 51000), ("C", 12000), ("D", 30000)]


def run(seeds, ov):
    cfg = dict(P4)
    cfg.update(ov)
    rs, ts, missed = [], [], []
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=dict(rc.DEFAULT_PARAMS, **cfg),
                      seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        for s in srcs:
            if not s.cleared:
                missed.append((sd, s.channel, round(math.hypot(s.x, s.y)),
                               s.kind, None if s.direction is None
                               else round(s.direction), round(s.r_eff),
                               br.status.get(s.channel),
                               len(br.obs.get(s.channel, []))))
    return {"ratio": statistics.mean(rs), "min": min(rs),
            "fails": sum(1 for r in rs if r < 0.9999),
            "time": statistics.mean(ts), "missed": missed,
            "n_src": sum(1 for _ in seeds)}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    both = {"relocate": True, "exhaustive_clear": True, "hard_attempt_cap": 24}
    off = {"relocate": False, "exhaustive_clear": False}
    for tag, ov in (("OFF (before this round)", off), ("ON  (this round)", both)):
        tot_m, tot_s, fails, times = [], 0, 0, []
        for pname, s0 in POOLS:
            seeds = list(range(s0, s0 + n))
            r = run(seeds, ov)
            print("%-24s pool %s: ratio=%.4f min=%.4f fails=%2d time=%7.1f  "
                  "missed %d" % (tag, pname, r["ratio"], r["min"], r["fails"],
                                 r["time"], len(r["missed"])), flush=True)
            tot_m += r["missed"]
            fails += r["fails"]
            times.append(r["time"])
        print("   --> %-20s total missed %d sources, %d failing cases, "
              "mean time %.1f s" % (tag, len(tot_m), fails,
                                    statistics.mean(times)), flush=True)
        if tot_m and tag.startswith("ON"):
            for m in tot_m:
                print("       still missed: seed %d ch %d r=%d %s dir=%s R_eff=%d "
                      "status=%s obs=%d" % m)
        print()
