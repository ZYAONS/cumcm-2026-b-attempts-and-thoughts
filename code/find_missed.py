#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
find_missed.py -- 列出当前配置在所有独立池上仍然漏掉的源及其几何特征。

usage: python find_missed.py [n_cases]
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

POOLS = [("A", 62000), ("B", 51000), ("C", 12000), ("D", 30000)]

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    tot_src, tot_miss = 0, 0
    rows = []
    for name, s0 in POOLS:
        missed = []
        for i in range(n):
            sd = s0 + i
            srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
            ar = sim.Arena(srcs, seed=sd)
            br = rc.Brain(rc.LocalClient(ar), params=dict(rc.DEFAULT_PARAMS, **P4),
                          seed=sd)
            st = br.run()
            tot_src += len(srcs)
            for s in srcs:
                if not s.cleared:
                    missed.append({
                        "pool": name, "seed": sd, "ch": s.channel,
                        "r": round(math.hypot(s.x, s.y)), "kind": s.kind,
                        "dir": None if s.direction is None else round(s.direction),
                        "r_eff": round(s.r_eff), "status": br.status.get(s.channel),
                        "obs": len(br.obs.get(s.channel, [])),
                        "nosig": len(br.nosig.get(s.channel, [])),
                        "attempts": br.attempts.get(s.channel),
                        "total": br.total_attempts.get(s.channel),
                        "vantage": br.vantage_tries.get(s.channel),
                        "est": None if br.est.get(s.channel) is None
                        else round(br.est[s.channel][2])})
        tot_miss += len(missed)
        print("pool %s (%d cases): %d missed" % (name, n, len(missed)), flush=True)
        rows += missed
    print("\nTOTAL missed %d / %d sources (%.3f%%)"
          % (tot_miss, tot_src, 100.0 * tot_miss / tot_src))
    for m in rows:
        # is the source's outward direction toward the rim?
        if m["kind"] == "directional":
            rad = math.degrees(0.0)  # placeholder
        print("  %s seed %d ch%2d r=%4d %-11s dir=%-4s R_eff=%4d status=%-8s "
              "obs=%d nosig=%3d attempts=%s/%s vantage=%s sigma=%s"
              % (m["pool"], m["seed"], m["ch"], m["r"], m["kind"], m["dir"],
                 m["r_eff"], m["status"], m["obs"], m["nosig"], m["attempts"],
                 m["total"], m["vantage"], m["est"]))
    with open(os.path.join(DATA, "find_missed.json"), "w", encoding="utf-8") as f:
        json.dump({"total_sources": tot_src, "missed": rows}, f,
                  ensure_ascii=False, indent=1)
    print("report -> data/find_missed.json")
