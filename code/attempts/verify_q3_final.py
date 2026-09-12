#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""verify_q3_final.py -- 在三个独立 60 例池上复核问题三定稿配置。

池：20000..20059（调参池）、50000..50059、66000..66059（独立池）
"""
import random
import statistics
import time

import robot_core as rc
import simulator as sim
from make_data import P3

POOLS = [(20000, "调参池 20000"), (50000, "独立池 50000"), (66000, "独立池 66000")]


def run(params, n, seed0):
    ratio, times, trav, meas = [], [], [], []
    for k in range(n):
        srcs = sim.make_case(random.Random(seed0 + k), kind_mix=0.0)
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
    return (statistics.mean(ratio), min(ratio), sum(1 for r in ratio if r < 0.9999),
            statistics.mean(times), statistics.median(times),
            statistics.pstdev(times), statistics.mean(trav), statistics.mean(meas))


def main():
    t0 = time.time()
    base = dict(rc.DEFAULT_PARAMS); base.update(P3)
    old = dict(base); old["relocate"] = True; old["ring_radius"] = 1250.0
    old["sweep_center_first"] = False
    all_new = []
    for seed0, name in POOLS:
        a = run(old, 60, seed0)
        b = run(base, 60, seed0)
        all_new.append(b)
        print("%s" % name)
        print("   旧配置  完成率 %.4f  失败 %d  平均 %6.1f s/源  中位 %6.1f  标准差 %5.1f  行程 %6.0f  检测 %5.1f"
              % (a[0], a[2], a[3], a[4], a[5], a[6], a[7]), flush=True)
        print("   新配置  完成率 %.4f  失败 %d  平均 %6.1f s/源  中位 %6.1f  标准差 %5.1f  行程 %6.0f  检测 %5.1f"
              % (b[0], b[2], b[3], b[4], b[5], b[6], b[7]), flush=True)
        print("   -> 每源省 %.1f s (%.1f%%)" % (a[3] - b[3], 100.0 * (a[3] - b[3]) / a[3]),
              flush=True)
    print("=" * 104)
    print("新配置三池平均：完成率 %.4f，最差完成率 %.4f，平均 %.1f s/源"
          % (statistics.mean(x[0] for x in all_new), min(x[1] for x in all_new),
             statistics.mean(x[3] for x in all_new)))
    print("elapsed %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
