# -*- coding: utf-8 -*-
"""
trace_case.py -- step-by-step trace of the terminal clearing of the channel that
case seed=30017 misses (true position (92,1409), estimate (111,1401) i.e. 20.6 m
away, sigma 77 m, clear radius 20 m).
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
P = dict(rc.DEFAULT_PARAMS, survey_mode="lattice", survey_spacing=1100.0,
         directional=True)
for k in ("survey_spacing", "probe_spacing", "locate_sigma", "clear_bonus",
          "probe_min_angle", "search_cost_bias", "max_attempts"):
    if k in TUNED:
        P[k] = TUNED[k]

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 30017
    chan = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    srcs = sim.make_case(random.Random(seed), kind_mix=0.5)
    tgt = [s for s in srcs if s.channel == chan][0]
    print("target channel %d at (%.1f, %.1f) r=%.1f kind=%s dir=%s R_eff=%.1f"
          % (chan, tgt.x, tgt.y, math.hypot(tgt.x, tgt.y), tgt.kind,
             tgt.direction, tgt.r_eff))

    ar = sim.Arena(srcs, seed=seed)
    br = rc.Brain(rc.LocalClient(ar), params=P, seed=seed)
    br.debug_channel = chan          # turns on the per-iteration trace
    orig_clear = br.clear_channel
    calls = {"n": 0}

    def wrapped_clear(c):
        if c != chan:
            return orig_clear(c)
        calls["n"] += 1
        est = br.est.get(c)
        d_true = math.hypot(br.pos[0] - tgt.x, br.pos[1] - tgt.y)
        print("\n>>> clear_channel(%d) call #%d  pos=(%.1f,%.1f)  "
              "dist to TRUE source = %.1f m" % (c, calls["n"], br.pos[0],
                                                br.pos[1], d_true))
        if est:
            print("    estimate (%0.1f, %0.1f) sigma=%.1f  est error=%.1f m"
                  % (est[0], est[1], est[2],
                     math.hypot(est[0] - tgt.x, est[1] - tgt.y)))
        r = orig_clear(c)
        print("<<< returned %s   pos=(%.1f,%.1f)   dist to TRUE = %.1f m"
              % (r, br.pos[0], br.pos[1],
                 math.hypot(br.pos[0] - tgt.x, br.pos[1] - tgt.y)))
        return r

    br.clear_channel = wrapped_clear
    st = br.run()
    print("\nRESULT ratio=%.3f cleared=%d/%d mean=%.1f s travel=%.0f m"
          % (st["clear_ratio"], st["n_cleared"], st["n_sources"],
             st["mean_time"], st["travel_m"]))
    print("channel %d cleared=%s attempts=%s total=%s"
          % (chan, tgt.cleared, br.attempts.get(chan), br.total_attempts.get(chan)))
