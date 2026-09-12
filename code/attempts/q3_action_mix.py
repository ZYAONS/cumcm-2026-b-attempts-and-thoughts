#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""q3_action_mix.py -- 当前问题三配置下，动作总数按用途拆分（20 例）。

目的：与公开仓库的"平均请求数 140"对比，找出我们动作数偏高的环节。
"""
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import robot_core as rc
import simulator as sim
from make_data import P3


def one(seed):
    srcs = sim.make_case(random.Random(seed), kind_mix=0.0)
    arena = sim.Arena(srcs, seed=seed)
    cl = rc.LocalClient(arena)
    p = dict(rc.DEFAULT_PARAMS); p.update(P3)
    brain = rc.Brain(cl, params=p, seed=seed)
    cat = {"census": 0, "search": 0, "track": 0, "vantage": 0, "clear": 0}
    om, oc = brain.move_measure, brain.move_clear

    def m2(x, y, c):
        r = om(x, y, c)
        t = brain._cur_task
        if t == "clear":
            # 清除任务里的检测：若该频道已在追踪中则记 track，否则记 search
            cat["track" if brain.obs[c] else "search"] += 1
        elif t == "localise":
            cat["vantage"] += 1
        elif t == "census":
            cat["census"] += 1
        else:
            cat["search"] += 1
        return r

    def c2(x, y, c):
        r = oc(x, y, c)
        cat["clear"] += 1
        return r
    brain.move_measure, brain.move_clear = m2, c2
    st = brain.run()
    st.update(arena.stats())
    brain.task_debug = cat
    arena.close()
    return st, cat


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    rows = []
    for k in range(n):
        rows.append(one(20000 + k))
    tot = {}
    for c in ("census", "search", "track", "vantage", "clear"):
        tot[c] = statistics.mean(r[1][c] for r in rows)
    acts = sum(tot.values())
    src = statistics.mean(r[0]["n_sources"] for r in rows)
    t = statistics.mean(r[0]["mean_time"] for r in rows)
    print("源/例 %.1f   平均 %.1f s/源   论文口径 %.1f" % (src, t, t))
    print("动作总数 %.1f 次 = 检测 %.1f + 清除 %.1f" % (acts, acts - tot["clear"], tot["clear"]))
    for c in ("census", "search", "track", "vantage", "clear"):
        print("   %-8s %6.1f 次  (%.1f s)" % (c, tot[c], tot[c] * 6.0))
    print("对照：公开仓库问题三平均请求数 140（含 enter/exit）")


if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.0f s" % (time.time() - t0))
