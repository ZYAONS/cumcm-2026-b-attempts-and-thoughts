#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
"""
minimal_lattice.py -- 认证只需要"覆盖 r<=1100"，那只需约 5 个格点。

关键推理
--------
认证边距为 700 时，只要求认证 $r\le1100$ 的区域（边界发现交给贴边环）。
而这个区域的认证只需覆盖半径 $\le R=958$ m，即
    $$\pi\cdot1100^2/(0.866\cdot958^2)=4.9$$
**约 5 个格点就够**。当前用了 12.9 个（因为它覆盖的是整个 $r\le1800$ 的圆盘）。

也就是说：**格点的大部分站位其实是在做"发现"，而不是"认证"**。
而发现完全可以由**清除巡回沿途的测量**承担——那段路本来就要走。

本站位集合 = 5 个认证格点 + 贴边环（边界发现）+ 清除巡回沿途采样。

usage: python minimal_lattice.py [n_per_pool]
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

POOLS = [("A", 62000), ("B", 51000)]


def cfg(cap, rim_n, spacing=950.0, margin=700.0, probe=250.0):
    return dict(P4, survey_mode="lattice", survey_spacing=spacing,
                max_survey_stops=cap, rim_ring_n=rim_n, verify_margin=margin,
                probe_spacing=probe, max_search_stops=40)


CANDS = [
    ("cap0 rim6 (now-ish)", cfg(0, 6)),
    ("cap12 rim6", cfg(12, 6)),
    ("cap10 rim6", cfg(10, 6)),
    ("cap8 rim6", cfg(8, 6)),
    ("cap6 rim6", cfg(6, 6)),
    ("cap6 rim10", cfg(6, 10)),
    ("cap6 rim12", cfg(6, 12)),
    ("cap8 rim8 ps150", cfg(8, 8, probe=150.0)),
    ("cap6 rim12 ps150", cfg(6, 12, probe=150.0)),
]


def ev(c, seeds):
    p = dict(rc.DEFAULT_PARAMS)
    p.update(c)
    rs, ts, tr, meas, stops = [], [], [], [], []
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=p, seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
        meas.append(st["n_measure"])
        stops.append(len(br.visited_stops))
    return {"ratio": statistics.mean(rs), "min": min(rs),
            "fails": sum(1 for r in rs if r < 0.9999),
            "time": statistics.mean(ts), "travel": statistics.mean(tr),
            "measure": statistics.mean(meas), "stops": statistics.mean(stops)}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    res = {}
    for tag, c in CANDS:
        acc = {"ratio": [], "time": [], "fails": 0, "stops": [], "travel": [],
               "measure": []}
        for pname, s0 in POOLS:
            r = ev(c, list(range(s0, s0 + n)))
            for k in ("ratio", "time", "stops", "travel", "measure"):
                acc[k].append(r[k])
            acc["fails"] += r["fails"]
        res[tag] = {"worst": min(acc["ratio"]),
                    "time": statistics.mean(acc["time"]), "fails": acc["fails"],
                    "stops": statistics.mean(acc["stops"]),
                    "travel": statistics.mean(acc["travel"]),
                    "measure": statistics.mean(acc["measure"])}
        print("%-20s worst=%.4f  time=%6.1f s  stops=%5.1f  travel=%6.0f  "
              "meas=%5.0f  failing=%d/%d"
              % (tag, res[tag]["worst"], res[tag]["time"], res[tag]["stops"],
                 res[tag]["travel"], res[tag]["measure"], res[tag]["fails"],
                 n * len(POOLS)), flush=True)
    with open(os.path.join(DATA, "minimal_lattice.json"), "w",
              encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("report -> data/minimal_lattice.json")
