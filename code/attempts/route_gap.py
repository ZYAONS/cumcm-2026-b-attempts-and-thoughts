#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
route_gap.py -- 19 个格点站位到底需要多少行程？

margin_scan 显示 s=900、纯扫描、margin 350+ 时：19 个站位、21159 m 行程、
361 次检测、527 s/源、完成率 0.9910。已经很接近 500 s。

本脚本回答"还能从哪里省"：把机器人实际访问的站位序列取出来，
与"同样这些站位的最优巡回"比较，看路径有多少余量。

usage: python route_gap.py [n_cases] [seed0] [spacing]
"""
import json
import math
import os
import random
import sys

import geom_core as g
import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
from make_data import P4  # noqa: E402


def nn_tour(points, start=(0.0, 0.0)):
    rest = list(points)
    cur, tot, seq = start, 0.0, []
    while rest:
        i = min(range(len(rest)),
                key=lambda k: (rest[k][0] - cur[0]) ** 2 + (rest[k][1] - cur[1]) ** 2)
        nxt = rest.pop(i)
        tot += math.hypot(nxt[0] - cur[0], nxt[1] - cur[1])
        cur = nxt
        seq.append(nxt)
    return tot, seq


def two_opt(seq, start=(0.0, 0.0)):
    def length(s):
        tot, cur = 0.0, start
        for p in s:
            tot += math.hypot(p[0] - cur[0], p[1] - cur[1])
            cur = p
        return tot
    best = list(seq)
    improved = True
    while improved:
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                cand = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                if length(cand) < length(best) - 1e-9:
                    best = cand
                    improved = True
    return length(best), best


def analyse(seed, spacing, margin):
    srcs = sim.make_case(random.Random(seed), kind_mix=0.5)
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    p["survey_spacing"] = spacing
    p["max_search_stops"] = 0
    p["verify_margin"] = margin
    ar = sim.Arena(srcs, seed=seed)
    br = rc.Brain(rc.LocalClient(ar), params=p, seed=seed)
    path = []
    om = br.move_measure

    def m2(x, y, c):
        path.append((br.pos[0], br.pos[1], x, y))
        return om(x, y, c)

    br.move_measure = m2
    st = br.run()
    # travel between task positions
    hops = [math.hypot(x1 - x0, y1 - y0) for (x0, y0, x1, y1) in path]
    stops = list(br.visited_stops)
    if len(stops) < 3:
        return None
    n1, seq = nn_tour(stops)
    n2, _ = two_opt(seq)
    return {"sources": len(srcs), "ratio": st["clear_ratio"],
            "time": st["mean_time"], "travel": st["travel_m"],
            "n_stops": len(stops), "nn": n1, "opt": n2,
            "sum_hops": sum(hops), "n_actions": len(path)}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    spacing = float(sys.argv[3]) if len(sys.argv) > 3 else 900.0
    margin = float(sys.argv[4]) if len(sys.argv) > 4 else 500.0
    agg = {"cases": 0, "stops": 0, "travel": 0.0, "nn": 0.0, "opt": 0.0,
           "ratio": 0.0, "time": 0.0, "actions": 0}
    for i in range(n):
        r = analyse(seed0 + i, spacing, margin)
        if r is None:
            continue
        agg["cases"] += 1
        for k in ("stops", "n_stops"):
            pass
        agg["stops"] += r["n_stops"]
        agg["travel"] += r["travel"]
        agg["nn"] += r["nn"]
        agg["opt"] += r["opt"]
        agg["ratio"] += r["ratio"]
        agg["time"] += r["time"]
        agg["actions"] += r["n_actions"]
        print("seed %d: stops=%2d actions=%3d travel=%6.0f  NN tour over the same "
              "stops=%6.0f  2-opt=%6.0f m  ratio=%.3f time=%.0f"
              % (seed0 + i, r["n_stops"], r["n_actions"], r["travel"], r["nn"],
                 r["opt"], r["ratio"], r["time"]), flush=True)
    c = float(agg["cases"])
    print("\nMEAN over %d cases: stops=%.1f actions=%.1f" % (c, agg["stops"] / c,
                                                             agg["actions"] / c))
    print("  actual travel  %7.0f m" % (agg["travel"] / c))
    print("  NN tour        %7.0f m  (%.0f%% of actual)"
          % (agg["nn"] / c, 100 * (agg["nn"] / c) / (agg["travel"] / c)))
    print("  2-opt tour     %7.0f m  (%.0f%% of actual)"
          % (agg["opt"] / c, 100 * (agg["opt"] / c) / (agg["travel"] / c)))
    print("  time %.1f s/source, ratio %.4f" % (agg["time"] / c, agg["ratio"] / c))
    with open(os.path.join(DATA, "route_gap.json"), "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=1)
