#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
route_check.py -- s=900 全量扫描下，站位巡回还有多少余量？

stop_cap_scan 的结论：cap=19（全量）516.0 s、完成率 0.9928，只超出 500 s 约 16 s/源。
而 route_gap 曾测得：同样 19 个站位的 2-opt 巡回只需 16200 m，实际总行程 21640 m。
若其中属于"站位巡回"的部分能从实际值降到 2-opt 值，节省的行程足以把
516 s 压到 470 s 附近，从而**在不牺牲完成率的前提下进入 500 s**。

本脚本把 s=900 全量扫描下的行程按任务拆分，并单独计算
"实际访问的站位序列长度"与"同一批站位的 2-opt 巡回长度"。

usage: python route_check.py [n_cases] [seed0]
"""
import json
import math
import os
import random
import sys

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
from make_data import P4  # noqa: E402


def two_opt_len(seq, start=(0.0, 0.0)):
    def L(s):
        tot, cur = 0.0, start
        for q in s:
            tot += math.hypot(q[0] - cur[0], q[1] - cur[1])
            cur = q
        return tot
    best = list(seq)
    improved = True
    while improved:
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                cand = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                if L(cand) < L(best) - 1e-9:
                    best, improved = cand, True
    return L(best)


def analyse(seed):
    srcs = sim.make_case(random.Random(seed), kind_mix=0.5)
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    p.update({"survey_spacing": 900.0, "max_search_stops": 0,
              "verify_margin": 900.0, "periodic_cert_every": 1})
    ar = sim.Arena(srcs, seed=seed)
    br = rc.Brain(rc.LocalClient(ar), params=p, seed=seed)
    order, last = [], None
    orig = br.probe

    def wrapped(pos, force=False):
        if force:
            if last is not None:
                order.append((pos[0], pos[1]))
            else:
                order.append((pos[0], pos[1]))
            order[-1] = (pos[0], pos[1])
        return orig(pos, force=force)
    br.probe = wrapped
    st = br.run()
    stops = list(br.visited_stops)
    actual_seq = 0.0
    cur = (0.0, 0.0)
    for q in order:
        actual_seq += math.hypot(q[0] - cur[0], q[1] - cur[1])
        cur = q
    return {"sources": len(srcs), "ratio": st["clear_ratio"],
            "time": st["mean_time"], "travel": st["travel_m"],
            "probe_travel": st["task_travel"].get("probe", 0.0),
            "clear_travel": st["task_travel"].get("clear", 0.0),
            "localise_travel": st["task_travel"].get("localise", 0.0),
            "n_stops": len(stops), "seq_len": actual_seq,
            "opt_len": two_opt_len(stops)}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    agg = {}
    for i in range(n):
        r = analyse(seed0 + i)
        for k, v in r.items():
            agg[k] = agg.get(k, 0.0) + v
        print("seed %d: ratio=%.3f time=%.0f travel=%6.0f (probe %6.0f clear %5.0f "
              "loc %4.0f)  optimal tour over the %d stops = %6.0f m"
              % (seed0 + i, r["ratio"], r["time"], r["travel"], r["probe_travel"],
                 r["clear_travel"], r["localise_travel"], r["n_stops"],
                 r["opt_len"]), flush=True)
    c = float(n)
    print("\nMEAN: time %.1f s/source  ratio %.4f" % (agg["time"] / c, agg["ratio"] / c))
    print("  total travel %7.0f m  = probe %7.0f + clear %6.0f + localise %5.0f"
          % (agg["travel"] / c, agg["probe_travel"] / c, agg["clear_travel"] / c,
             agg["localise_travel"] / c))
    print("  2-opt tour over the same stops: %7.0f m  -> probe slack %6.0f m "
          "(%.0f s, %.1f s/source)"
          % (agg["opt_len"] / c,
             (agg["probe_travel"] - agg["opt_len"]) / c,
             (agg["probe_travel"] - agg["opt_len"]) / c / 5.0,
             (agg["probe_travel"] - agg["opt_len"]) / c / 5.0 / (agg["sources"] / c)))
    with open(os.path.join(DATA, "route_check.json"), "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=1)
