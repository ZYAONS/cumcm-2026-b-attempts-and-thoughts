#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""q3_probe_test.py -- 机会式（途中）检测到底值不值？

当前 Q3：动作 248 次/例（检测 225 + 清除 23），公开仓库约 140 次/例。
拆分为 census 20 / search 134 / track 49 / vantage 22 / clear 23。
若"途中机会式检测"（adaptive_probe 把间距压到 320 m）能关掉，可省约 60 次动作 = 300 s/例。

两池各 30 例，完成率必须保持 1.0000。
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

POOLS = [(20000, "池P"), (50000, "池Q")]


def run(params, n, seed0):
    ratio, times, trav, meas, clr = [], [], [], [], []
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
        clr.append(st["n_clear"])
    return (statistics.mean(ratio), min(ratio), sum(1 for r in ratio if r < 0.9999),
            statistics.mean(times), statistics.mean(trav), statistics.mean(meas),
            statistics.mean(clr))


def show(tag, r):
    print("  %-40s 完成率 %.4f (最低 %.3f 失败 %d)  %6.1f s/源  行程 %6.0f  检测 %5.1f  清除 %4.1f  动作 %5.1f"
          % ((tag,) + r[:1] + r[1:2] + r[2:] + (r[5] + r[6],)), flush=True)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    base = dict(rc.DEFAULT_PARAMS); base.update(P3)
    configs = [
        ("baseline（途中检测开）", {}),
        ("adaptive_probe=False, ps=450", {"adaptive_probe": False}),
        ("adaptive_probe=False, ps=1200", {"adaptive_probe": False, "probe_spacing": 1200.0}),
        ("adaptive_probe=False, ps=1e6（只在大站检测）", {"adaptive_probe": False, "probe_spacing": 1e6}),
        ("adaptive_probe=True, busy_channels=99（等于关掉加速）", {"busy_channels": 99}),
    ]
    for seed0, pname in POOLS:
        print("=" * 120)
        print("%s (seed0=%d, %d 例)" % (pname, seed0, n))
        for tag, mod in configs:
            p = dict(base); p.update(mod)
            show(tag, run(p, n, seed0))


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
