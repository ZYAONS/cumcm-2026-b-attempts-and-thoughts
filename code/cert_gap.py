#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cert_gap.py -- exactly what is left uncertified when the survey sweep is done?

If a full lattice sweep at spacing s already surrounds every candidate (the three
vertices of the containing triangle are within the certification radius), then the
sweep alone should certify every channel that was never heard, and the
certification search should add no stops at all.  Measured: it adds 11-19.

This script captures the certification state at the moment the primary sweep has
just finished (the first time next_search_stop is called) and reports
  * how many candidates are still open, for how many channels
  * where those candidates sit (radius)
  * how far they are from the nearest true source
  * whether the channel they belong to was ever heard

usage: python cert_gap.py [n_cases] [seed0] [spacing]
"""
import json
import math
import os
import random
import sys

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
from make_data import P4  # noqa: E402
D2 = (P4.get("verify_r", 1000.0)
      - P4.get("verify_grid", 60.0) * 0.7072) ** 2


def analyse(seed, spacing):
    srcs = sim.make_case(random.Random(seed), kind_mix=0.5)
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    p["survey_spacing"] = spacing
    ar = sim.Arena(srcs, seed=seed)
    br = rc.Brain(rc.LocalClient(ar), params=p, seed=seed)

    cap = {}
    orig = br.next_search_stop
    first = [True]
    extra = [0]

    def wrapped(unresolved):
        if first[0]:
            first[0] = False
            grid = br._verify_grid()
            unc = {}
            for c in unresolved:
                open_pts = []
                for q in grid:
                    near = [(r[0] - q[0], r[1] - q[1]) for r in br.nosig[c]
                            if (r[0] - q[0]) ** 2 + (r[1] - q[1]) ** 2 <= D2]
                    if not near or not rc._origin_inside_hull(near):
                        open_pts.append(q)
                unc[c] = open_pts
            cap["unresolved"] = list(unresolved)
            cap["open_per_channel"] = {c: len(v) for c, v in unc.items()}
            allq = [q for v in unc.values() for q in v]
            if allq:
                cap["r_min"] = min(math.hypot(q[0], q[1]) for q in allq)
                cap["r_max"] = max(math.hypot(q[0], q[1]) for q in allq)
                cap["d_to_src_min"] = min(
                    min(math.hypot(q[0] - s.x, q[1] - s.y) for s in srcs)
                    for q in allq)
            cap["n_stops_so_far"] = len(br.visited_stops)
            cap["n_nosig"] = {c: len(br.nosig[c]) for c in unresolved}
            cap["heard"] = {c: len(br.obs.get(c, [])) for c in unresolved}
        r = orig(unresolved)
        if r[0] is not None:
            extra[0] += 1
        return r

    br.next_search_stop = wrapped
    st = br.run()
    cap["extra_stops"] = extra[0]
    cap["ratio"] = st["clear_ratio"]
    cap["time"] = st["mean_time"]
    cap["stops"] = len(br.visited_stops)
    cap["sources"] = len(srcs)
    return cap


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    spacing = float(sys.argv[3]) if len(sys.argv) > 3 else 1100.0
    agg = {"extra": 0, "stops": 0, "cases": 0, "open": 0, "ch_open": 0,
           "r_max": 0.0, "d_min": 1e9, "ratio": 0.0}
    for i in range(n):
        c = analyse(seed0 + i, spacing)
        agg["cases"] += 1
        agg["extra"] += c["extra_stops"]
        agg["stops"] += c["stops"]
        agg["ratio"] += c["ratio"]
        tot_open = sum(c["open_per_channel"].values())
        agg["open"] += tot_open
        agg["ch_open"] += sum(1 for v in c["open_per_channel"].values() if v)
        if tot_open:
            agg["r_max"] = max(agg["r_max"], c.get("r_max", 0.0))
            agg["d_min"] = min(agg["d_min"], c.get("d_to_src_min", 1e9))
        print("seed %d: sources=%2d stops=%2d extra=%2d ratio=%.3f  "
              "unresolved=%2d  still-open candidates=%4d over %d channels  "
              "r_max=%s d_to_src_min=%s"
              % (seed0 + i, c["sources"], c["stops"], c["extra_stops"], c["ratio"],
                 len(c["unresolved"]), tot_open,
                 sum(1 for v in c["open_per_channel"].values() if v),
                 c.get("r_max", "-"), c.get("d_to_src_min", "-")), flush=True)
    print("\nMEAN over %d cases (spacing %.0f): stops=%.1f  extra=%.1f  "
          "open candidates after the sweep=%.1f over %.1f channels  ratio=%.4f"
          % (agg["cases"], spacing, agg["stops"] / agg["cases"],
             agg["extra"] / agg["cases"], agg["open"] / agg["cases"],
             agg["ch_open"] / agg["cases"], agg["ratio"] / agg["cases"]))
    print("   worst radius of an open candidate: %.0f m   "
          "smallest distance to a true source: %.0f m"
          % (agg["r_max"], agg["d_min"]))
    with open(os.path.normpath(os.path.join(HERE, "..", "data", "cert_gap.json")),
              "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=1)
