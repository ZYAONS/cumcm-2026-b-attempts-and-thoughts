#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""xcheck_q1.py -- 与公开仓库 li2396803/cumcm2026-b-radio-interference-localization
的问题一结果交叉核对（性能友好版）。

对方报告：直径圆覆盖率 96.6 / 86.0 / 80.0 / 74.2 %（n=2/3/4/5）；
          环绕场景 n=3/4/5 只有 40.6 / 58.9 / 36.2 %。
我们此前报告：失效 1.13 / 2.50 / 3.00 / 3.70 %（覆盖 98.87 / 97.50 / 97.00 / 96.30 %）。

统一判据（Thales），统一目标圆域用 60 边形外近似（半径 1800 m 时外扩误差 2.5 m）。
"""
import math
import random
import statistics
import time

import geom_core as g

ARENA = 1800.0
EPS = 1.0
NGON = 60
DISK_HP = [(math.cos(2 * math.pi * k / NGON), math.sin(2 * math.pi * k / NGON), ARENA)
           for k in range(NGON)]


def make_region(stations, bearings, disk):
    hp = g.halfplanes_from_bearings(stations, bearings, EPS)
    if disk:
        hp = hp + DISK_HP
    verts = g.polygon_vertices(hp)
    return verts if verts and len(verts) >= 3 else None


def covered(verts):
    d, (A, B) = g.polygon_diameter(verts)
    others = [v for v in verts if math.dist(v, A) > 1e-6 and math.dist(v, B) > 1e-6]
    if not others:
        return True, d, 0.0
    slack = g.diameter_disk_slack(others, A, B)
    mec = g.min_enclosing_circle(verts)
    return slack <= 1e-9, d, mec[2] / (d / 2.0) if d > 0 else 1.0


def rp(rnd, rmax=ARENA):
    r = rmax * math.sqrt(rnd.random())
    a = 2 * math.pi * rnd.random()
    return (r * math.cos(a), r * math.sin(a))


def e1(rnd, n):            # 我们的算例集合
    sts = [rp(rnd) for _ in range(n)]
    if min(math.dist(a, b) for i, a in enumerate(sts) for b in sts[i + 1:]) < 200:
        return None
    G = rp(rnd)
    if min(math.dist(s, G) for s in sts) < 30 or max(math.dist(s, G) for s in sts) > 1500:
        return None
    return sts, G, False


def e2(rnd, n):            # 对方的算例集合：都均匀随机落域内
    sts = [rp(rnd) for _ in range(n)]
    if min(math.dist(a, b) for i, a in enumerate(sts) for b in sts[i + 1:]) < 50:
        return None
    G = rp(rnd)
    if min(math.dist(s, G) for s in sts) < 5:
        return None
    return sts, G, True


def e3(rnd, n):            # 对方场景 B：检测点环绕源
    G = rp(rnd, ARENA * 0.7)
    base = 2 * math.pi * rnd.random()
    sts = []
    for k in range(n):
        a = base + 2 * math.pi * k / n + rnd.uniform(-0.2, 0.2)
        r = rnd.uniform(400.0, 1500.0)
        sts.append((G[0] + r * math.cos(a), G[1] + r * math.sin(a)))
    return sts, G, True


def run(fn, n, trials=600, seed=7):
    rnd = random.Random(seed)
    cnt = ok = unb = 0
    ratios, diam = [], []
    while cnt < trials:
        out = fn(rnd, n)
        if out is None:
            continue
        sts, G, disk = out
        bs = [g.bearing(s[0], s[1], G[0], G[1]) for s in sts]
        if not disk and not g.is_bounded(bs, EPS):
            unb += 1
            cnt += 1
            continue
        verts = make_region(sts, bs, disk)
        cnt += 1
        if verts is None:
            continue
        good, d, ratio = covered(verts)
        ok += 1 if good else 0
        diam.append(d)
        ratios.append(ratio)
    denom = max(cnt - unb, 1)
    return {"cover": 100.0 * ok / denom, "unb": 100.0 * unb / cnt,
            "maxr": max(ratios) if ratios else -1,
            "diam": statistics.mean(diam) if diam else -1}


def main():
    t0 = time.time()
    print("对方报告：覆盖 96.6 / 86.0 / 80.0 / 74.2 %% | 环绕 99.3 / 40.6 / 58.9 / 36.2 %%")
    print("%-5s | %-26s | %-26s | %-26s" % ("n", "E1 我们(纯楔形交)", "E2 对方集合(∩圆域)", "E3 环绕源(∩圆域)"))
    print("-" * 96)
    for n in (2, 3, 4, 5):
        r1 = run(e1, n)
        r2 = run(e2, n)
        r3 = run(e3, n)
        print("n=%-3d | 覆盖%6.1f%% 无界%5.1f%% D=%5.0f | 覆盖%6.1f%% 无界%5.1f%% D=%5.0f | 覆盖%6.1f%% D=%5.0f"
              % (n, r1["cover"], r1["unb"], r1["diam"],
                 r2["cover"], r2["unb"], r2["diam"], r3["cover"], r3["diam"]), flush=True)
    print()
    print("最大 2R*/D（Jung 上界 1.1547）：")
    for n in (2, 3, 4, 5):
        r1 = run(e1, n, trials=600)
        r2 = run(e2, n, trials=600)
        r3 = run(e3, n, trials=600)
        print("  n=%d  E1 %.4f   E2 %.4f   E3 %.4f" % (n, r1["maxr"], r2["maxr"], r3["maxr"]))
    print("elapsed %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
