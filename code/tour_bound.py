#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
tour_bound.py -- 测量"探测行程"到底有多少余量。

实测（16 例均值，本配置）：
    总行程 23441 m = 探测 12871 + 清除 8633 + 补测 2974
其中**清除行程 8633 m 与 13 个源的 2-opt 巡回（8635 m）几乎完全相同——已经最优**。
而探测行程 12871 m 对应 12.9 个格点站位，平均每站 998 m。

问题：格点站位本身的巡回应当只有约 6000 m。多出来的 7000 m 在哪里？
本脚本把机器人**实际访问过的全部位置序列**记录下来，
并与"同一批位置的最优巡回（2-opt）"对比，给出确定性的答案。

usage: python tour_bound.py [n_cases] [seed0]
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


def path_len(pts, start=(0.0, 0.0)):
    tot, cur = 0.0, start
    for q in pts:
        tot += math.hypot(q[0] - cur[0], q[1] - cur[1])
        cur = q
    return tot


def two_opt(pts, start=(0.0, 0.0), rounds=60):
    best = list(pts)
    cur_len = path_len(best, start)
    for _ in range(rounds):
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                a = start if i == 0 else best[i - 1]
                b = best[i]
                c = best[j]
                d = best[j + 1] if j + 1 < len(best) else None
                old = math.hypot(a[0] - b[0], a[1] - b[1]) + (
                    math.hypot(c[0] - d[0], c[1] - d[1]) if d else 0.0)
                new = math.hypot(a[0] - c[0], a[1] - c[1]) + (
                    math.hypot(b[0] - d[0], b[1] - d[1]) if d else 0.0)
                if new < old - 1e-9:
                    best[i:j + 1] = best[i:j + 1][::-1]
                    improved = True
        if not improved:
            break
    return path_len(best, start)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    rows = []
    for sd in range(seed0, seed0 + n):
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        ar = sim.Arena(srcs, seed=sd)
        p = dict(rc.DEFAULT_PARAMS)
        p.update(P4)
        br = rc.Brain(rc.LocalClient(ar), params=p, seed=sd)
        seq = []
        om = br.move_measure

        def m2(x, y, c, _seq=seq):
            d = math.hypot(x - br.pos[0], y - br.pos[1])
            if d > 1.0:
                _seq.append((br.pos[0], br.pos[1], x, y, br._cur_task))
            return om(x, y, c)

        br.move_measure = m2
        st = br.run()
        # 只保留"任务之间的腿"：起点 -> 目标
        legs = [(x1, y1) for (_, _, x1, y1, _) in seq]
        actual = sum(math.hypot(x1 - x0, y1 - y0) for (x0, y0, x1, y1, _) in seq)
        opt = two_opt(legs)
        rows.append({"seed": sd, "time": st["mean_time"], "travel": st["travel_m"],
                     "legs": len(legs), "leg_sum": actual, "opt": opt,
                     "n_stops": len(br.visited_stops)})
        print("seed %d: legs=%3d  actual %6.0f m  2-opt over the SAME points %6.0f m"
              "  (%.0f%%)  time %.0f s" % (sd, len(legs), actual, opt,
                                           100 * opt / actual, st["mean_time"]),
              flush=True)
    c = float(n)
    print("\nMEAN: legs %.1f  actual %.0f m  2-opt %.0f m  ->  slack %.0f m "
          "(%.0f s, %.0f s/source)"
          % (statistics.mean(r["legs"] for r in rows),
             statistics.mean(r["leg_sum"] for r in rows),
             statistics.mean(r["opt"] for r in rows),
             statistics.mean(r["leg_sum"] - r["opt"] for r in rows),
             statistics.mean(r["leg_sum"] - r["opt"] for r in rows) / 5.0,
             statistics.mean(r["leg_sum"] - r["opt"] for r in rows) / 5.0 / 13.1))
    with open(os.path.join(DATA, "tour_bound.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
