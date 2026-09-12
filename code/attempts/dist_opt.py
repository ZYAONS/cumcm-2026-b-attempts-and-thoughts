# -*- coding: utf-8 -*-
"""dist_opt.py -- distribution, not just the mean: the tuning pool suggested a
44 % gain from ring_radius 1280 -> 1250 which an independent pool does not
reproduce, so look at the shape of the distribution."""
import random
import statistics as st
import sys

import robot_core as rc
import simulator as sim


def per_case(params, seeds, mix):
    out = []
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        s, _ = rc.run_case(srcs, params=params, seed=sd)
        out.append((s["mean_time"], s["clear_ratio"], s["travel_m"]))
    return out


def report(tag, rows):
    t = sorted(r[0] for r in rows)
    print("%-22s mean=%7.1f median=%7.1f p10=%7.1f p90=%7.1f  >600s: %d/%d  ratio=%.4f"
          % (tag, sum(t) / len(t), st.median(t), t[len(t) // 10],
             t[9 * len(t) // 10], sum(1 for v in t if v > 600), len(t),
             sum(r[1] for r in rows) / len(rows)), flush=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "q3"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    if which == "q3":
        pools = [("tune 70000", range(70000, 70000 + n), 0.0),
                 ("valid 31000", range(31000, 31000 + n), 0.0),
                 ("valid 44000", range(44000, 44000 + n), 0.0)]
        for tag, seeds, mix in pools:
            for rho in (1250.0, 1280.0, 1320.0):
                p = dict(rc.DEFAULT_PARAMS, survey_mode="ring", ring_radius=rho)
                report("%s rho=%.0f" % (tag, rho), per_case(p, list(seeds), mix))
            print()
