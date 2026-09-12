#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
final_validate.py -- final acceptance test of the tuned strategy.

Runs the tuned configuration and the pre-optimisation baseline on an
INDEPENDENT case pool (a seed range that no tuning run ever touched) and prints
the comparison.  This is the step that caught the pool-reuse artefact: a 44 %
"gain" that did not survive an independent pool.

usage: python final_validate.py [n_cases]
"""
import json
import math
import os
import random
import statistics as st
import sys
import time

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40


def load_best(tag):
    p = os.path.join(OUT, "optimize_%s.json" % tag)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)["params"]
    return None


def evaluate(params, seeds, mix):
    rows = []
    t0 = time.time()
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        s, _ = rc.run_case(srcs, params=params, seed=sd)
        rows.append((s["clear_ratio"], s["mean_time"], s["travel_m"]))
    t = sorted(r[1] for r in rows)
    return {"ratio": sum(r[0] for r in rows) / len(rows),
            "ratio_min": min(r[0] for r in rows),
            "time": sum(r[1] for r in rows) / len(rows),
            "median": st.median(t), "p90": t[9 * len(t) // 10],
            "travel": sum(r[2] for r in rows) / len(rows),
            "wall": time.time() - t0}


def show(tag, r):
    print("%-30s ratio=%.4f min=%.4f time=%7.1f median=%7.1f p90=%7.1f "
          "travel=%7.0f  (%.0f s)"
          % (tag, r["ratio"], r["ratio_min"], r["time"], r["median"], r["p90"],
             r["travel"], r["wall"]), flush=True)


CONF = {
    "q3": {
        "seeds": list(range(12000, 12000 + N)),
        "mix": 0.0,
        "old": dict(rc.DEFAULT_PARAMS, survey_mode="ring", ring_radius=1280.0,
                    probe_spacing=650.0, locate_sigma=320.0, clear_bonus=260.0,
                    probe_min_angle=22.0, search_cost_bias=60.0,
                    term_cap=420.0, endgame_radius=90.0,
                    no_plain_fallback=False, rim_patrol=False),
        "new": dict(rc.DEFAULT_PARAMS, survey_mode="ring"),
    },
    "q4": {
        "seeds": list(range(62000, 62000 + N)),
        "mix": 0.5,
        "old": dict(rc.DEFAULT_PARAMS, survey_mode="lattice",
                    survey_spacing=1000.0, directional=True,
                    no_plain_fallback=False, rim_patrol=False),
        "new": dict(rc.DEFAULT_PARAMS, survey_mode="lattice",
                    survey_spacing=1000.0, directional=True),
    },
}

if __name__ == "__main__":
    summary = {}
    for tag in ("q3", "q4"):
        c = CONF[tag]
        tuned = load_best(tag)
        new = dict(c["new"])
        if tuned:
            for k in ("ring_radius", "probe_spacing", "locate_sigma", "clear_bonus",
                      "probe_min_angle", "search_cost_bias", "term_cap",
                      "endgame_radius", "survey_spacing", "max_attempts",
                      "rim_step", "max_rim_patrols"):
                if k in tuned:
                    new[k] = tuned[k]
        print("--- %s : %d independent cases (seeds %d..%d)"
              % (tag.upper(), N, c["seeds"][0], c["seeds"][-1]), flush=True)
        a = evaluate(c["old"], c["seeds"], c["mix"])
        show("before (pre-optimisation)", a)
        b = evaluate(new, c["seeds"], c["mix"])
        show("after  (verified + tuned)", b)
        summary[tag] = {"before": a, "after": b, "params": new,
                        "seeds": [c["seeds"][0], c["seeds"][-1]]}
        print("  delta: time %+.1f %%  ratio %+.4f  travel %+.1f %%"
              % (100.0 * (b["time"] / a["time"] - 1.0), b["ratio"] - a["ratio"],
                 100.0 * (b["travel"] / a["travel"] - 1.0)), flush=True)
    with open(os.path.join(OUT, "final_validation.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print("report -> data/final_validation.json")
