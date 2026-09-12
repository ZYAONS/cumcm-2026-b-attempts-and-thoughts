#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""speed_q3b.py -- 问题三：安全范围内的最优组合。

七点覆盖条件 0.866*rho + sqrt(R_min^2 - rho^2/4) >= 1800：
    rho=1100 -> 1787.8 (不满足)      rho=1123 -> 1800.0 (临界)
    rho=1150 -> 1814.2 (满足)        rho=1250 -> 1863.8 (满足)
用法: python speed_q3b.py [n_cases] [pool]
"""
import random
import statistics
import sys
import time

import robot_core as rc
import simulator as sim
from make_data import P3

POOLS = {"A": 20000, "B": 50000, "C": 66000, "D": 91000}


def cover_radius(rho, rmin=1000.0):
    import math
    return 0.8660254 * rho + math.sqrt(max(rmin ** 2 - 0.25 * rho ** 2, 0.0))


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
            statistics.mean(times), statistics.mean(trav), statistics.mean(meas))


def show(tag, r):
    print("%-40s 完成率 %.4f (最低 %.3f 失败 %d)  %7.1f s/源  行程 %6.0f  检测 %5.1f"
          % ((tag,) + r), flush=True)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    pool = sys.argv[2] if len(sys.argv) > 2 else "A"
    seed0 = POOLS[pool]
    print("pool %s (seed0=%d), %d cases" % (pool, seed0, n))
    for rho in (1100, 1130, 1150, 1180, 1200, 1250):
        print("   覆盖半径(rho=%.0f) = %.1f m  %s"
              % (rho, cover_radius(float(rho)),
                 "满足" if cover_radius(float(rho)) >= 1800 else "**不满足**"))
    print("-" * 118)
    base = dict(rc.DEFAULT_PARAMS); base.update(P3)
    show("baseline (ring 1250)", run(base, n, seed0))
    for rho in (1130.0, 1150.0, 1180.0, 1200.0):
        v = dict(base); v["ring_radius"] = rho
        show("ring_radius %.0f (cover %.0f m)" % (rho, cover_radius(rho)),
             run(v, n, seed0))
    for vt in (0, 1, 2):
        v = dict(base); v["ring_radius"] = 1150.0; v["vantage_max_tries"] = vt
        show("ring1150 + vantage_max_tries=%d" % vt, run(v, n, seed0))


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
