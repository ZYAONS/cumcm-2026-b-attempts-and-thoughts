#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scan_spacing.py -- the key measurement for time compression.

Problem 4 currently spends 67.6 % of its virtual time on the survey stops and
visits 25.5 of them per case, while the lattice itself only contains about ten
points.  The extra stops come from the certification search.

Two facts drive everything:

  * a channel that was never heard must be CERTIFIED absent.  For an
    omnidirectional source one reading inside R_min rules the candidate out; for
    a directional source the candidate is ruled out only when the origin lies in
    the interior of the convex hull of the readings inside R_min.  For a
    triangular lattice the three vertices of the containing triangle surround any
    point, so coverage follows as soon as the spacing is at most R_min.
  * R_min here is the certification radius used by the scan:
    verify_r - verify_grid*sqrt(2)/2 = 1000 - 42 = 958 m.

So spacing <= 958 m should certify every candidate from the plain lattice, while
1100 m needs extra stops.  This script measures what actually happens: stops
visited, travel, detections, and virtual time, for a range of spacings.

usage: python scan_spacing.py [n_cases] [seed0]
"""
import json
import math
import os
import random
import sys
import time

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
from make_data import P4  # noqa: E402

SPACINGS = [700.0, 800.0, 850.0, 900.0, 950.0, 1000.0, 1100.0, 1300.0]


def evaluate(spacing, seeds, mix=0.5):
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P4)
    p["survey_spacing"] = spacing
    rs, ts, tr, stops, meas, sw = [], [], [], [], [], []
    t0 = time.time()
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        ar = sim.Arena(srcs, seed=sd)
        br = rc.Brain(rc.LocalClient(ar), params=p, seed=sd)
        st = br.run()
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
        stops.append(len(br.visited_stops))
        meas.append(st["n_measure"])
        sw.append(st["n_switch"])
    n = float(len(seeds))
    # the pure lattice size at this spacing, for reference
    cell = math.sqrt(3.0) / 2.0 * spacing * spacing
    n_lat = math.pi * 1800.0 ** 2 / cell
    return {"spacing": spacing, "ratio": sum(rs) / n, "min": min(rs),
            "time": sum(ts) / n, "travel": sum(tr) / n,
            "stops": sum(stops) / n, "lattice_pts": n_lat,
            "extra_stops": sum(stops) / n - n_lat,
            "measure": sum(meas) / n, "switch": sum(sw) / n,
            "wall": time.time() - t0}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    seeds = list(range(seed0, seed0 + n))
    print("verify_r=%.0f  verify_grid=%.0f  -> certification radius R=%.1f m"
          % (P4.get("verify_r", rc.DEFAULT_PARAMS["verify_r"]),
             P4.get("verify_grid", rc.DEFAULT_PARAMS["verify_grid"]),
             P4.get("verify_r", rc.DEFAULT_PARAMS["verify_r"])
             - P4.get("verify_grid", rc.DEFAULT_PARAMS["verify_grid"]) * 0.7072))
    print("%d cases, seeds %d..%d" % (n, seeds[0], seeds[-1]))
    print("%8s %8s %7s %8s %8s %8s %7s %8s %8s"
          % ("spacing", "lattice", "stops", "extra", "travel", "time", "ratio",
             "measure", "wall/s"))
    out = []
    for s in SPACINGS:
        r = evaluate(s, seeds)
        out.append(r)
        print("%8.0f %8.1f %7.1f %8.1f %8.0f %8.1f %7.4f %8.0f %8.0f"
              % (r["spacing"], r["lattice_pts"], r["stops"], r["extra_stops"],
                 r["travel"], r["time"], r["ratio"], r["measure"], r["wall"]),
              flush=True)
    with open(os.path.join(DATA, "scan_spacing.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/scan_spacing.json")
