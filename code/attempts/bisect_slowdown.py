#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""bisect_slowdown.py -- 找出让问题三从 327 s 变慢到 366 s 的那个改动。

对 9/12 下午以后加入、且默认开启的开关逐个单独关闭，看谁能让用时回到 327 s。
池：seed 20000..20029（30 例，与 q34_agg.json 同池的前半）。
"""
import random
import statistics
import time

import robot_core as rc
import simulator as sim
from make_data import P3

SWITCHES = [
    ("baseline (现状全开)", {}),
    ("skip_useless_stops=False", {"skip_useless_stops": False}),
    ("periodic_cert=False", {"periodic_cert": False}),
    ("relocate=False", {"relocate": False}),
    ("exhaustive_clear=False", {"exhaustive_clear": False}),
    ("leg_probe_step=0", {"leg_probe_step": 0.0}),
    ("term_step_frac=0.7", {"term_step_frac": 0.7}),
    ("adaptive_probe=False", {"adaptive_probe": False}),
    ("spread_stops=False", {"spread_stops": False}),
    ("enroute_clear=False", {"enroute_clear": False}),
]


def run(params, n=30, seed0=20000):
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
    return (statistics.mean(ratio), statistics.mean(times),
            statistics.mean(trav), statistics.mean(meas))


def main():
    print("目标：q34_agg.json 记录的问题三 = 327.0 s/源（60 例）；现在同一池约 362~366 s")
    print("-" * 100)
    base = dict(rc.DEFAULT_PARAMS); base.update(P3)
    for tag, mod in SWITCHES:
        p = dict(base); p.update(mod)
        r = run(p)
        print("%-28s 完成率 %.4f  平均 %7.1f s/源  行程 %6.0f  检测 %5.1f"
              % (tag, r[0], r[1], r[2], r[3]), flush=True)


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
