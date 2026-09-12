#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
why_extra_stops.py -- the certification search adds 16-22 stops regardless of the
lattice spacing, which contradicts the geometric expectation.  Find out what they
are actually for.

Reports, for one case:
  * how many stops come from the lattice and how many from the certification
    greedy
  * after the lattice sweep: how many candidate points are still uncertified,
    for which channels, and where they sit (radius, and their distance to the
    nearest true source)
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

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 30000
    spacing = float(sys.argv[2]) if len(sys.argv) > 2 else 1100.0
    srcs = sim.make_case(random.Random(seed), kind_mix=0.5)
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    p["survey_spacing"] = spacing
    ar = sim.Arena(srcs, seed=seed)
    br = rc.Brain(rc.LocalClient(ar), params=p, seed=seed)

    meta = {"lattice": 0, "extra": 0, "first_extra_at": None, "n_act": 0}
    orig_stop = br.next_search_stop
    lattice_keys = set((round(q[0], 1), round(q[1], 1))
                       for q in br._pending_stops())
    orig_probe = br.probe

    def wrapped_probe(pos, force=False):
        if force:
            key = (round(pos[0], 1), round(pos[1], 1))
            if key in lattice_keys:
                meta["lattice"] += 1
            else:
                meta["extra"] += 1
                if meta["first_extra_at"] is None:
                    meta["first_extra_at"] = meta["n_act"]
        meta["n_act"] += 1
        return orig_probe(pos, force=force)

    br.probe = wrapped_probe
    st = br.run()

    print("seed %d spacing %.0f : %d sources, ratio=%.3f time=%.0f travel=%.0f"
          % (seed, spacing, len(srcs), st["clear_ratio"], st["mean_time"],
             st["travel_m"]))
    print("  stops: lattice=%d  extra=%d  (first extra at action %s)"
          % (meta["lattice"], meta["extra"], meta["first_extra_at"]))

    unresolved = [c for c in br.channels if br.status[c] not in ("cleared", "empty")]
    ok, uncov, flags = br.certification_scan(unresolved)
    print("  at the end: unresolved channels=%d, certified=%s, uncovered grid pts=%d"
          % (len(unresolved), ok, len(uncov)))
    for c in unresolved:
        print("     ch %2d status=%-8s certified=%-5s obs=%d nosig=%d"
              % (c, br.status[c], flags.get(c), len(br.obs.get(c, [])),
                 len(br.nosig.get(c, []))))
    if uncov:
        bych = {}
        for q in uncov[:2000]:
            for c in unresolved:
                near = [(r[0] - q[0], r[1] - q[1]) for r in br.nosig[c]
                        if (r[0] - q[0]) ** 2 + (r[1] - q[1]) ** 2 <= 957.6 ** 2]
                okc = bool(near) and (not p.get("directional")
                                      or rc._origin_inside_hull(near))
                if not okc:
                    bych[c] = bych.get(c, 0) + 1
        print("  uncovered candidate count per channel: %s"
              % sorted(bych.items(), key=lambda kv: -kv[1])[:8])
        # how far are those candidates from the true sources?
        dmin = []
        for q in uncov[:400]:
            d = min(math.hypot(q[0] - s.x, q[1] - s.y) for s in srcs)
            dmin.append(d)
        dmin.sort()
        print("  distance from uncovered candidates to the nearest true source:"
              " min=%.0f  median=%.0f  max=%.0f m"
              % (dmin[0], dmin[len(dmin) // 2], dmin[-1]))
        rr = sorted(math.hypot(q[0], q[1]) for q in uncov[:400])
        print("  radius of uncovered candidates: min=%.0f median=%.0f max=%.0f m"
              % (rr[0], rr[len(rr) // 2], rr[-1]))
