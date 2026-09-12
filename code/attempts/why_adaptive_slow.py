#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
why_adaptive_slow.py -- 自适应模式的行程为什么高达 45000 m？

理论下界（floor.py）：
    清除巡回（13 个源的 2-opt）8635 m = 1727 s
    + 普查 120 s + 约 5 次/源检测 392 s + 约 4 次/源清除动作 209 s
    = 2447 s = 188 s/源

若"认证所需的读数"能由**本来就要走的清除巡回**沿途测量提供，
那么总时间应当落在 250~330 s/源。但自适应模式实测 974.9 s、行程 45344 m。

本脚本把自适应模式的行程按任务类拆开，并统计"每次站位补点的行程"，
找出是哪一个环节在制造绕路。

usage: python why_adaptive_slow.py [n_cases] [seed0]
"""
import json
import math
import os
import random
import statistics
import sys

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
from make_data import P4  # noqa: E402


def run(seed, ov):
    cfg = dict(P4)
    cfg.update(ov)
    srcs = sim.make_case(random.Random(seed), kind_mix=0.5)
    ar = sim.Arena(srcs, seed=seed)
    br = rc.Brain(rc.LocalClient(ar), params=dict(rc.DEFAULT_PARAMS, **cfg),
                  seed=seed)
    # 记录每次 task 的起点与终点，看看"绕路"发生在哪里
    hops = []
    om = br.move_measure

    def m2(x, y, c):
        hops.append((br.pos[0], br.pos[1], x, y, br._cur_task))
        return om(x, y, c)

    br.move_measure = m2
    st = br.run()
    by = {}
    for (x0, y0, x1, y1, k) in hops:
        d = math.hypot(x1 - x0, y1 - y0)
        by.setdefault(k, [0.0, 0])
        by[k][0] += d
        by[k][1] += 1
    return st, by, len(br.visited_stops)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    for tag, ov in (
            ("adaptive batch1", {"survey_mode": "adaptive", "adaptive_batch": 1,
                                 "max_search_stops": 60, "verify_margin": 90.0,
                                 "periodic_cert_every": 1, "probe_spacing": 400.0,
                                 "clear_bonus": 500.0, "locate_sigma": 400.0}),
            ("adaptive batch4", {"survey_mode": "adaptive", "adaptive_batch": 4,
                                 "max_search_stops": 60, "verify_margin": 90.0,
                                 "periodic_cert_every": 1, "probe_spacing": 400.0,
                                 "clear_bonus": 500.0, "locate_sigma": 400.0}),
            ("s950 rim16", {"survey_spacing": 950.0, "rim_ring_n": 16,
                            "max_search_stops": 40, "verify_margin": 90.0,
                            "periodic_cert_every": 1, "probe_spacing": 650.0,
                            "clear_bonus": 500.0, "locate_sigma": 400.0}),
    ):
        agg = {}
        tot_time, tot_travel, tot_stops = [], [], []
        for sd in range(seed0, seed0 + n):
            st, by, nst = run(sd, ov)
            tot_time.append(st["mean_time"])
            tot_travel.append(st["travel_m"])
            tot_stops.append(nst)
            for k, v in by.items():
                agg.setdefault(k, [0.0, 0])
                agg[k][0] += v[0]
                agg[k][1] += v[1]
        print("=" * 74)
        print("%-18s time %6.1f s/source  travel %7.0f m  stops %5.1f"
              % (tag, statistics.mean(tot_time), statistics.mean(tot_travel),
                 statistics.mean(tot_stops)))
        tot = sum(v[0] for v in agg.values())
        for k in sorted(agg, key=lambda x: -agg[x][0]):
            d, c = agg[k]
            print("   %-9s hops %5.1f  travel %8.0f m (%4.1f%%)  mean hop %5.0f m"
                  % (k, c / float(n), d / n, 100 * d / tot, d / max(c, 1)))
        print("   TOTAL travel %.0f m" % (tot / n))
