#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
probe_failures.py -- examine the cases the tuned strategy fails on, and check
whether the rim patrol or a different setting rescues them.

The drill pool uses seeds 30000 + case index (see make_data.run_cases), so the
failing cases can be reproduced exactly.
"""
import json
import os
import random
import sys

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))

TUNED = {}
p = os.path.join(OUT, "optimize_q4.json")
if os.path.exists(p):
    with open(p, encoding="utf-8") as f:
        TUNED = json.load(f)["params"]

BASE = dict(rc.DEFAULT_PARAMS, survey_mode="lattice", survey_spacing=1000.0,
            directional=True)
for k in ("survey_spacing", "probe_spacing", "locate_sigma", "clear_bonus",
          "probe_min_angle", "search_cost_bias", "max_attempts", "rim_step",
          "max_rim_patrols"):
    if k in TUNED:
        BASE[k] = TUNED[k]

BAD = [5, 21, 32, 45]                      # failing case indices in the drill pool


def run(idx, params, mix=0.5):
    seed = 30000 + idx
    srcs = sim.make_case(random.Random(seed), kind_mix=mix)
    st, _ = rc.run_case(srcs, params=params, seed=seed)
    return st, srcs


if __name__ == "__main__":
    variants = [
        ("tuned (rim on)", {}),
        ("rim off", {"rim_patrol": False}),
        ("rim trips<=4", {"max_rim_patrols": 4}),
        ("rim_step 300", {"rim_step": 300.0}),
    ]
    for idx in BAD:
        print("=== case %d (seed %d)" % (idx, 30000 + idx), flush=True)
        for tag, ov in variants:
            st, srcs = run(idx, dict(BASE, **ov))
            missed = [(s.channel, round(s.x), round(s.y), s.kind,
                       None if s.direction is None else round(s.direction),
                       round((s.x ** 2 + s.y ** 2) ** 0.5))
                      for s in srcs if not s.cleared]
            print("   %-16s ratio=%.3f time=%7.1f travel=%7.0f  missed=%s"
                  % (tag, st["clear_ratio"], st["mean_time"], st["travel_m"],
                     missed), flush=True)
