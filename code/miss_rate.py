#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
miss_rate.py -- 在全新算例池上核实真实的漏源率，并判定漏源是否都是几何极限。

正式测试的种子 950001~950003 中出现 2 例未清完，密度看似高于四池验证（1/120 例）。
必须核实：是新种子池"贴边朝外源"更多，还是存在回归。

对每个漏源输出：半径、朝向与朝外径向的夹角余弦、其域内受光区占比。
若全部是"dot ≈ 1 且受光区 < 1%"，则属于问题固有的几何极限。

usage: python miss_rate.py [n_cases] [seed0]
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


def lit_fraction(s):
    tot = lit = 0
    for i in range(120):
        for j in range(120):
            x = -1800 + 30.0 * i
            y = -1800 + 30.0 * j
            if math.hypot(x, y) <= 1800:
                tot += 1
                if s.covers(x, y):
                    lit += 1
    return 100.0 * lit / max(tot, 1)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 70000
    tot = missed = 0
    times, rows = [], []
    for sd in range(seed0, seed0 + n):
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=dict(rc.DEFAULT_PARAMS, **P4),
                      seed=sd)
        st = br.run()
        times.append(st["mean_time"])
        tot += len(srcs)
        for s in srcs:
            if not s.cleared:
                missed += 1
                r = math.hypot(s.x, s.y)
                d0 = s.direction if s.direction is not None else 0.0
                u = (math.cos(math.radians(d0)), math.sin(math.radians(d0)))
                dot = u[0] * s.x / r + u[1] * s.y / r if r > 1 else 0.0
                lf = lit_fraction(s)
                rows.append({"seed": sd, "ch": s.channel, "r": round(r),
                             "kind": s.kind,
                             "dir": None if s.direction is None
                             else round(s.direction),
                             "dot": round(dot, 3), "lit_pct": round(lf, 3),
                             "r_eff": round(s.r_eff),
                             "status": br.status.get(s.channel)})
    print("pool %d..%d : %d cases, %d sources, %d missed (%.3f%% of sources)"
          % (seed0, seed0 + n - 1, n, tot, missed, 100.0 * missed / tot))
    print("mean time %.1f s/source" % statistics.mean(times))
    for m in rows:
        print("   seed %d ch%2d r=%4d %-11s dir=%-4s R_eff=%4d  dot=%+.3f  "
              "lit=%5.2f%%  status=%s"
              % (m["seed"], m["ch"], m["r"], m["kind"], m["dir"], m["r_eff"],
                 m["dot"], m["lit_pct"], m["status"]))
    geo = [m for m in rows if m["dot"] > 0.8 and m["lit_pct"] < 1.0]
    print("\nof the %d missed, %d are rim-outward (dot>0.8) with a lit region "
          "under 1%% of the arena -- the documented geometric limit"
          % (len(rows), len(geo)))
    with open(os.path.join(DATA, "miss_rate.json"), "w", encoding="utf-8") as f:
        json.dump({"n": n, "total": tot, "missed": missed, "rows": rows},
                  f, ensure_ascii=False, indent=1)
    print("report -> data/miss_rate.json")
