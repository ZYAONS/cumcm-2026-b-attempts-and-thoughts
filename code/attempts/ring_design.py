#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ring_design.py -- 用"环组"构造认证覆盖集，并枚举出最少站位。

为什么改用环组
--------------
贪心集合覆盖在这个问题上失效：认证一个候选点需要**至少 3 个环绕读数**，
所以单个站位的"边际增益"恒为 0，贪心第一步就无从下手。

而问题具有旋转对称性，最优布局几乎必然是**同心环组**：
    中心 1 个 + 若干环，每个环上 n_k 个点均匀分布。
于是只要枚举 (半径, 个数) 的组合，就能直接评估"这些站位能认证多少候选点"。

认证判据（定理 2，与 robot_core 中一致）：
    q 被排除 <=> q 落在 {p - q : |p-q| <= R} 的凸包内部。

评价指标：认证网格（间距 60 m、r <= 1800 - margin）中被认证的比例，
以及**站位总数**与**巡回长度**（后者决定时间）。

usage: python ring_design.py [grid] [margin]
"""
import itertools
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
R = 1000.0 - 60.0 * 0.7072          # 认证半径 957.6 m


def inside_hull(pts):
    """原点是否在 pts 的凸包内部。"""
    n = len(pts)
    if n < 3:
        return False
    ang = sorted(math.atan2(y, x) for (x, y) in pts)
    # 原点在凸包内 <=> 不存在一条过原点的线使所有点在同侧
    # 等价于：按极角排序后，相邻点夹角的最大值 < pi
    gaps = [ang[i + 1] - ang[i] for i in range(n - 1)]
    gaps.append(ang[0] + 2 * math.pi - ang[-1])
    return max(gaps) < math.pi - 1e-9


def make_stops(spec):
    """spec: [(radius, count), ...]，count=0 表示圆心一个点。"""
    out = []
    for r, c in spec:
        if c <= 0 or r <= 0:
            out.append((0.0, 0.0))
            continue
        for k in range(c):
            a = 2.0 * math.pi * k / c
            out.append((r * math.cos(a), r * math.sin(a)))
    return out


def evaluate(stops, Q):
    R2 = R * R
    ok = 0
    for q in Q:
        pts = [(p[0] - q[0], p[1] - q[1]) for p in stops
               if (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 <= R2]
        if inside_hull(pts):
            ok += 1
    return ok


def tour_len(pts, start=(0.0, 0.0)):
    """最近邻巡回长度（站位数量少时够用）。"""
    rest = list(pts)
    cur, tot = start, 0.0
    while rest:
        i = min(range(len(rest)),
                key=lambda k: (rest[k][0] - cur[0]) ** 2 + (rest[k][1] - cur[1]) ** 2)
        nxt = rest.pop(i)
        tot += math.hypot(nxt[0] - cur[0], nxt[1] - cur[1])
        cur = nxt
    return tot


if __name__ == "__main__":
    g = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
    margin = float(sys.argv[2]) if len(sys.argv) > 2 else 90.0
    lim = 1800.0 - margin
    Q = []
    n = int(lim / g) + 1
    for iy in range(-n, n + 1):
        for ix in range(-n, n + 1):
            x, y = ix * g, iy * g
            if x * x + y * y <= lim * lim:
                Q.append((x, y))
    print("certification grid: %d points (r <= %.0f), R = %.1f m"
          % (len(Q), lim, R), flush=True)

    CANDIDATES = [
        [(0, 0)],
        [(0, 0), (900, 6)],
        [(0, 0), (957, 6)],
        [(900, 6), (1600, 12)],
        [(957, 6), (1658, 12)],
        [(0, 0), (900, 6), (1650, 12)],
        [(700, 6), (1400, 12)],
        [(800, 6), (1550, 12)],
        [(850, 6), (1600, 12)],
        [(900, 6), (1700, 12)],
        [(957, 6), (1750, 12)],
        [(0, 0), (700, 6), (1400, 12)],
        [(750, 6), (1450, 12), (1800, 6)],
        [(850, 8), (1600, 12)],
        [(900, 10), (1650, 14)],
    ]
    rows = []
    for spec in CANDIDATES:
        stops = make_stops(spec)
        t0 = time.time()
        ok = evaluate(stops, Q)
        tl = tour_len(stops)
        rows.append({"spec": spec, "n": len(stops), "certified": ok,
                     "frac": ok / float(len(Q)), "tour": tl,
                     "time_at_5ms": tl / 5.0,
                     "secs": time.time() - t0})
        print("%-42s n=%2d  certified %5d/%5d (%6.2f%%)  tour %6.0f m  "
              "%.0f s" % (str(spec), len(stops), ok, len(Q),
                          100.0 * ok / len(Q), tl, tl / 5.0), flush=True)
    rows.sort(key=lambda r: (-r["frac"], r["n"]))
    print("\nbest by coverage then size:")
    for r in rows[:5]:
        print("   %-40s n=%2d  %.2f%%  tour %.0f m"
              % (str(r["spec"]), r["n"], 100 * r["frac"], r["tour"]))
    full = [r for r in rows if r["frac"] > 0.999]
    if full:
        b = min(full, key=lambda r: r["n"])
        print("\nSMALLEST FULLY CERTIFYING: %s  (%d stops, tour %.0f m)"
              % (str(b["spec"]), b["n"], b["tour"]))
    with open(os.path.join(DATA, "ring_design.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    print("report -> data/ring_design.json")
