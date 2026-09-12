# -*- coding: utf-8 -*-
"""fix_verify_fg.py -- two corrections to the verification suite.

  F  brain_vtime and the arena clock are not supposed to be equal: when the
     strategy replays a cached reading it moves without contacting the arena,
     so the arena clock (and hence the reported metric) advances less than the
     brain's own estimate.  The check now asserts the correct invariant
     (arena clock <= brain estimate) and that the log replay equals the arena
     clock, which it already did.

  G  the brute-force reference reproduced the *old* early-exit shortcut of
     certification_scan (`if flags[c] is False: continue`), which silently
     truncated the uncovered list.  The incremental rewrite returns the true
     uncovered set, so the reference has to be the true set as well.  The
     outcome check is also made a proper equivalence test (same case, with and
     without the instrumented scan).
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "verify_simulator.py")
s = io.open(p, encoding="utf-8").read()

# ---- F --------------------------------------------------------------------
a = """    check(G, "brain_clock_agrees", close(st["brain_vtime"], acc, 1e-6),
          "the strategy clock agrees with the log replay", "%.3f" % st["brain_vtime"],
          "%.3f" % acc)"""
b = """    check(G, "brain_clock_not_below_arena", st["brain_vtime"] >= acc - 1e-6,
          "the strategy estimate includes movements that never reach the arena "
          "(cached readings), so it can only be larger than the logged clock",
          ">= %.3f" % acc, "%.3f" % st["brain_vtime"])"""
assert a in s, "F anchor"
s = s.replace(a, b, 1)

# ---- G: reference without the early-exit shortcut -------------------------
a = """        flags, unc = {}, set()
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
        return flags, unc"""
b = """        flags, unc = {}, set()
        for q in grid:
            for c in channels:
                near = [(r[0] - q[0], r[1] - q[1]) for r in br.nosig[c]
                        if (r[0] - q[0]) ** 2 + (r[1] - q[1]) ** 2 <= R2]
                okp = bool(near) and (not directional or rc._origin_inside_hull(near))
                if not okp:
                    flags[c] = False
                    unc.add((round(q[0], 3), round(q[1], 3)))
        for c in channels:
            flags.setdefault(c, True)
        return flags, unc"""
assert a in s, "G brute anchor"
s = s.replace(a, b, 1)

# ---- G: proper equivalence of the outcome ---------------------------------
a = """    br.certification_scan = wrapped
    st = br.run()
    check(G, "incremental_equals_bruteforce", state["bad"] == 0,
          "every scan call compared with a from-scratch recomputation",
          "identical", "%d comparisons, %d mismatches %s"
          % (state["n"], state["bad"], state["why"]))
    check(G, "run_still_completes", st["clear_ratio"] >= 0.999,
          "the incremental scan does not degrade the outcome", "1.000",
          "%.4f" % st["clear_ratio"])"""
b = """    br.certification_scan = wrapped
    st = br.run()
    check(G, "incremental_equals_bruteforce", state["bad"] == 0,
          "every scan call compared with a from-scratch recomputation "
          "(full uncovered set, no early exit)",
          "identical", "%d comparisons, %d mismatches %s"
          % (state["n"], state["bad"], state["why"]))

    st2, _ = rc.run_case(sim.make_case(random.Random(90909), kind_mix=0.5),
                         params=params, seed=90909)
    same = (abs(st["clear_ratio"] - st2["clear_ratio"]) < 1e-9
            and abs(st["mean_time"] - st2["mean_time"]) < 1e-6)
    check(G, "instrumented_run_equivalent", same,
          "instrumenting the scan does not change the outcome of a run",
          "%.4f/%.1f" % (st2["clear_ratio"], st2["mean_time"]),
          "%.4f/%.1f" % (st["clear_ratio"], st["mean_time"]))"""
assert a in s, "G check anchor"
s = s.replace(a, b, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("verification suite corrected (F invariant, G reference)")
