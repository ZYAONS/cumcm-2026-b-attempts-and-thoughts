#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""check_q3_baseline.py -- 确认 326.8 s 是否为过期数字。

同一 60 例池（seed 20000..20059）上比较：
  旧配置：ring_radius 1250 + 端末中心最后
  新配置：ring_radius 1130 + 端末中心优先
"""
import random
import statistics
import time

import robot_core as rc
import simulator as sim
from make_data import P3


def run(params, n=60, seed0=20000):
    ratio, times, trav = [], [], []
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
    return (statistics.mean(ratio), statistics.mean(times),
            statistics.median(times), statistics.mean(trav),
            statistics.pstdev(times), len(times))


def main():
    old = dict(rc.DEFAULT_PARAMS); old.update(P3)
    old["ring_radius"] = 1250.0
    old["sweep_center_first"] = False
    new = dict(rc.DEFAULT_PARAMS); new.update(P3)
    for tag, p in (("旧配置 ring1250 + 中心最后", old),
                   ("新配置 ring1130 + 中心优先", new)):
        a = run(p)
        print("%-28s 完成率 %.4f  平均 %.1f s/源  中位 %.1f  标准差 %.1f  行程 %.0f"
              % (tag, a[0], a[1], a[2], a[4], a[3]), flush=True)


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
