#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""speed_q3.py -- 问题三：把 326.8 s/源 压到 300 s 的候选参数扫描（两池复核）。

用法: python speed_q3.py [n_cases] [pool]
"""
import random
import statistics
import sys
import time

import robot_core as rc
import simulator as sim
from make_data import P3

POOLS = {"A": 20000, "B": 50000, "C": 66000, "D": 91000}


def run(params, n, seed0):
    ratio, times, trav, meas, stops = [], [], [], [], []
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
        stops.append(len(brain.visited_stops))
    return (statistics.mean(ratio), min(ratio), sum(1 for r in ratio if r < 0.9999),
            statistics.mean(times), statistics.mean(trav), statistics.mean(meas),
            statistics.mean(stops))


def show(tag, r):
    print("%-34s 完成率 %.4f (最低 %.3f 失败 %d)  %7.1f s/源  行程 %6.0f  检测 %5.1f  站位 %5.1f"
          % ((tag,) + r), flush=True)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    pool = sys.argv[2] if len(sys.argv) > 2 else "A"
    seed0 = POOLS[pool]
    print("pool %s (seed0=%d), %d cases" % (pool, seed0, n))
    base = dict(rc.DEFAULT_PARAMS); base.update(P3)
    print("-" * 118)
    show("baseline (326.8 s 参考)", run(base, n, seed0))
    for tag, mod in (
            ("ring_radius 1250->1100", {"ring_radius": 1100.0}),
            ("ring_radius 1250->1400", {"ring_radius": 1400.0}),
            ("vantage_b_local 550->330", {"vantage_b_local": 330.0}),
            ("vantage_phi_local 55->70", {"vantage_phi_local": 70.0}),
            ("probe_spacing 450->800", {"probe_spacing": 800.0}),
            ("probe_spacing 450->250", {"probe_spacing": 250.0}),
            ("locate_sigma 220->150", {"locate_sigma": 150.0}),
            ("clear_try_radius 42->60", {"clear_try_radius": 60.0}),
            ("endgame_radius 90->60", {"endgame_radius": 60.0}),
            ("probe_min_angle 35->55", {"probe_min_angle": 55.0}),
    ):
        v = dict(base); v.update(mod)
        show(tag, run(v, n, seed0))


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
