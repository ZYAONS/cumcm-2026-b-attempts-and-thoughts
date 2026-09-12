#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
geom_core.py  --  Core geometry engine for bearing-only (cross-fixing) localization.

Chinese comments are used for readability; all executable identifiers/strings are ASCII.

Model background
----------------
A direction finder at station S_i measures the bearing (deg) of one interference
source. Because of the local electromagnetic environment the reading carries a
bounded systematic error, so the TRUE bearing of the source seen from S_i is
unknown but confined to

        [ theta_i - eps , theta_i + eps ]        (eps = 1 deg in this problem)

Hence every station defines an angular WEDGE (a convex cone with apex S_i). The
cross-fixing positioning region is the intersection of all wedges

        R = { P : | angle(P - S_i) - theta_i | <= eps   for every i }

which is a convex polygon (possibly empty, possibly unbounded). This module
builds that polygon exactly, computes its diameter, tests whether the disk whose
diameter equals the region diameter covers the region, and computes the minimum
enclosing circle (Welzl) for comparison.

Conventions
-----------
* angle : degrees, measured counter-clockwise from +x axis (east), range [0,360)
* half-plane : (a, b, c) encodes  a*x + b*y <= c
"""

import math
import random


# ----------------------------------------------------------------------------
# basic angle helpers
# ----------------------------------------------------------------------------
def norm360(a):
    """Normalize an angle (deg) into [0, 360)."""
    return a % 360.0


def deg2rad(a):
    return a * math.pi / 180.0


def bearing(px, py, qx, qy):
    """Bearing (deg, [0,360)) of the vector from P to Q."""
    return norm360(math.degrees(math.atan2(qy - py, qx - px)))


def ang_diff(a, b):
    """Signed smallest difference a-b wrapped into (-180, 180]."""
    d = (a - b + 180.0) % 360.0 - 180.0
    return 180.0 if d == -180.0 else d


def unit(a_deg):
    r = deg2rad(a_deg)
    return math.cos(r), math.sin(r)


# ----------------------------------------------------------------------------
# wedge -> half planes
# ----------------------------------------------------------------------------
def wedge_halfplanes(sx, sy, theta_deg, eps_deg):
    """
    Two half planes whose intersection is the angular wedge
        { P : bearing(P - S) in [theta-eps, theta+eps] (ccw) }.

    Derivation: v = P - S must satisfy
        cross(u(theta-eps), v) >= 0   and   cross(u(theta+eps), v) <= 0
    with cross(u, v) = ux*vy - uy*vx. Writing v = (x - sx, y - sy) this gives
        sin(theta-eps)*(x-sx) - cos(theta-eps)*(y-sy) <= 0
       -sin(theta+eps)*(x-sx) + cos(theta+eps)*(y-sy) <= 0
    Both are of the form a*x + b*y <= c.
    """
    t1 = deg2rad(theta_deg - eps_deg)
    t2 = deg2rad(theta_deg + eps_deg)
    hp = []
    a1, b1 = math.sin(t1), -math.cos(t1)
    hp.append((a1, b1, a1 * sx + b1 * sy))
    a2, b2 = -math.sin(t2), math.cos(t2)
    hp.append((a2, b2, a2 * sx + b2 * sy))
    return hp


def halfplanes_satisfied(hps, x, y, tol=1e-9):
    """True when the point satisfies every half plane a*x+b*y <= c (within tol)."""
    for (a, b, c) in hps:
        if a * x + b * y > c + tol * max(1.0, abs(c)):
            return False
    return True


def intersect_lines(l1, l2):
    """
    Intersection of two lines a1 x + b1 y = c1 and a2 x + b2 y = c2.
    Returns None when (nearly) parallel.
    """
    a1, b1, c1 = l1
    a2, b2, c2 = l2
    det = a1 * b2 - a2 * b1
    scale = math.hypot(a1, b1) * math.hypot(a2, b2)
    if abs(det) <= 1e-12 * max(scale, 1.0):
        return None
    x = (c1 * b2 - c2 * b1) / det
    y = (a1 * c2 - a2 * c1) / det
    return (x, y)


def convex_hull(points, tol=1e-9):
    """
    Andrew monotone chain. Returns hull vertices in counter-clockwise order,
    without duplicated points. Collinear points on the boundary are dropped.
    """
    pts = sorted(set((round(p[0], 9), round(p[1], 9)) for p in points))
    if len(pts) <= 2:
        return [tuple(p) for p in pts]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= tol:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= tol:
            upper.pop()
        upper.append(p)
    return [tuple(p) for p in lower[:-1] + upper[:-1]]


def polygon_vertices(hps):
    """
    Exact vertex enumeration of the feasible polygon { P : A P <= c }.

    Every vertex of a 2-D polyhedron is the intersection of two of its boundary
    lines, so we enumerate all O(m^2) line pairs, keep the feasible ones and take
    their convex hull. This is robust for the tiny systems appearing here
    (m = 2n <= 40) and it needs no artificial bounding box, therefore an
    unbounded region is not silently truncated: the caller is warned through
    the `bounded` flag (see region_from_bearings).
    """
    feasible = []
    m = len(hps)
    for i in range(m):
        for j in range(i + 1, m):
            p = intersect_lines(hps[i], hps[j])
            if p is None:
                continue
            if halfplanes_satisfied(hps, p[0], p[1]):
                feasible.append(p)
    if not feasible:
        return []
    return convex_hull(feasible)


# ----------------------------------------------------------------------------
# boundedness: recession cone of the region
# ----------------------------------------------------------------------------
def _circular_arc_intersection(arcs):
    """
    Intersection of circular arcs [lo_i, hi_i] (degrees, ccw, length < 180).
    Returns (nonempty, [representative angle]). Implemented by sampling the
    boundary directions: an intersection of closed arcs is non-empty iff one of
    the arc start points lies inside all arcs (or all arcs are the full circle).
    """
    starts = [a[0] % 360.0 for a in arcs]
    for s in starts:
        ok = True
        for (lo, hi) in arcs:
            if ang_diff(s, lo) < -1e-9 or ang_diff(s, hi) > 1e-9:
                ok = False
                break
        if ok:
            return True, s
    # also test just-inside points to be safe against floating point edges
    for s in starts:
        for d in (1e-7, -1e-7):
            t = (s + d) % 360.0
            if all(ang_diff(t, lo) >= -1e-9 and ang_diff(t, hi) <= 1e-9 for (lo, hi) in arcs):
                return True, t
    return False, None


def is_bounded(bearings_deg, eps_deg):
    """
    The region is unbounded iff the recession cone
        { d : bearing(d) in [theta_i-eps, theta_i+eps] for all i }
    contains a non-zero direction, i.e. iff the arcs have a common direction.
    """
    arcs = [(norm360(t - eps_deg), norm360(t + eps_deg)) for t in bearings_deg]
    nonempty, _ = _circular_arc_intersection(arcs)
    return not nonempty


# ----------------------------------------------------------------------------
# region built from a set of (station, bearing) measurements
# ----------------------------------------------------------------------------
def halfplanes_from_bearings(stations, bearings_deg, eps_deg):
    hps = []
    for (sx, sy), th in zip(stations, bearings_deg):
        hps.extend(wedge_halfplanes(sx, sy, th, eps_deg))
    return hps


def region_from_bearings(stations, bearings_deg, eps_deg=1.0):
    """
    Full description of the cross-fixing positioning region.

    Returns a dict with
      vertices  : hull vertices (ccw). Meaningful only when not empty.
      empty     : True when no point is consistent with all measurements.
      bounded   : False when the region is an unbounded cone-like set.
      diameter  : max pairwise distance of the vertices (inf if unbounded),
      d_pair    : the vertex pair realizing the diameter,
      cover_ok  : whether the disk having that pair as diameter contains the
                  whole region (Thales test on every vertex),
      cover_slack : max over vertices of (V-A).(V-B)  (<=0 means covered)
      mec       : (cx, cy, r) minimum enclosing circle
    """
    hps = halfplanes_from_bearings(stations, bearings_deg, eps_deg)
    verts = polygon_vertices(hps)
    bounded = is_bounded(bearings_deg, eps_deg)
    out = {
        "vertices": verts,
        "empty": len(verts) == 0,
        "bounded": bounded,
        "diameter": float("inf"),
        "d_pair": None,
        "cover_ok": None,
        "cover_slack": None,
        "mec": None,
    }
    if out["empty"]:
        return out
    if not bounded:
        # an unbounded region has no finite diameter: report the recession
        # direction so that the caller can react (add stations / use the
        # physically bounded region instead)
        arcs = [(norm360(t - eps_deg), norm360(t + eps_deg)) for t in bearings_deg]
        _, d = _circular_arc_intersection(arcs)
        out["recession_dir"] = d
        return out

    d, pair = polygon_diameter(verts)
    out["diameter"] = d
    out["d_pair"] = pair
    slack = diameter_disk_slack(verts, pair[0], pair[1])
    out["cover_slack"] = slack
    out["cover_ok"] = bool(slack <= 1e-9)
    out["mec"] = min_enclosing_circle(verts)
    return out


# ----------------------------------------------------------------------------
# diameter of a point set / convex polygon
# ----------------------------------------------------------------------------
def polygon_diameter(pts):
    """
    Diameter (largest pairwise distance) of a convex polygon given by its
    vertices. Brute force O(m^2) is used because m <= 40 here; the result is
    exact for a convex polygon (the diameter is realized by two vertices).
    Returns (value, (P, Q)).
    """
    best = -1.0
    bp = None
    m = len(pts)
    for i in range(m):
        xi, yi = pts[i]
        for j in range(i + 1, m):
            xj, yj = pts[j]
            d = math.hypot(xi - xj, yi - yj)
            if d > best:
                best = d
                bp = (pts[i], pts[j])
    if bp is None:
        return 0.0, (pts[0], pts[0])
    return best, bp


def rotating_calipers_diameter(pts):
    """
    Independent cross-check of polygon_diameter() using rotating calipers on the
    convex hull (Shamos). Both methods must agree; the agreement is reported in
    the self-check of Q1.
    """
    hull = convex_hull(pts)
    n = len(hull)
    if n < 2:
        return 0.0, (hull[0], hull[0]) if n == 1 else (None, None)
    if n == 2:
        d = math.dist(hull[0], hull[1])
        return d, (hull[0], hull[1])
    best = -1.0
    bp = None
    j = 1
    for i in range(n):
        ni = (i + 1) % n
        while True:
            nj = (j + 1) % n
            # advance j while the triangle area keeps growing
            a1 = abs(_tri_area2(hull[i], hull[ni], hull[j]))
            a2 = abs(_tri_area2(hull[i], hull[ni], hull[nj]))
            if a2 > a1:
                j = nj
            else:
                break
        for k in (j, (j + 1) % n):
            d = math.dist(hull[i], hull[k])
            if d > best:
                best = d
                bp = (hull[i], hull[k])
    return best, bp


def _tri_area2(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


# ----------------------------------------------------------------------------
# Thales test : does the disk with AB as diameter contain every vertex?
# ----------------------------------------------------------------------------
def diameter_disk_slack(pts, A, B):
    """
    By Thales' theorem P lies in the closed disk with diameter AB iff
        (P - A) . (P - B) <= 0.
    Returns the maximum of that quantity over the point set: <= 0 means the
    disk covers everything, > 0 gives the size of the violation (metres^2).
    """
    worst = -float("inf")
    for (x, y) in pts:
        v = (x - A[0]) * (x - B[0]) + (y - A[1]) * (y - B[1])
        if v > worst:
            worst = v
    return worst


# ----------------------------------------------------------------------------
# minimum enclosing circle (Welzl, randomized incremental, exact arithmetic in
# double precision with a small tolerance)
# ----------------------------------------------------------------------------
def _circle_from2(a, b):
    cx, cy = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
    return (cx, cy, math.dist(a, b) / 2.0)


def _circle_from3(a, b, c):
    ax, ay = a
    bx, by = b
    cx, cy = c
    d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        # collinear: fall back to the farthest pair
        cand = [(_circle_from2(a, b), a, b), (_circle_from2(a, c), a, c),
                (_circle_from2(b, c), b, c)]
        return max(cand, key=lambda t: t[0][2])[0]
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay)
          + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx)
          + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy, math.hypot(ux - ax, uy - ay))


def _inside(c, p, tol=1e-7):
    return math.hypot(p[0] - c[0], p[1] - c[1]) <= c[2] + tol


def min_enclosing_circle(points, seed=20260913):
    """
    Smallest enclosing circle of a point set (Welzl's algorithm).
    Returns (cx, cy, r).
    """
    pts = list(points)
    if not pts:
        return None
    rnd = random.Random(seed)
    rnd.shuffle(pts)
    c = (pts[0][0], pts[0][1], 0.0)
    for i in range(1, len(pts)):
        if _inside(c, pts[i]):
            continue
        c = (pts[i][0], pts[i][1], 0.0)
        for j in range(i):
            if _inside(c, pts[j]):
                continue
            c = _circle_from2(pts[i], pts[j])
            for k in range(j):
                if _inside(c, pts[k]):
                    continue
                c = _circle_from3(pts[i], pts[j], pts[k])
    return c


# ----------------------------------------------------------------------------
# analytic description of the 2-station region (used for closed-form checks)
# ----------------------------------------------------------------------------
def two_station_region(s1, s2, th1_deg, th2_deg, eps_deg=1.0):
    """
    Explicit four lines of the classical two-station cross-fixing figure and the
    four corner points A = L1- ^ L2-, B = L1- ^ L2+ , C = L1+ ^ L2- ,
    D = L1+ ^ L2+ (the feasible ones form the red quadrilateral of the problem
    statement). Returns dict with the lines and the feasible corners.
    """
    hps = wedge_halfplanes(s1[0], s1[1], th1_deg, eps_deg) + \
          wedge_halfplanes(s2[0], s2[1], th2_deg, eps_deg)
    L1m, L1p, L2m, L2p = hps
    corners = {}
    for name, la, lb in (("A", L1m, L2m), ("B", L1m, L2p),
                         ("C", L1p, L2m), ("D", L1p, L2p)):
        p = intersect_lines(la, lb)
        if p is not None:
            corners[name] = p
    feasible = {k: v for k, v in corners.items() if halfplanes_satisfied(hps, v[0], v[1])}
    return {"lines": {"L1m": L1m, "L1p": L1p, "L2m": L2m, "L2p": L2p},
            "corners": corners, "feasible": feasible}


def region_intersection_angle(s1, s2, g):
    """
    Intersection angle gamma (deg) at the source G between the two lines of
    sight: the geometric quality factor of a two-station fix.
    """
    b1 = bearing(g[0], g[1], s1[0], s1[1])
    b2 = bearing(g[0], g[1], s2[0], s2[1])
    return abs(ang_diff(b1, b2))


def asymptotic_diameter(d1, d2, gamma_deg, eps_deg=1.0):
    """
    Closed-form first-order diameter of the positioning region for a slender
    region: the two +-eps rays through the source form, after linearisation, a
    parallelogram with side widths w_i = 2*eps*d_i cut at angle gamma, hence
        D ~ sqrt(w1^2 + w2^2 + 2 w1 w2 cos(gamma)) / sin(gamma).
    Used as an independent analytic check of the polygon-based diameter.
    """
    w1 = 2.0 * deg2rad(eps_deg) * d1
    w2 = 2.0 * deg2rad(eps_deg) * d2
    s = math.sin(deg2rad(gamma_deg))
    if abs(s) < 1e-12:
        return float("inf")
    return math.sqrt(w1 * w1 + w2 * w2 + 2.0 * w1 * w2 * math.cos(deg2rad(gamma_deg))) / s
