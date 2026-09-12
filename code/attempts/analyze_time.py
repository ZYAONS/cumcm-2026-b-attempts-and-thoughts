# -*- coding: utf-8 -*-
"""analyze_time.py -- where does the virtual time actually go?

Breaks the total virtual time of a run into
    travel / detection(+switching) / clearance,
and the detection count into     census / search-stop probe / homing / vantage.
Run: python analyze_time.py
"""
import json
import os
import random
import statistics
import sys

import robot_core as rc
import simulator as sim

P3 = {"survey_mode": "ring"}
P4 = {"survey_mode": "lattice", "survey_spacing": 1000.0, "directional": True,
      "outer_ring_gap": 0.0}


def instrument(brain):
    """count measurements per task class"""
    brain._task_measure = {"clear": 0, "localise": 0, "probe": 0, "census": 0}
    orig = brain.move_measure

    def wrapper(x, y, c):
        r = orig(x, y, c)
        brain._task_measure[brain._cur_task] = \
            brain._task_measure.get(brain._cur_task, 0) + 1
        return r
    brain.move_measure = wrapper
    return brain


def run_one(mode, seed, params=None, mix=None):
    p = dict(rc.DEFAULT_PARAMS)
    if mode == "q3":
        p.update(P3)
        mix = 0.0 if mix is None else mix
    else:
        p.update(P4)
        mix = 0.5 if mix is None else mix
    if params:
        p.update(params)
    srcs = sim.make_case(random.Random(seed), kind_mix=mix)
    arena = sim.Arena(srcs, seed=seed)
    cl = rc.LocalClient(arena)
    brain = instrument(rc.Brain(cl, params=p, seed=seed))
    st = brain.run()
    st.update(arena.stats())
    st["meas_by_task"] = dict(brain._task_measure)
    st["stops_visited"] = len(brain.visited_stops)
    st["wall"] = None
    arena.close()
    return st


def report(tag, rows):
    n = len(rows)
    ratio = statistics.mean(r["clear_ratio"] for r in rows)
    mt = statistics.mean(r["mean_time"] if r["n_cleared"] else 9000.0 for r in rows)
    trav = statistics.mean(r["travel_m"] for r in rows)
    meas = statistics.mean(r["n_measure"] for r in rows)
    clr = statistics.mean(r["n_clear"] for r in rows)
    stops = statistics.mean(r["stops_visited"] for r in rows)
    vt = statistics.mean(r["virtual_time"] for r in rows)
    cats = {}
    for k in ("census", "probe", "localise", "clear"):
        cats[k] = statistics.mean(r["meas_by_task"].get(k, 0) for r in rows)
    print("%-26s ratio=%.3f  T/source=%7.1f  total=%7.1f s | travel=%6.0f m "
          "(%4.0f s)  detect=%5.1f (%4.0f s)  clear=%4.1f (%3.0f s)  stops=%4.1f"
          % (tag, ratio, mt, vt, trav, trav / 5.0, meas, meas * 6.0 - 0,
             clr, clr * 3.6, stops))
    print("      %-22s census=%.0f  search-probe=%.0f  homing=%.0f  vantage=%.0f"
          % ("", cats["census"], cats["probe"], cats["clear"], cats["localise"]))
    return {"ratio": ratio, "mean_time": mt, "travel": trav, "measure": meas,
            "stops": stops, "vtime": vt, "meas_by_task": cats}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    print("=" * 118)
    print("problem 3 (20 cases each)")
    for tag, par in (("baseline", {}),
                     ("probe_spacing 650->1100", {"probe_spacing": 1100.0}),
                     ("ring_radius 1280->1100", {"ring_radius": 1100.0}),
                     ("probe_min_angle 22->40", {"probe_min_angle": 40.0})):
        rows = [run_one("q3", 20000 + k, par) for k in range(n)]
        report(tag, rows)
    print("=" * 118)
    print("problem 4 (mixed, 20 cases each)")
    for tag, par in (("baseline (lattice 1000)", {}),
                     ("lattice spacing 1400", {"survey_spacing": 1400.0}),
                     ("ring + certification", {"survey_mode": "ring"}),
                     ("probe_spacing 650->1100", {"probe_spacing": 1100.0})):
        rows = [run_one("q4", 30000 + k, par) for k in range(n)]
        report(tag, rows)


if __name__ == "__main__":
    main()
