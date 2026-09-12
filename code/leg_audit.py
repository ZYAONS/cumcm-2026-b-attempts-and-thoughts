#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
leg_audit.py -- 把 55.6 段移动逐类拆开，找出可压缩的那部分。

已知：访问约 55.6 个点，其 2-opt 巡回 19964 m = 305 s/源。
但这 55.6 个点里包含约 18 个"归航中间点"——它们不是必须的独立目标，
而是归航过程的副产品。如果归航是单调走向估计点的，这些点不应额外增加行程；
若它们额外增加了行程，那就是可压缩的余量。

本脚本按任务类型统计每段的起点/终点/长度，并回答：
  * 观测站位之间的腿有多长（这是"普查"的成本）
  * 走向源的腿有多长（这是"清除"的必需成本）
  * 归航内部的腿有多长、是否单调

usage: python leg_audit.py [n_cases] [seed0]
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


def audit(seed):
    srcs = sim.make_case(random.Random(seed), kind_mix=0.5)
    ar = sim.Arena(srcs, seed=seed)
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    br = rc.Brain(rc.LocalClient(ar), params=p, seed=seed)
    rows = []
    om = br.move_measure

    def m2(x, y, c):
        x0, y0 = br.pos
        d = math.hypot(x - x0, y - y0)
        if d > 1.0:
            rows.append((br._cur_task, x0, y0, x, y, d, c))
        return om(x, y, c)

    br.move_measure = m2
    st = br.run()
    # 归航是否单调：把 clear 任务内的连续腿按"到最近源的距离是否下降"判断
    srcpos = [(s.x, s.y) for s in srcs]
    mono = 0
    nonmono = 0
    for (k, x0, y0, x1, y1, d, c) in rows:
        if k != "clear":
            continue
        d0 = min(math.hypot(x0 - s[0], y0 - s[1]) for s in srcpos)
        d1 = min(math.hypot(x1 - s[0], y1 - s[1]) for s in srcpos)
        if d1 <= d0 + 1.0:
            mono += 1
        else:
            nonmono += 1
    by = {}
    for (k, x0, y0, x1, y1, d, c) in rows:
        by.setdefault(k, [0.0, 0])
        by[k][0] += d
        by[k][1] += 1
    return {"time": st["mean_time"], "travel": st["travel_m"], "n": len(srcs),
            "by": by, "mono": mono, "nonmono": nonmono,
            "n_stops": len(br.visited_stops)}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    agg, tm, tt, nn, mono, non = {}, [], [], [], 0, 0
    for sd in range(seed0, seed0 + n):
        r = audit(sd)
        tm.append(r["time"])
        tt.append(r["travel"])
        nn.append(r["n"])
        mono += r["mono"]
        non += r["nonmono"]
        for k, v in r["by"].items():
            agg.setdefault(k, [0.0, 0])
            agg[k][0] += v[0]
            agg[k][1] += v[1]
    print("mean time %.1f s/source, travel %.0f m, %.1f sources/case"
          % (statistics.mean(tm), statistics.mean(tt), statistics.mean(nn)))
    tot = sum(v[0] for v in agg.values())
    print("%-10s %8s %8s %10s %10s %10s"
          % ("task", "legs", "travel", "share", "mean leg", "per source"))
    nsrc = statistics.mean(nn)
    for k in sorted(agg, key=lambda x: -agg[x][0]):
        d, c = agg[k]
        print("%-10s %8.1f %8.0f %9.1f%% %10.0f %10.1f"
              % (k, c / n, d / n, 100 * d / tot, d / max(c, 1),
                 d / n / nsrc))
    print("TOTAL travel %.0f m  = %.0f s = %.0f s/source"
          % (tot / n, tot / n / 5.0, tot / n / 5.0 / nsrc))
    print("clear legs monotone toward a source: %d, non-monotone: %d"
          % (mono, non))
