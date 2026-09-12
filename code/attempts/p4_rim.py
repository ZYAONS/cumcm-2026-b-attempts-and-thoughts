#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
p4_rim.py -- 论文配置 + 贴边环：能否把最后一例"贴边朝外、从未听到"的源找回来？

背景（四池 120 例 A/B）：
    本轮改动前  漏 3 个源 / 3 例失败 / 平均 885.3 s
    本轮改动后  漏 1 个源 / 1 例失败 / 平均 880.7 s
    仅剩的一例：seed 51029 ch2，r=1780、定向 348°、从未听到、
               却被认证判为"不存在"（status=empty）。

原因清楚：P4 的认证网格边距把 r>1710 的候选点排除，因此**扫描不会为贴边区域
专门布站**；而朝外辐射的贴边源，其域内受光区是一条薄月牙，格点扫描极难碰上。

贴边环正是为这种情况设计的（它只服务于发现，与认证边距无关）。

usage: python p4_rim.py [n_per_pool]
"""
import json
import os
import random
import statistics
import sys

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
from make_data import P4  # noqa: E402

POOLS = [("A", 62000), ("B", 51000), ("C", 12000), ("D", 30000)]
CANDS = [("rim0", {}),
         ("rim12", {"rim_ring_n": 12}),
         ("rim16", {"rim_ring_n": 16}),
         ("rim20", {"rim_ring_n": 20}),
         ("rim24", {"rim_ring_n": 24}),
         ("rim16 r1600", {"rim_ring_n": 16, "rim_ring_r": 1600.0}),
         ("rim16 r1700", {"rim_ring_n": 16, "rim_ring_r": 1700.0}),
         ("rim20 r1650", {"rim_ring_n": 20, "rim_ring_r": 1650.0})]


def run(seeds, ov):
    cfg = dict(P4)
    cfg.update(ov)
    rs, ts, miss = [], [], []
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=dict(rc.DEFAULT_PARAMS, **cfg),
                      seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        for s in srcs:
            if not s.cleared:
                miss.append((sd, s.channel))
    return statistics.mean(rs), min(rs), sum(1 for r in rs if r < 0.9999), \
        statistics.mean(ts), miss


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    out = {}
    for tag, ov in CANDS:
        tot, f, tt, mm = [], 0, [], []
        for name, s0 in POOLS:
            r, mn, fl, t, ms = run(list(range(s0, s0 + n)), ov)
            tot.append(r)
            f += fl
            tt.append(t)
            mm += ms
        out[tag] = {"worst": min(tot), "mean_time": statistics.mean(tt),
                    "fails": f, "missed": len(mm)}
        print("%-14s worst=%.4f mean_time=%7.1f s  failing=%2d/%d  missed=%d"
              % (tag, min(tot), statistics.mean(tt), f, n * len(POOLS), len(mm)),
              flush=True)
    with open(os.path.join(DATA, "p4_rim.json"), "w", encoding="utf-8") as fp:
        json.dump(out, fp, ensure_ascii=False, indent=1)
    print("report -> data/p4_rim.json")
