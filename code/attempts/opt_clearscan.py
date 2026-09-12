#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""opt_clearscan.py -- 借鉴公开实现"候选区域直径 <= 95 m 就改用 20 m 覆盖格点做清除扫描"的思路，
测我们这边"保证性栅格穷举"的触发时机（exhaustive_after）与末段半径。

我们的 _exhaustive_clear 是在常规图案连续失败若干次后触发的保证性栅格；
把它提前（=0/1）相当于对方"更早把定位换成清除"。测 Q3 与 Q4，各 20 例 × 2 池。
"""
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import robot_core as rc
import simulator as sim
from make_data import P3, P4


def run(params, n, seed0, mix):
    ratio, times, trav, meas, clr = [], [], [], [], []
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
        clr.append(st["n_clear"])
    return (statistics.mean(ratio), min(ratio), sum(1 for r in ratio if r < 0.9999),
            statistics.mean(times), statistics.mean(trav), statistics.mean(meas),
            statistics.mean(clr))


def show(tag, r):
    print("  %-40s 完成率 %.4f (最低 %.3f 失败 %d)  %6.1f s/源  行程 %6.0f  检测 %5.1f  清除 %4.1f"
          % ((tag,) + r[:1] + r[1:2] + r[2:]), flush=True)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    for prob, base in (("问题三", P3), ("问题四", P4)):
        mix = 0.0 if prob == "问题三" else 0.5
        b = dict(rc.DEFAULT_PARAMS); b.update(base)
        print("=" * 112)
        print("%s（%d 例 × 2 池）" % (prob, n))
        variants = [
            ("baseline", {}),
            ("exhaustive_after=0（立即保证性栅格）", {"exhaustive_after": 0}),
            ("exhaustive_after=1", {"exhaustive_after": 1}),
            ("endgame_radius 90->120", {"endgame_radius": 120.0}),
            ("clear_try_radius 42->60", {"clear_try_radius": 60.0}),
            ("对照：exhaustive_clear=False", {"exhaustive_clear": False}),
        ]
        agg = {}
        for seed0 in (20000 if prob == "问题三" else 30000,
                      50000 if prob == "问题三" else 12000):
            for tag, mod in variants:
                p = dict(b); p.update(mod)
                r = run(p, n, seed0, mix)
                agg.setdefault(tag, []).append(r)
        for tag, _ in variants:
            rs = agg[tag]
            mean_t = statistics.mean(x[3] for x in rs)
            worst = min(x[1] for x in rs)
            ratio = statistics.mean(x[0] for x in rs)
            fails = sum(x[2] for x in rs)
            print("  %-40s 两池平均完成率 %.4f (最差 %.3f 失败 %d)  %6.1f s/源"
                  % (tag, ratio, worst, fails, mean_t), flush=True)


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
