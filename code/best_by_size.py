#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""best_by_size.py -- 问题三/问题四在固定 12 源与 16 源下的最好成绩。

同时给出"快速配置"与"严格变体"两条曲线，便于论文与 README 引用。
池：4 个独立池 × 30 例 = 120 例/档。
"""
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import robot_core as rc
import simulator as sim
from make_data import P3, P4, P4_RIGOROUS

POOLS = [20000, 50000, 30000, 12000]


def run(params, n, seed0, mix, nsrc):
    ratio, times, trav, act = [], [], [], []
    for k in range(n):
        srcs = sim.make_case(random.Random(seed0 + k), n_sources=nsrc, kind_mix=mix)
        arena = sim.Arena(srcs, seed=seed0 + k)
        cl = rc.LocalClient(arena)
        brain = rc.Brain(cl, params=params, seed=k)
        st = brain.run()
        st.update(arena.stats())
        arena.close()
        ratio.append(st["clear_ratio"])
        times.append(st["mean_time"] if st["n_cleared"] else 9000.0)
        trav.append(st["travel_m"])
        act.append(st["n_measure"] + st["n_clear"])
    return (statistics.mean(ratio), min(ratio), sum(1 for r in ratio if r < 0.9999),
            statistics.mean(times), statistics.mean(trav), statistics.mean(act))


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    p3 = dict(rc.DEFAULT_PARAMS); p3.update(P3)
    p4 = dict(rc.DEFAULT_PARAMS); p4.update(P4)
    p4r = dict(rc.DEFAULT_PARAMS); p4r.update(P4); p4r.update(P4_RIGOROUS)
    combos = [
        ("问题三（全向）", p3, 0.0),
        ("问题四（混合）", p4, 0.5),
        ("问题四（混合·严格变体）", p4r, 0.5),
    ]
    print("每档 %d 池 × %d 例 = %d 例" % (len(POOLS), n, len(POOLS) * n))
    print("%-24s %-6s %8s %10s %10s %9s %9s" %
          ("配置", "源数", "完成率", "最差完成率", "时间/源", "行程/m", "动作数"))
    print("-" * 84)
    for name, params, mix in combos:
        for nsrc in (12, 16):
            rs = [run(params, n, s0, mix, nsrc) for s0 in POOLS]
            ratio = statistics.mean(x[0] for x in rs)
            worst = min(x[1] for x in rs)
            fails = sum(x[2] for x in rs)
            t = statistics.mean(x[3] for x in rs)
            trav = statistics.mean(x[4] for x in rs)
            act = statistics.mean(x[5] for x in rs)
            print("%-24s %-6d %8.4f %10.4f %10.1f %9.0f %9.1f   (失败 %d/%d)"
                  % (name, nsrc, ratio, worst, t, trav, act, fails, len(POOLS) * n),
                  flush=True)
        print()


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
