#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""speed_test.py -- 逐个实测"压缩用时"的候选改动，报告 完成率 / 平均时间 / 行程 / 检测数。

纪律：每个配置都在**同一批算例池**上跑，时间与完成率同时报告；
      真正采用前还要在第二个池上复核。

用法: python speed_test.py [n_cases] [pool]
      pool: A=30000.. (调参池)  B=12000.. C=70000..
"""
import os
import random
import statistics
import sys
import time

import robot_core as rc
import simulator as sim
from make_data import P3, P4

POOLS = {"A": 30000, "B": 12000, "C": 70000, "D": 45000}


def run(mode, params, n, seed0, mix):
    ratio, times, trav, meas, stops = [], [], [], [], []
    for k in range(n):
        srcs = sim.make_case(random.Random(seed0 + k), kind_mix=mix)
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
        stops.append(len(brain.visited_stops))
    return {"ratio": statistics.mean(ratio), "min": min(ratio),
            "time": statistics.mean(times), "travel": statistics.mean(trav),
            "measure": statistics.mean(meas), "stops": statistics.mean(stops),
            "fails": sum(1 for r in ratio if r < 0.9999)}


def show(tag, r):
    print("%-34s 完成率 %.4f (最低 %.3f, 失败 %d)  时间 %7.1f s/源  "
          "行程 %6.0f m  检测 %5.1f  站位 %5.1f"
          % (tag, r["ratio"], r["min"], r["fails"], r["time"], r["travel"],
             r["measure"], r["stops"]), flush=True)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    pool = sys.argv[2] if len(sys.argv) > 2 else "A"
    seed0 = POOLS[pool]
    print("pool %s (seed0=%d), %d cases each" % (pool, seed0, n))
    print("-" * 118)

    print("问题 3")
    base3 = dict(rc.DEFAULT_PARAMS); base3.update(P3)
    show("baseline", run("q3", base3, n, seed0, 0.0))
    v = dict(base3); v["sweep_center_first"] = False
    show("sweep centre LAST (旧行为)", run("q3", v, n, seed0, 0.0))
    print("-" * 118)

    print("问题 4")
    base4 = dict(rc.DEFAULT_PARAMS); base4.update(P4)
    show("baseline (rim12, lattice 全区域)", run("q4", base4, n, seed0, 0.5))
    v = dict(base4); v["sweep_center_first"] = False
    show("  sweep centre LAST (旧行为)", run("q4", v, n, seed0, 0.5))
    for rmax in (1650.0, 1500.0, 1300.0, 1100.0):
        v = dict(base4); v["survey_max_r"] = rmax
        show("  lattice 限制在 r<=%.0f" % rmax, run("q4", v, n, seed0, 0.5))
    for rn in (6, 8, 10):
        v = dict(base4); v["rim_ring_n"] = rn
        show("  rim_ring_n=%d" % rn, run("q4", v, n, seed0, 0.5))
    # 组合
    v = dict(base4); v["survey_max_r"] = 1500.0; v["rim_ring_n"] = 8
    show("  lattice<=1500 + rim8", run("q4", v, n, seed0, 0.5))


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
