#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
floor.py -- 下界核算：这件事最少要花多少时间？

目标是把问题四压到 200~300 s/源且完成率 0.99+。为此必须知道**硬下界**：

  (1) 清除巡回：13 个源随机分布在全域，机器人必须逐个走到 20 m 以内。
      这一段是"无论如何都要走"的，其下界就是这些点的 TSP 长度。
  (2) 检测：至少要在原点普查一次（20 个频道），每个源还要几条方位读数。
  (3) 清除动作：每次 3~5 s。
  (4) 认证：要证明"没有漏掉的源"，需要对全域取样覆盖。

本脚本把 (1) 单独算出来（用 2-opt 在真实源坐标上求解），
并与当前实现的实测值对比，从而判断还剩多少非必要开销。

usage: python floor.py [n_cases] [seed0]
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


def tour_len(seq, start=(0.0, 0.0)):
    tot, cur = 0.0, start
    for q in seq:
        tot += math.hypot(q[0] - cur[0], q[1] - cur[1])
        cur = q
    return tot


def two_opt(points, start=(0.0, 0.0)):
    best = list(points)
    improved = True
    while improved:
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                cand = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                if tour_len(cand, start) < tour_len(best, start) - 1e-9:
                    best, improved = cand, True
    return tour_len(best, start), best


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    rows = []
    for sd in range(seed0, seed0 + n):
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        pts = [(s.x, s.y) for s in srcs]
        nn = tour_len(pts)
        opt, _ = two_opt(pts)
        rows.append({"seed": sd, "n": len(pts), "nn": nn, "opt": opt})
    nn = statistics.mean(r["nn"] for r in rows)
    opt = statistics.mean(r["opt"] for r in rows)
    ns = statistics.mean(r["n"] for r in rows)
    print("over %d cases (%.1f sources each):" % (n, ns))
    print("  nearest-neighbour tour over the sources : %7.0f m = %6.0f s"
          % (nn, nn / 5.0))
    print("  2-opt tour over the sources             : %7.0f m = %6.0f s"
          % (opt, opt / 5.0))
    print("  per source                              : %7.0f m = %6.0f s"
          % (opt / ns, opt / 5.0 / ns))
    print()
    print("  + entry census 20 detections            : %6.0f s" % (20 * 6.0))
    print("  + ~5 extra detections per source        : %6.0f s"
          % (ns * 5 * 6.0))
    print("  + ~4 clear actions per source           : %6.0f s"
          % (ns * 4 * 4.0))
    base = opt / 5.0 + 20 * 6.0 + ns * 5 * 6.0 + ns * 4 * 4.0
    print("  ---------------------------------------------------")
    print("  unavoidable subtotal                    : %6.0f s = %5.0f s/source"
          % (base, base / ns))
    print()
    print("  measured, perfect config (P4_PERFECT)   : %6.0f s = %5.0f s/source"
          % (6795, 6795 / ns))
    print("  measured, adaptive batch1               : %6.0f s = %5.0f s/source"
          % (508.5 * ns, 508.5))
    with open(os.path.join(DATA, "floor.json"), "w", encoding="utf-8") as f:
        json.dump({"rows": rows, "mean_nn": nn, "mean_opt": opt,
                   "mean_n": ns, "floor_total": base,
                   "floor_per_source": base / ns}, f, ensure_ascii=False, indent=1)
    print("report -> data/floor.json")
