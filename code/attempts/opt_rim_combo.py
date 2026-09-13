#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""opt_rim_combo.py -- 组合拳：域外贴边环 + 砍掉外圈格点。

上一轮结论：域外 r=1900 的 8 点环在 60 例上完成率 1.0000、零失败（基线域内 1750/12
有 1 例失败）。域外环补上的正是"r>1750 的贴边朝外源"这个缺口 —— 而这恰好是此前
`survey_max_r<=1500`（砍掉 r=1645 那圈 6 个格点）导致完成率掉到 0.9924 的原因。
因此两者组合起来有望同时减站、减动作、并保持完成率。
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
    ratio, times, trav, meas, clr, stops, act = [], [], [], [], [], [], []
    for k in range(n):
        srcs = sim.make_case(random.Random(seed0 + k), kind_mix=0.5)
        arena = sim.Arena(srcs, seed=seed0 + k)
        cl = rc.LocalClient(arena)
        brain = rc.Brain(cl, params=params, seed=k)
        st = brain.run()
        st.update(arena.stats())
        stops.append(len(brain.visited_stops))
        arena.close()
        ratio.append(st["clear_ratio"])
        times.append(st["mean_time"] if st["n_cleared"] else 9000.0)
        trav.append(st["travel_m"])
        meas.append(st["n_measure"])
        clr.append(st["n_clear"])
        act.append(st["n_measure"] + st["n_clear"])
    return (statistics.mean(ratio), min(ratio), sum(1 for r in ratio if r < 0.9999),
            statistics.mean(times), statistics.mean(trav), statistics.mean(meas),
            statistics.mean(clr), statistics.mean(stops), statistics.mean(act))


VARIANTS = [
    ("基线 域内1750/12 格点全", {}),
    ("域外1900/8 格点全", {"rim_ring_r": 1900.0, "rim_ring_n": 8}),
    ("域外1900/8 格点<=1500", {"rim_ring_r": 1900.0, "rim_ring_n": 8,
                              "survey_max_r": 1500.0}),
    ("域外1900/8 格点<=1300", {"rim_ring_r": 1900.0, "rim_ring_n": 8,
                              "survey_max_r": 1300.0}),
    ("域外1900/10 格点<=1500", {"rim_ring_r": 1900.0, "rim_ring_n": 10,
                               "survey_max_r": 1500.0}),
    ("域内1750/12 格点<=1500（旧失败例）", {"survey_max_r": 1500.0}),
]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    b = dict(rc.DEFAULT_PARAMS); b.update(P4)
    agg = {}
    for seed0, pname in ((30000, "池A"), (12000, "池B"), (70000, "池C")):
        for tag, mod in VARIANTS:
            p = dict(b); p.update(mod)
            r = run(p, n, seed0)
            agg.setdefault(tag, []).append(r)
            print("  %s %-28s 完成率 %.4f 失败 %d  %6.1f s/源 行程 %6.0f 动作 %5.1f 站位 %5.1f"
                  % (pname, tag, r[0], r[2], r[3], r[4], r[8], r[7]), flush=True)
    print()
    print("三池汇总（%d 例/池，共 %d 例）" % (n, n * 3))
    rows = []
    for tag, _ in VARIANTS:
        rs = agg[tag]
        rows.append((statistics.mean(x[3] for x in rs), tag,
                     statistics.mean(x[0] for x in rs), min(x[1] for x in rs),
                     sum(x[2] for x in rs), statistics.mean(x[7] for x in rs),
                     statistics.mean(x[8] for x in rs), statistics.mean(x[4] for x in rs)))
    rows.sort()
    for t, tag, ratio, worst, fails, stops, act, trav in rows:
        print("  %-28s %6.1f s/源  完成率 %.4f (最差 %.3f 失败 %d)  站位 %5.1f  动作 %5.1f  行程 %6.0f"
              % (tag, t, ratio, worst, fails, stops, act, trav))


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
