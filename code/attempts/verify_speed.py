#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""verify_speed.py -- 对推荐改动做两池复核（时间与完成率必须同时报告）。

用法: python verify_speed.py [n_cases_per_pool]
"""
import random
import statistics
import sys
import time

import robot_core as rc
import simulator as sim
from make_data import P3, P4

POOLS = [(20000, "池A"), (50000, "池B"), (66000, "池C")]
POOLS4 = [(30000, "池A"), (12000, "池B"), (70000, "池C"), (45000, "池D")]


def run(params, n, seed0, mix):
    ratio, times, trav, meas = [], [], [], []
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
    return (statistics.mean(ratio), min(ratio), sum(1 for r in ratio if r < 0.9999),
            statistics.mean(times), statistics.mean(trav), statistics.mean(meas))


def show(tag, r):
    print("  %-34s 完成率 %.4f (最低 %.3f 失败 %d)  %7.1f s/源  行程 %6.0f  检测 %5.1f"
          % ((tag,) + r), flush=True)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    t0 = time.time()

    print("=" * 112)
    print("问题三：推荐改动 = ring_radius 1250 -> 1130（覆盖率 1804 m >= 1800 m，仍满足七点覆盖定理）")
    print("         + 端末清除图案先试估计中心")
    base = dict(rc.DEFAULT_PARAMS); base.update(P3)
    new = dict(base); new["ring_radius"] = 1130.0; new["sweep_center_first"] = True
    old = dict(base); old["sweep_center_first"] = False
    for seed0, name in POOLS:
        a = run(old, n, seed0, 0.0)
        b = run(new, n, seed0, 0.0)
        show("%s 现状" % name, a)
        show("%s 推荐(ring1130+中心优先)" % name, b)
        print("      -> 每源省 %.1f s (%.1f%%)，完成率 %s"
              % (a[3] - b[3], 100.0 * (a[3] - b[3]) / a[3],
                 "不变" if abs(a[0] - b[0]) < 1e-9 else "变化 %.4f->%.4f" % (a[0], b[0])),
              flush=True)

    print("=" * 112)
    print("问题四：候选改动 = rim_ring_n 12 -> 6（缩掉一半贴边环）")
    b4 = dict(rc.DEFAULT_PARAMS); b4.update(P4)
    v4 = dict(b4); v4["rim_ring_n"] = 6
    tot_a = tot_b = 0
    for seed0, name in POOLS4:
        a = run(b4, n, seed0, 0.5)
        b = run(v4, n, seed0, 0.5)
        show("%s rim12" % name, a)
        show("%s rim6" % name, b)
        ok = "完成率不变" if abs(a[0] - b[0]) < 1e-9 else "**完成率 %.4f -> %.4f**" % (a[0], b[0])
        print("      -> 每源省 %.1f s (%.1f%%)，%s"
              % (a[3] - b[3], 100.0 * (a[3] - b[3]) / a[3], ok), flush=True)
        tot_a += a[4] + 5 * a[5] * 6 / 5.0
        tot_b += b[4] + 5 * b[5] * 6 / 5.0
    print("elapsed %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
