#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""q3_final_check.py -- 问题三配置定稿：relocate / ring_radius / sweep_center_first
的 2x2x2 组合，在两池上各跑 30 例（池 P=20000..、池 Q=50000..）。

判定纪律：完成率必须保持 1.0000，且两池时间都不劣于基线才允许采纳。
"""
import random
import statistics
import sys
import time

import robot_core as rc
import simulator as sim
from make_data import P3

POOLS = [(20000, "池P"), (50000, "池Q")]


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
    return (statistics.mean(ratio), min(ratio), statistics.mean(times),
            statistics.mean(trav), statistics.mean(meas))


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    combos = []
    for rel in (True, False):
        for rho in (1250.0, 1130.0):
            for cf in (True, False):
                combos.append(("relocate=%-5s ring=%.0f centre_first=%-5s"
                               % (rel, rho, cf),
                               {"relocate": rel, "ring_radius": rho,
                                "sweep_center_first": cf}))
    for seed0, pname in POOLS:
        print("=" * 104)
        print("%s (seed0=%d, %d 例)" % (pname, seed0, n))
        for tag, mod in combos:
            p = dict(rc.DEFAULT_PARAMS); p.update(P3); p.update(mod)
            r = run(p, n, seed0)
            print("  %-44s 完成率 %.4f (最低 %.3f)  %7.1f s/源  行程 %6.0f  检测 %5.1f"
                  % ((tag,) + r[:1] + r[1:2] + r[2:]), flush=True)


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
