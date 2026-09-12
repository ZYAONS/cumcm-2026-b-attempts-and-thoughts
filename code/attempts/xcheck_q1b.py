#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""xcheck_q1b.py -- 进一步定位与公开仓库的差异来源。

三种假设：
  H1 对方场景 B 用的是"等半径正多边形环绕"（而非我上一版 400~1500 m 随机半径），
     此时定位区域接近正多边形 -> 直径圆必然失效（正五边形 R*=0.618D > 0.5D）。
  H2 对方统计时未与目标圆域求交，且把"无界"也算作不能覆盖。
  H3 差异来自他们用的判据/实现（需要对方代码复算）。
"""
import math
import random
import statistics

import geom_core as g

ARENA = 1800.0
EPS = 1.0
NGON = 60
DISK_HP = [(math.cos(2 * math.pi * k / NGON), math.sin(2 * math.pi * k / NGON), ARENA)
           for k in range(NGON)]


def rp(rnd, rmax=ARENA):
    r = rmax * math.sqrt(rnd.random())
    a = 2 * math.pi * rnd.random()
    return (r * math.cos(a), r * math.sin(a))


def analyse(sts, bs, disk):
    hp = g.halfplanes_from_bearings(sts, bs, EPS)
    if disk:
        hp = hp + DISK_HP
    verts = g.polygon_vertices(hp)
    if not verts or len(verts) < 3:
        return None
    d, (A, B) = g.polygon_diameter(verts)
    others = [v for v in verts if math.dist(v, A) > 1e-6 and math.dist(v, B) > 1e-6]
    slack = g.diameter_disk_slack(others, A, B) if others else -1.0
    mec = g.min_enclosing_circle(verts)
    return {"cover": slack <= 1e-9, "d": d, "ratio": mec[2] / (d / 2.0) if d else 1.0,
            "nv": len(verts)}


def sweep(fn, n, trials=400, seed=11):
    rnd = random.Random(seed)
    cnt = ok = unb = 0
    ds, rs = [], []
    while cnt < trials:
        out = fn(rnd, n)
        if out is None:
            continue
        sts, G, disk = out
        bs = [g.bearing(s[0], s[1], G[0], G[1]) for s in sts]
        if not g.is_bounded(bs, EPS):
            unb += 1
            if not disk:
                cnt += 1
                continue
        r = analyse(sts, bs, disk)
        cnt += 1
        if r is None:
            continue
        ok += 1 if r["cover"] else 0
        ds.append(r["d"])
        rs.append(r["ratio"])
    return {"cover": 100.0 * ok / max(cnt, 1), "unb": 100.0 * unb / max(cnt, 1),
            "d": statistics.mean(ds) if ds else -1,
            "ratio": max(rs) if rs else -1}


def reg_circle(rnd, n, radius):        # 等半径正 n 边形环绕
    G = rp(rnd, ARENA * 0.7)
    base = 2 * math.pi * rnd.random()
    sts = [(G[0] + radius * math.cos(base + 2 * math.pi * k / n),
            G[1] + radius * math.sin(base + 2 * math.pi * k / n)) for k in range(n)]
    return sts, G, True


def rand_circle(rnd, n):               # 半径随机的环绕
    G = rp(rnd, ARENA * 0.7)
    base = 2 * math.pi * rnd.random()
    sts = []
    for k in range(n):
        r = rnd.uniform(400.0, 1500.0)
        a = base + 2 * math.pi * k / n + rnd.uniform(-0.15, 0.15)
        sts.append((G[0] + r * math.cos(a), G[1] + r * math.sin(a)))
    return sts, G, True


def uniform_both(rnd, n, disk):
    sts = [rp(rnd) for _ in range(n)]
    G = rp(rnd)
    if min(math.dist(s, G) for s in sts) < 5:
        return None
    return sts, G, disk


def main():
    print("假设 H1：等半径正多边形环绕（对方场景 B 的严格形态）")
    for rad in (600.0, 1000.0, 1400.0):
        for n in (2, 3, 4, 5):
            r = sweep(lambda rr, k, rad=rad: reg_circle(rr, k, rad), n)
            print("   半径 %4.0f m  n=%d  覆盖 %6.1f%%  平均直径 %6.1f m  最大 2R*/D %.4f"
                  % (rad, n, r["cover"], r["d"], r["ratio"]), flush=True)
    print("   对方报告（场景 B）：n=3/4/5 覆盖 40.6 / 58.9 / 36.2 %%")
    print()
    print("假设 H2：域内均匀随机，不与目标圆域求交，无界计为不能覆盖")
    for n in (2, 3, 4, 5):
        a = sweep(lambda rr, k: uniform_both(rr, k, False), n)
        b = sweep(lambda rr, k: uniform_both(rr, k, True), n)
        print("   n=%d  不求交：覆盖 %6.1f%%（无界 %5.1f%%）   求交：覆盖 %6.1f%%"
              % (n, a["cover"], a["unb"], b["cover"]), flush=True)
    print("   对方报告（场景 A）：n=2/3/4/5 覆盖 96.6 / 86.0 / 80.0 / 74.2 %%")
    print()
    print("对照：随机半径环绕（我上一版算例）")
    for n in (2, 3, 4, 5):
        r = sweep(rand_circle, n)
        print("   n=%d 覆盖 %6.1f%%  平均直径 %5.1f m" % (n, r["cover"], r["d"]))


if __name__ == "__main__":
    main()
