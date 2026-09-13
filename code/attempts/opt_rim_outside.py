#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""opt_rim_outside.py -- 新想法：贴边环从域内 r=1750 移到域外 r=1900。

动机（几何）：贴边朝外辐射的定向源，只有当采样点半径大于源半径时才可能收到信号。
r=1750 的环覆盖不到 r>1750 的源，这正是"半平面黑洞"残留的缺口，也是我们必须保留
13 个认证格点的原因之一。把环移到域外 r=1900 后：
  * 环上点到 r<=1800 任意源的距离都 <= 1000（同向时 100~450 m），
  * 采样点在目标域外 => 对朝外辐射的源一定处于受光半平面，
  * 因此可以用更少的环上点覆盖同样的角向范围（角向容差 cos(delta) >= 0.85，约 +-32 度）。
代价只有环周长从 2*pi*1750=11.0 km 增到 2*pi*1900=11.9 km。

若"域外 8 点环"能达到与"域内 12 点环"相同的完成率，则可同时省 4 个站位。
"""
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import robot_core as rc
import simulator as sim
from make_data import P4


def run(params, n, seed0):
    ratio, times, trav, meas, clr, stops = [], [], [], [], [], []
    for k in range(n):
        srcs = sim.make_case(random.Random(seed0 + k), kind_mix=0.5)
        arena = sim.Arena(srcs, seed=seed0 + k)
        cl = rc.LocalClient(arena)
        brain = rc.Brain(cl, params=params, seed=k)
        st = brain.run()
        st.update(arena.stats())
        stops.append(len(brain.visited_stops))
        arena.close()
        ratio.append(st["clear_ratio"])
        times.append(st["mean_time"] if st["n_cleared"] else 9000.0)
        trav.append(st["travel_m"])
        meas.append(st["n_measure"])
        clr.append(st["n_clear"])
    return (statistics.mean(ratio), min(ratio), sum(1 for r in ratio if r < 0.9999),
            statistics.mean(times), statistics.mean(trav), statistics.mean(meas),
            statistics.mean(clr), statistics.mean(stops))


VARIANTS = [
    ("基线 域内 r=1750 n=12", {}),
    ("域外 r=1900 n=12", {"rim_ring_r": 1900.0, "rim_ring_n": 12}),
    ("域外 r=1900 n=8", {"rim_ring_r": 1900.0, "rim_ring_n": 8}),
    ("域外 r=1900 n=6", {"rim_ring_r": 1900.0, "rim_ring_n": 6}),
    ("域外 r=1850 n=8", {"rim_ring_r": 1850.0, "rim_ring_n": 8}),
]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    b = dict(rc.DEFAULT_PARAMS); b.update(P4)
    agg = {}
    for seed0, pname in ((30000, "池A"), (12000, "池B"), (70000, "池C")):
        for tag, mod in VARIANTS:
            p = dict(b); p.update(mod)
            agg.setdefault(tag, []).append(run(p, n, seed0))
            print("  %s %-24s 完成率 %.4f 失败 %d  %6.1f s/源 行程 %6.0f 检测 %5.1f 站位 %5.1f"
                  % (pname, tag, agg[tag][-1][0], agg[tag][-1][2], agg[tag][-1][3],
                     agg[tag][-1][4], agg[tag][-1][5], agg[tag][-1][7]), flush=True)
    print()
    print("三池汇总（%d 例/池）" % n)
    for tag, _ in VARIANTS:
        rs = agg[tag]
        print("  %-24s 平均完成率 %.4f (最差 %.3f 总失败 %d)  %6.1f s/源  平均站位 %.1f"
              % (tag, statistics.mean(x[0] for x in rs), min(x[1] for x in rs),
                 sum(x[2] for x in rs), statistics.mean(x[3] for x in rs),
                 statistics.mean(x[7] for x in rs)))


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
