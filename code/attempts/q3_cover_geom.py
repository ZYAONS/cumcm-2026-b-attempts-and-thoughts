#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""q3_cover_geom.py -- 覆盖环几何扫描：点数 n × 半径 ρ，三池各 30 例。

动机：公开仓库用 8 点环（ρ=1081，覆盖半径 1909 m）。我们的七点环（6 点，ρ=1130）
只留 3.7 m 余量，且初始交会几何较差，导致需要大量"途中机会式检测"。
本脚本同时固定 adaptive_probe=False（上一轮实测的小幅改进）。
"""
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import robot_core as rc
import simulator as sim
from make_data import P3

POOLS = [(20000, "池P"), (50000, "池Q"), (66000, "池R")]


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
    print("  %-34s 完成率 %.4f (最低 %.3f 失败 %d)  %6.1f s/源  行程 %6.0f  检测 %5.1f"
          % ((tag,) + r[:1] + r[1:2] + r[2:]), flush=True)


CONFIGS = [
    ("6 点 ρ=1130（现在）", {"ring_n": 6, "ring_radius": 1130.0}),
    ("8 点 ρ=1081（对方）", {"ring_n": 8, "ring_radius": 1081.0}),
    ("8 点 ρ=1130", {"ring_n": 8, "ring_radius": 1130.0}),
    ("8 点 ρ=1250", {"ring_n": 8, "ring_radius": 1250.0}),
    ("12 点 ρ=900", {"ring_n": 12, "ring_radius": 900.0}),
    ("12 点 ρ=1000", {"ring_n": 12, "ring_radius": 1000.0}),
]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    base = dict(rc.DEFAULT_PARAMS); base.update(P3)
    base["adaptive_probe"] = False          # 上一轮实测的小幅改进
    for seed0, pname in POOLS:
        print("=" * 112)
        print("%s (seed0=%d, %d 例)" % (pname, seed0, n))
        for tag, mod in CONFIGS:
            p = dict(base); p.update(mod)
            show(tag, run(p, n, seed0))


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
