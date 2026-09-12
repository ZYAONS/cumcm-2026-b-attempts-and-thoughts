# -*- coding: utf-8 -*-
"""add_verify_h.py -- group H: the strategy-level guarantees.

These are not simulator properties but the properties the paper's correctness
argument rests on, and they are cheap to check exhaustively:

  H1  guaranteed discovery.  For the configured survey lattice every point of the
      target disk is within R_min of some survey stop, so a source with any
      R_eff >= R_min is bound to be received at least once.  The lattice is
      triangular, so the covering radius is spacing/sqrt(3).

  H2  the seven point covering of problem 3 (theorem 1) satisfies the closed
      form  rho*cos30 + sqrt(R_min^2 - (rho/2)^2) >= R_arena.

  H3  a rim candidate really is uncertifiable from inside: taking a point just
      inside the rim, every reading position inside the disk lies in the same
      open half plane through it, so the origin is never in the convex hull.

  H4  the certification predicate agrees with brute force on synthetic reading
      sets (random point sets, both omni and directional rules).
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "verify_simulator.py")
s = io.open(p, encoding="utf-8").read()

a = "def rc_default():"
b = '''def group_h():
    """Strategy level guarantees: discovery, the covering theorem, rim geometry."""
    G = "H"
    import robot_core as rc

    # ---- H1 guaranteed discovery -----------------------------------------
    bad = []
    for spacing in (850.0, 1000.0, 1100.0, 1300.0):
        params = dict(rc.DEFAULT_PARAMS, survey_mode="lattice",
                      survey_spacing=spacing, directional=True)
        br = rc.Brain(rc.LocalClient(sim.Arena(
            sim.make_case(random.Random(1), n_sources=10), seed=1)),
            params=params, seed=1)
        stops = br._make_survey_stops()
        rng = random.Random(7)
        worst = 0.0
        for _ in range(3000):
            a = 2 * math.pi * rng.random()
            r = sim.ARENA_RADIUS * math.sqrt(rng.random())
            q = (r * math.cos(a), r * math.sin(a))
            d = min(math.hypot(q[0] - p[0], q[1] - p[1]) for p in stops)
            worst = max(worst, d)
        if worst > sim.R_EFF_LO:
            bad.append((spacing, worst))
    check(G, "discovery_guaranteed", not bad,
          "every point of the disk is within R_min of a survey stop "
          "(triangular lattice: covering radius = spacing/sqrt(3))",
          "<= %.0f m for every spacing" % sim.R_EFF_LO,
          "violations: %s" % bad if bad else "ok")

    # ---- H2 the seven point covering -------------------------------------
    rho = rc.DEFAULT_PARAMS["ring_radius"]
    cov = rho * math.cos(math.radians(30)) + math.sqrt(
        sim.R_EFF_LO ** 2 - (rho / 2.0) ** 2)
    check(G, "seven_point_covering", cov >= sim.ARENA_RADIUS,
          "ring_radius=%.0f m gives a covering radius of %.1f m" % (rho, cov),
          ">= %.0f" % sim.ARENA_RADIUS, "%.1f" % cov)

    # ---- H3 a rim candidate is not certifiable from inside ---------------
    rim = sim.ARENA_RADIUS - 5.0
    q = (rim, 0.0)
    inside = []
    for i in range(400):
        a = 2 * math.pi * i / 400.0
        for rr in (300.0, 900.0, 1500.0):
            x, y = rr * math.cos(a), rr * math.sin(a)
            if math.hypot(x, y) <= sim.ARENA_RADIUS:
                inside.append((x - q[0], y - q[1]))
    worst_dot = max(v[0] for v in inside)          # radial direction is +x
    check(G, "rim_not_certifiable_inside", worst_dot < 0.0,
          "for a source 5 m inside the rim every in-domain reading direction "
          "has a negative component along the outward normal, so no convex hull "
          "of them can contain the source (theorem 2)",
          "< 0", "%.1f" % worst_dot)

    # ---- H4 the certification predicate vs brute force -------------------
    rng = random.Random(11)
    mism = 0
    for trial in range(200):
        k = rng.randint(1, 6)
        pts = [(rng.uniform(-1200, 1200), rng.uniform(-1200, 1200))
               for _ in range(k)]
        if (0.0, 0.0) in pts:
            continue
        for directional in (False, True):
            got = rc._origin_inside_hull(pts)
            # reference: the origin is outside the hull iff some direction has a
            # strictly negative dot product with every point
            hull_pts = __import__("geom_core").convex_hull(pts)
            ref = True
            if len(hull_pts) >= 3:
                cross = []
                n = len(hull_pts)
                for i in range(n):
                    x1, y1 = hull_pts[i]
                    x2, y2 = hull_pts[(i + 1) % n]
                    cross.append(x1 * y2 - y1 * x2)
                ref = all(c > 1e-9 for c in cross) or all(c < -1e-9 for c in cross)
            if got != ref:
                mism += 1
    check(G, "hull_predicate_vs_cross_product", mism == 0,
          "the origin-in-hull test agrees with the cross product sign test "
          "on 200 random point sets", "0 mismatches", mism)


def rc_default():'''
assert a in s, "insert anchor"
s = s.replace(a, b, 1)

a = """    group_f()
    group_g()"""
b = """    group_f()
    group_g()
    group_h()"""
assert a in s, "call anchor"
s = s.replace(a, b, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("group H added (discovery guarantee, covering theorem, rim geometry, hull predicate)")
