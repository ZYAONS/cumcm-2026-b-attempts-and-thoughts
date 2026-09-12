#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""speed_test2.py -- 组合方案扫描，两池复核。

用法: python speed_test2.py [n_cases] [pool]
"""
import os
import random
import statistics
import sys
import time

import robot_core as rc
import simulator as sim
from make_data import P3, P4

POOLS = {"A": 30000, "B": 12000, "C": 70000, "D": 45000, "E": 88000}


def run(params, n, seed0, mix=0.5):
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
    return (statistics.mean(ratio), min(ratio), sum(1 for r in ratio if r < 0.9999),
            statistics.mean(times), statistics.mean(trav), statistics.mean(meas),
            statistics.mean(stops))


def show(tag, r):
    print("%-36s 完成率 %.4f (最低 %.3f 失败 %d)  %7.1f s/源  行程 %6.0f  检测 %5.1f  站位 %5.1f"
          % ((tag,) + r), flush=True)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    pool = sys.argv[2] if len(sys.argv) > 2 else "A"
    seed0 = POOLS[pool]
    print("pool %s (seed0=%d), %d cases" % (pool, seed0, n))
    base = dict(rc.DEFAULT_PARAMS); base.update(P4)
    print("-" * 118)
    show("baseline (rim12, lattice<=1800)", run(base, n, seed0))
    for tag, mod in (
            ("rim6", {"rim_ring_n": 6}),
            ("rim6 + lattice<=1500", {"rim_ring_n": 6, "survey_max_r": 1500.0}),
            ("rim6 + lattice<=1300", {"rim_ring_n": 6, "survey_max_r": 1300.0}),
            ("rim6 + lattice<=1100", {"rim_ring_n": 6, "survey_max_r": 1100.0}),
            ("rim4 + lattice<=1300", {"rim_ring_n": 4, "survey_max_r": 1300.0}),
            ("rim6 + rim_r1650", {"rim_ring_n": 6, "rim_ring_r": 1650.0}),
            ("rim6 + verify_margin 500", {"rim_ring_n": 6, "verify_margin": 500.0}),
    ):
        v = dict(base); v.update(mod)
        show(tag, run(v, n, seed0))


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
