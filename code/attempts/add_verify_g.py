# -*- coding: utf-8 -*-
"""add_verify_g.py -- group G of the verification suite.

The certification scan was rewritten to be incremental (a candidate location can
only move from "not ruled out" to "ruled out" as readings accumulate).  An
optimisation like that is only acceptable if it is provably equivalent, so the
suite now compares the incremental result with a from-scratch recomputation on
every single call.

It also checks the two structural properties of the rim patrol: the samples must
actually lie outside the arena rim, and the trip budget must be respected.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "verify_simulator.py")
s = io.open(p, encoding="utf-8").read()

a = """def rc_default():"""
b = '''def group_g():
    """Incremental certification vs brute force, and the rim patrol contract."""
    G = "G"
    import robot_core as rc

    params = dict(rc.DEFAULT_PARAMS, survey_mode="lattice",
                  survey_spacing=1000.0, directional=True)
    srcs = sim.make_case(random.Random(90909), kind_mix=0.5)
    ar = sim.Arena(srcs, seed=90909)
    br = rc.Brain(rc.LocalClient(ar), params=params, seed=90909)
    grid = br._verify_grid()

    def brute(channels):
        R = br.p["verify_r"] - br.p["verify_grid"] * 0.7072
        R2 = R * R
        directional = bool(br.p.get("directional", False))
        flags, unc = {}, set()
        for q in grid:
            for c in channels:
                if flags.get(c) is False:
                    continue
                near = [(r[0] - q[0], r[1] - q[1]) for r in br.nosig[c]
                        if (r[0] - q[0]) ** 2 + (r[1] - q[1]) ** 2 <= R2]
                okp = bool(near) and (not directional or rc._origin_inside_hull(near))
                if not okp:
                    flags[c] = False
                    unc.add((round(q[0], 3), round(q[1], 3)))
        for c in channels:
            flags.setdefault(c, True)
        return flags, unc

    state = {"n": 0, "bad": 0, "why": ""}
    orig = br.certification_scan

    def wrapped(channels):
        ok, uncov, flags = orig(list(channels))
        bflags, bunc = brute(list(channels))
        inc = set((round(q[0], 3), round(q[1], 3)) for q in uncov)
        state["n"] += 1
        if bunc != inc or any(bflags[c] != flags.get(c) for c in channels):
            state["bad"] += 1
            if not state["why"]:
                state["why"] = ("call %d: brute %d vs incremental %d uncovered"
                                % (state["n"], len(bunc), len(inc)))
        return ok, uncov, flags

    br.certification_scan = wrapped
    st = br.run()
    check(G, "incremental_equals_bruteforce", state["bad"] == 0,
          "every scan call compared with a from-scratch recomputation",
          "identical", "%d comparisons, %d mismatches %s"
          % (state["n"], state["bad"], state["why"]))
    check(G, "run_still_completes", st["clear_ratio"] >= 0.999,
          "the incremental scan does not degrade the outcome", "1.000",
          "%.4f" % st["clear_ratio"])

    # rim patrol contract
    patrol = rc.Brain(rc.LocalClient(sim.Arena(srcs, seed=1)), params=params, seed=1)
    rim = sim.ARENA_RADIUS - 2.0 * params["verify_grid"]
    q = [(rim + 5.0, 0.0), (0.0, rim + 5.0), (rim * 0.9, 0.0), (-rim - 1.0, 0.0)]
    pts = patrol._rim_patrol_stops(q)
    outside = all(math.hypot(x, y) > sim.ARENA_RADIUS for (x, y) in pts)
    check(G, "rim_patrol_outside", bool(pts) and outside,
          "patrol samples lie beyond the arena rim",
          "all outside", "%d pts, outside=%s" % (len(pts), outside))

    capped = patrol._rim_patrol_stops([(rim + 1.0, 0.0)], )
    big = patrol._rim_patrol_stops([(rim + 1.0 + 1.0 * i, 0.0) for i in range(40)])
    check(G, "rim_patrol_capped", len(big) <= patrol.p["rim_max_pts"],
          "the number of outside samples per step is capped", "<=%d"
          % patrol.p["rim_max_pts"], len(big))
    check(G, "rim_patrol_ignores_interior", patrol._rim_patrol_stops([(0.0, 0.0)]) == [],
          "interior candidates never trigger a trip outside", "no points",
          patrol._rim_patrol_stops([(0.0, 0.0)]))


def rc_default():'''
assert a in s, "insert anchor"
s = s.replace(a, b, 1)

a = """    extra = group_e()
    group_f()"""
b = """    extra = group_e()
    group_f()
    group_g()"""
assert a in s, "call anchor"
s = s.replace(a, b, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("group G added (incremental certification equivalence + rim patrol contract)")
