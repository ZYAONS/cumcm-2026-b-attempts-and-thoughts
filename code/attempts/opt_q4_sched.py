#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""opt_q4_sched.py -- 问题四调度权重扫描。

我们与公开实现的差别集中在"动作多、行程少"：443 次检测 + 27 次清除（对方 287），
但行程 23.3 km（对方 24.9）。调度权重 clear_bonus / search_cost_bias 正是控制
这一取舍的旋钮：偏置越大越倾向"先清除"，偏置越小越倾向"先普查"。
"""
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import robot_core as rc
import simulator as sim
from make_data import P4


def run(params, n, seed0):
    ratio, times, trav, meas, clr = [], [], [], [], []
    for k in range(n):
        srcs = sim.make_case(random.Random(seed0 + k), kind_mix=0.5)
        arena = sim.Arena(srcs, seed=seed0 + k)
        cl = rc.LocalClient(arena)
        brain = rc.Brain(cl, params=params, seed=k)
        st = brain.run()
        st.update(arena.stats())
        arena.close()
        ratio.append(st["clear_ratio"])
        times.append(st["mean_time"] if st["n_cleared"] else 9000.0)
        trav.append(st["travel_m"])
        meas.append(st["n_measure"])
        clr.append(st["n_clear"])
    return (statistics.mean(ratio), min(ratio), sum(1 for r in ratio if r < 0.9999),
            statistics.mean(times), statistics.mean(trav), statistics.mean(meas),
            statistics.mean(clr))


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    b = dict(rc.DEFAULT_PARAMS); b.update(P4)
    variants = []
    for cb in (250.0, 350.0, 500.0):
        for scb in (0.0, 120.0, 300.0):
            variants.append(("clear_bonus=%.0f search_cost_bias=%.0f" % (cb, scb),
                             {"clear_bonus": cb, "search_cost_bias": scb}))
    agg = {}
    for seed0 in (30000, 12000):
        for tag, mod in variants:
            p = dict(b); p.update(mod)
            agg.setdefault(tag, []).append(run(p, n, seed0))
    print("问题四（%d 例 × 2 池）" % n)
    rows = []
    for tag, _ in variants:
        rs = agg[tag]
        rows.append((statistics.mean(x[3] for x in rs), tag,
                     statistics.mean(x[0] for x in rs), min(x[1] for x in rs),
                     sum(x[2] for x in rs), statistics.mean(x[4] for x in rs),
                     statistics.mean(x[5] for x in rs), statistics.mean(x[6] for x in rs)))
    rows.sort()
    for t, tag, ratio, worst, fails, trav, meas, clr in rows:
        print("  %-38s %6.1f s/源  完成率 %.4f (最差 %.3f 失败 %d)  行程 %6.0f  检测 %5.1f  清除 %4.1f"
              % (tag, t, ratio, worst, fails, trav, meas, clr), flush=True)


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
