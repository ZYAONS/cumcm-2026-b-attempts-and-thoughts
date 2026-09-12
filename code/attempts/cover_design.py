#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cover_design.py -- 离线求解"认证全域所需的最少站位"（贪心集合覆盖）。

思路
----
当前站位来自三处拼凑：间距 1100 的格点（7 站）、贴边环（16 站）、
认证搜索自适应补站（约 1.5 站），合计 24.5 站。而几何上的下界只有约 13 站：

    间距 s 的三角格点，若 s <= 认证半径 958 m，则任意候选点所在格点三角形的
    三个顶点都在认证半径内且包围它 —— 于是全域可认证。
    所需站位数 = pi*1800^2 / (0.866*958^2) = 12.8

也就是说**理论上 13 站就够**，而实现用了 24.5 站。

认证判据（定理 2）是精确的：
    候选点 q 被排除  <=>  q 落在"半径 R 内的读数点相对 q 的坐标"凸包的内部
（全向源只需存在一个 R 内的读数点）。

于是"最少站位"就是一个标准的**集合覆盖问题**：
    地面元素 = 认证网格点 Q（间距 60 m，r <= arena_r - margin）
    集合      = 每个候选站位 p 能认证的 Q 的子集
    目标      = 用最少（或最小代价）的 p 覆盖 Q

用贪心（每次选"单位代价新覆盖最多"的 p）即可得到接近最优解。
本脚本离线算出这样一组站位，供 survey_mode = "cover" 使用。

usage: python cover_design.py [grid] [stop_grid] [margin]
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


def origin_inside_hull(pts):
    """q 是否为原点：原点是否落在 pts 的凸包内部（严格）。pts 已相对 q 平移。"""
    n = len(pts)
    if n < 3:
        return False
    # 若原点在某个方向的极值之外，做角度排序后用"同侧"判据
    ang = sorted((math.atan2(y, x), x, y) for (x, y) in pts)
    if n == 3:
        x1, y1 = ang[0][1], ang[0][2]
        x2, y2 = ang[1][1], ang[1][2]
        x3, y3 = ang[2][1], ang[2][2]
        d1 = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
        return abs(d1) > 1e-9
    # 一般情形：原点是凸组合 <=> 存在两个点跨越 180 度以上
    # 实用判据：对每个点检查是否所有其它点都在过原点的某条线同侧
    for i in range(n):
        ax, ay = ang[i][1], ang[i][2]
        # 以 (ax,ay) 为基准，看是否存在一条过原点的线使全部点在闭半平面内
        for j in range(n):
            if i == j:
                continue
            bx, by = ang[j][1], ang[j][2]
            cr = ax * by - ay * bx
            if abs(cr) < 1e-12:
                continue
            pos = neg = 0
            for k in range(n):
                cx, cy = ang[k][1], ang[k][2]
                v = cr * 0 + (bx * cy - by * cx) * (1 if cr > 0 else -1)
                if v > 1e-12:
                    pos += 1
                elif v < -1e-12:
                    neg += 1
            if pos == 0 or neg == 0:
                return False
    return True


def design(grid=60.0, stop_grid=150.0, margin=90.0, arena=1800.0, R=957.6):
    t0 = time.time()
    lim = arena - margin
    Q = []
    n = int(lim / grid) + 1
    for iy in range(-n, n + 1):
        y = iy * grid
        for ix in range(-n, n + 1):
            x = ix * grid
            if x * x + y * y <= lim * lim:
                Q.append((x, y))
    # 站位候选取在更大的可行域上（可以贴到边界）
    P = []
    m = int(arena / stop_grid) + 1
    for iy in range(-m, m + 1):
        y = iy * stop_grid
        for ix in range(-m, m + 1):
            x = ix * stop_grid
            if x * x + y * y <= arena * arena:
                P.append((x, y))
    print("grid points %d, stop candidates %d (%.1f s to build)"
          % (len(Q), len(P), time.time() - t0), flush=True)

    # 每个站位能覆盖哪些网格点（索引）
    covers = []
    R2 = R * R
    for p in P:
        idx = [j for j, q in enumerate(Q)
               if (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 <= R2]
        covers.append(idx)
    print("coverage pairs built (%.1f s)" % (time.time() - t0), flush=True)

    # 预先算好每个网格点邻域内的站位（用于精确认证判定）
    nearP = []
    for q in Q:
        nearP.append([i for i, p in enumerate(P)
                      if (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 <= R2])
    print("near-stop lists built (%.1f s)" % (time.time() - t0), flush=True)

    def certifies(qi, chosen_set):
        q = Q[qi]
        pts = [(P[i][0] - q[0], P[i][1] - q[1]) for i in nearP[qi]
               if i in chosen_set]
        return origin_inside_hull(pts)

    chosen = set()
    chosen_list = []
    uncov = set(range(len(Q)))
    # 贪心：每轮选择"能认证最多未覆盖点"的站位
    while uncov:
        best_i, best_gain = None, 0
        for i in range(len(P)):
            gain = 0
            for j in covers[i]:
                if j in uncov:
                    gain += 1
            if gain > best_gain:
                best_gain, best_i = gain, i
        if best_i is None or best_gain == 0:
            break
        # 精确复核：加入后真正被认证的点
        chosen.add(best_i)
        new_cov = set()
        for j in list(uncov):
            if certifies(j, chosen):
                new_cov.add(j)
        if not new_cov:
            chosen.discard(best_i)
            break
        chosen_list.append(P[best_i])
        uncov -= new_cov
        if len(chosen_list) % 5 == 0 or not uncov:
            print("  stops=%2d  uncovered=%5d  (%.1f s)"
                  % (len(chosen_list), len(uncov), time.time() - t0), flush=True)
    return chosen_list, len(Q), len(uncov)


if __name__ == "__main__":
    g = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
    sg = float(sys.argv[2]) if len(sys.argv) > 2 else 150.0
    mg = float(sys.argv[3]) if len(sys.argv) > 3 else 90.0
    stops, nq, left = design(g, sg, mg)
    print("\nRESULT: %d stops certify %d of %d grid points (%d left)"
          % (len(stops), nq - left, nq, left))
    rr = sorted(round(math.hypot(p[0], p[1])) for p in stops)
    print("radii: %s" % rr)
    with open(os.path.join(DATA, "cover_design.json"), "w", encoding="utf-8") as f:
        json.dump({"stops": stops, "n_grid": nq, "uncovered": left},
                  f, ensure_ascii=False, indent=1)
    print("report -> data/cover_design.json")
