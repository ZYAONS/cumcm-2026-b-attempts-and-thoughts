# -*- coding: utf-8 -*-
"""
diag_seen.py -- why does a "seen but never located" channel stay that way?

Both residual failures (2 sources out of 914) are near-rim directional sources
with exactly ONE bearing: status stays "seen", no clear task is ever generated,
and the source is missed.  This script instruments the vantage (second station)
logic for such a channel:

  * how many vantage attempts were made and what the budget is
  * whether vantage_point() actually returns a point
  * how many vantage tasks the planner emitted

usage: python diag_seen.py [seed] [channel]
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

P = dict(rc.DEFAULT_PARAMS)
P.update(P4)

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 100006
    chan = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    srcs = sim.make_case(random.Random(seed), kind_mix=0.5)
    tgt = [s for s in srcs if s.channel == chan][0]
    print("target ch%d at (%.0f, %.0f) r=%.0f kind=%s dir=%.0f R_eff=%.0f"
          % (chan, tgt.x, tgt.y, math.hypot(tgt.x, tgt.y), tgt.kind,
             tgt.direction or -1, tgt.r_eff))

    ar = sim.Arena(srcs, seed=seed)
    br = rc.Brain(rc.LocalClient(ar), params=P, seed=seed)
    stats = {"vantage_emitted": 0, "vantage_point_none": 0, "under_clear": 0}
    orig_tasks = br._build_tasks

    def wrapped_tasks():
        tasks = orig_tasks()
        vt = [t for t in tasks if t[0] == "vantage" and t[1] == chan]
        if vt:
            stats["vantage_emitted"] += len(vt)
        else:
            # was a vantage skipped because clear tasks existed?
            if any(t[0] == "clear" for t in tasks) and \
                    len(br.obs.get(chan, [])) == 1 and \
                    br.vantage_tries.get(chan, 0) < P["vantage_max_tries"]:
                stats["under_clear"] += 1
        return tasks

    br._build_tasks = wrapped_tasks
    st = br.run()
    print("result ratio=%.3f  ch%d cleared=%s" % (st["clear_ratio"], chan, tgt.cleared))
    print("  status=%s  obs=%d  nosig=%d  vantage_tries=%s (budget %d)"
          % (br.status.get(chan), len(br.obs.get(chan, [])), len(br.nosig.get(chan, [])),
             br.vantage_tries.get(chan), P["vantage_max_tries"]))
    print("  vantage tasks emitted for this channel : %d"
          % stats["vantage_emitted"])
    print("  planner calls where a vantage was due but clear tasks took priority : %d"
          % stats["under_clear"])
    if br.obs.get(chan):
        o = br.obs[chan][0]
        print("  the single bearing was taken at (%.0f, %.0f), bearing %.1f deg"
              % (o[0], o[1], o[2]))
        print("  distance from there to the source: %.0f m (R_eff %.0f)"
              % (math.hypot(o[0] - tgt.x, o[1] - tgt.y), tgt.r_eff))
        lit = tgt.covers(o[0], o[1])
        print("  that point is on the %s side" % ("LIT" if lit else "DARK"))
    # what would vantage_point return now?
    if br.obs.get(chan):
        for local in (True, False):
            p = br.vantage_point(chan, local=local)
            print("  vantage_point(local=%s) -> %s" % (local, p))
