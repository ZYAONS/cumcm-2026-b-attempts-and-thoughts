#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
diagnose_loss.py -- why does the strategy still miss a source?

For every missed source of a failing case it reports the geometry (radius, kind,
radiation direction) and the whole history of that channel: how often it was
measured, what came back, whether a bearing was ever obtained, the final
knowledge state, and whether the certification scan ever ruled it out.

usage: python diagnose_loss.py [mode] [n_cases] [seed0] [mix]
       mode = q4 | q3
"""
import json
import math
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
P4 = dict(rc.DEFAULT_PARAMS, survey_mode="lattice", survey_spacing=1100.0,
          directional=True)
for k in ("survey_spacing", "probe_spacing", "locate_sigma", "clear_bonus",
          "probe_min_angle", "search_cost_bias", "max_attempts"):
    if k in TUNED:
        P4[k] = TUNED[k]
P3 = dict(rc.DEFAULT_PARAMS, survey_mode="ring", ring_radius=1250.0)


def run(mode, seed, mix):
    srcs = sim.make_case(random.Random(seed), kind_mix=mix)
    ar = sim.Arena(srcs, seed=seed)
    br = rc.Brain(rc.LocalClient(ar), params=(P3 if mode == "q3" else P4),
                  seed=seed)
    st = br.run()
    return st, srcs, br, ar


def describe(mode, seed, mix):
    st, srcs, br, ar = run(mode, seed, mix)
    missed = [s for s in srcs if not s.cleared]
    if not missed:
        return None
    print("=" * 78)
    print("case seed=%d  n=%d  cleared=%d  ratio=%.3f  mean=%.1f s  travel=%.0f m"
          % (seed, len(srcs), st["n_cleared"], st["clear_ratio"], st["mean_time"],
             st["travel_m"]), flush=True)
    for s in missed:
        c = s.channel
        obs = br.obs.get(c, [])
        nos = br.nosig.get(c, [])
        r = math.hypot(s.x, s.y)
        print("  --- channel %d  MISSED" % c)
        print("      true: pos=(%.0f,%.0f) r=%.0f m  kind=%s  dir=%s  R_eff=%.0f m"
              % (s.x, s.y, r, s.kind,
                 "None" if s.direction is None else "%.0f deg" % s.direction,
                 s.r_eff))
        print("      knowledge: status=%s  n_obs=%d  n_nosig=%d  est=%s"
              % (br.status.get(c), len(obs), len(nos),
                 None if br.est.get(c) is None
                 else tuple(round(v) for v in br.est[c])))
        print("      last task counters: attempts=%s total=%s vantage=%s"
              % (br.attempts.get(c), br.total_attempts.get(c),
                 br.vantage_tries.get(c)))
        # was it ever inside any measurement footprint?
        inside = 0
        for (x, y, t) in [(o[0], o[1], None) for o in obs] + \
                         [(n[0], n[1], None) for n in nos]:
            if math.hypot(x - s.x, y - s.y) <= s.r_eff:
                inside += 1
        print("      measured positions inside the reception radius: %d / %d"
              % (inside, len(obs) + len(nos)))
        if s.kind == "directional":
            lit = 0
            for (x, y, _) in [(o[0], o[1], None) for o in obs] + \
                             [(n[0], n[1], None) for n in nos]:
                if math.hypot(x - s.x, y - s.y) <= s.r_eff and s.covers(x, y):
                    lit += 1
            print("      ... of which on the LIT side: %d" % lit)
        flags = {}
        ok, uncov, flags = br.certification_scan(
            [c for c in br.channels if br.status[c] not in ("cleared", "empty")])
        near_q = [q for q in uncov
                  if math.hypot(q[0] - s.x, q[1] - s.y) <= 120.0]
        print("      certification: ruled_out=%s  uncovered points near the "
              "true position: %d" % (flags.get(c), len(near_q)))
    return st


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "q4"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed0 = int(sys.argv[3]) if len(sys.argv) > 3 else 30000
    mix = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
    nfail = 0
    for i in range(n):
        if describe(mode, seed0 + i, mix) is not None:
            nfail += 1
            if nfail >= 3:
                break
    print("(stopped after %d failing cases)" % nfail)
