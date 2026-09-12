#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""opt_q4_actions.py -- 问题四动作数压缩（我们 465 次 vs 公开实现 287 次）。

普查段 = 25 个站位 × 每站约 8 个未解算频道 ≈ 200 次检测。对方是 19 站 × 约 6 = 114。
可行的压缩方向：
  (a) 已经拿到两条好方位的频道不再重复测（probe_min_angle 提高）
  (b) 补测间隔拉长（probe_spacing）
  (c) 贴边环只在大站之外补测（rim_ring_n 已在上一轮否掉）
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
    variants = [
        ("baseline", {}),
        ("probe_min_angle 22->35", {"probe_min_angle": 35.0}),
        ("probe_min_angle 22->50", {"probe_min_angle": 50.0}),
        ("probe_spacing 650->1200", {"probe_spacing": 1200.0}),
        ("probe_spacing 650->350", {"probe_spacing": 350.0}),
        ("max_channels_probe 20->12", {"max_channels_probe": 12}),
    ]
    agg = {}
    for seed0 in (30000, 12000):
        for tag, mod in variants:
            p = dict(b); p.update(mod)
            agg.setdefault(tag, []).append(run(p, n, seed0))
    print("问题四（%d 例 × 2 池）" % n)
    for tag, _ in variants:
        rs = agg[tag]
        print("  %-30s 完成率 %.4f (最差 %.3f 失败 %d)  %6.1f s/源  行程 %6.0f  检测 %5.1f  清除 %4.1f"
              % (tag, statistics.mean(x[0] for x in rs), min(x[1] for x in rs),
                 sum(x[2] for x in rs), statistics.mean(x[3] for x in rs),
                 statistics.mean(x[4] for x in rs), statistics.mean(x[5] for x in rs),
                 statistics.mean(x[6] for x in rs)), flush=True)


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
