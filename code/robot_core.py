#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
robot_core.py -- robot-dog client + search/localisation/clearance strategy for
problems 3 (all omni sources) and 4 (mixed omni + directional sources).

The client speaks the HTTP+JSON protocol of 附件2 (four actions /enter, /measure,
/clear, /exit, one new request_id per action, retry with the same request_id on
network failure).  A local in-process adapter exposing the same three methods is
provided so that thousands of Monte-Carlo runs can be executed quickly.

Strategy ("census - opportunistic triangulation - homing - verification"):

  phase A  census      : measure every channel at the entry point; each detected
                         channel yields one bearing ray.
  phase B  task loop   : repeatedly execute the cheapest useful task
                          * CLEAR(c)   : a located source, cleared by bearing
                                         homing with the Q2 geometry rule,
                          * LOCALISE(c): obtain a second bearing for a channel
                                         that is detected but not yet located,
                                         from the Q2-optimal vantage point,
                          * PROBE(p)   : drive to a survey stop of a triangular
                                         lattice and measure the unresolved
                                         channels (this both discovers hidden
                                         sources and, together with the
                                         verification test, certifies channels
                                         that do not exist).
  phase C  verification: a channel is certified empty when the positions at which
                         it returned "no_signal" prevent any source from hiding
                         (omni: a 1000 m cover; directional: the "no direction
                         can hide" test of section 4 of the paper).
"""

import json
import math
import os
import random
import time

import geom_core as g
import simulator as sim

EPS = 1.0
ARENA_R = 1800.0
R_MIN = 1000.0
R_MAX = 1500.0
SPEED = 5.0
VANTAGE_B = 1000.0            # Q2 result: |S1S2| ~ R_min
VANTAGE_PHI = 37.0            # Q2 result: +-37 deg off the measured bearing


# ===========================================================================
# clients
# ===========================================================================
class HTTPClient(object):
    """Thin HTTP client for the simulator interface (附件2)."""

    def __init__(self, robot_id, port=2026, host="127.0.0.1", timeout=15.0):
        self.robot_id = robot_id
        self.base = "http://%s:%d" % (host, port)
        self.timeout = timeout
        self.n_requests = 0
        self.t_wall = 0.0
        self._session = None

    def _post(self, path, payload, request_id):
        import requests
        body = dict(payload)
        body["arena_id"] = "default"
        body["robot_id"] = self.robot_id
        body["request_id"] = request_id
        t0 = time.time()
        last = None
        for attempt in range(4):
            try:
                r = requests.post(self.base + path, json=body,
                                  headers={"Content-Type": "application/json; charset=utf-8"},
                                  timeout=self.timeout)
                self.n_requests += 1
                self.t_wall += time.time() - t0
                if r.status_code != 200:
                    raise RuntimeError("HTTP %d: %s" % (r.status_code, r.text[:200]))
                js = r.json()
                if not js.get("accepted", False):
                    raise RuntimeError("rejected: %s" % json.dumps(js)[:200])
                return js
            except Exception as exc:                      # retry the SAME request
                last = exc
                time.sleep(0.05 * (attempt + 1))
        raise RuntimeError("request failed: %s" % last)

    def enter(self, rid="enter-1"):
        return self._post("/enter", {}, rid)

    def exit(self, rid="exit-1"):
        return self._post("/exit", {}, rid)

    def measure(self, request_id, x, y, channel):
        return self._post("/measure", {"position": {"x": float(x), "y": float(y)},
                                       "channel": int(channel)}, request_id)

    def clear(self, request_id, x, y, channel):
        return self._post("/clear", {"position": {"x": float(x), "y": float(y)},
                                     "channel": int(channel)}, request_id)


class LocalClient(object):
    """In-process adapter with the same call signature as HTTPClient."""

    def __init__(self, arena, robot_id="local-team"):
        self.arena = arena
        self.robot_id = robot_id
        self.n_requests = 0
        self.t_wall = 0.0
        self._k = 0
        self.sources = arena.sources

    def _rid(self, tag):
        self._k += 1
        return "%s-%d" % (tag, self._k)

    def enter(self, rid=None):
        return self.arena.enter(self.robot_id, rid or self._rid("enter"))

    def exit(self, rid=None):
        return self.arena.exit(self.robot_id, rid or self._rid("exit"))

    def measure(self, request_id, x, y, channel):
        self.n_requests += 1
        return self.arena.measure(self.robot_id, request_id or self._rid("m"),
                                  {"x": x, "y": y}, channel)

    def clear(self, request_id, x, y, channel):
        self.n_requests += 1
        return self.arena.clear(self.robot_id, request_id or self._rid("c"),
                                {"x": x, "y": y}, channel)


# ===========================================================================
# helpers used by the verification test
# ===========================================================================
def _origin_inside_hull(points, tol=1e-9):
    """
    Strict positive-spanning test: is the origin in the INTERIOR of the convex
    hull of `points`?  Equivalently: no open half plane through the origin
    contains all the points, i.e. no radiation sector can hide a source.
    """
    pts = [(round(p[0], 6), round(p[1], 6)) for p in points]
    pts = list(set(pts))
    if len(pts) < 3:
        return False
    hull = g.convex_hull(pts)
    if len(hull) < 3:
        return False
    # the origin must be strictly left of every directed hull edge
    n = len(hull)
    for i in range(n):
        a = hull[i]
        b = hull[(i + 1) % n]
        cr = (b[0] - a[0]) * (0.0 - a[1]) - (b[1] - a[1]) * (0.0 - a[0])
        if cr <= tol:
            return False
    return True


# ===========================================================================
# robot brain
# ===========================================================================
DEFAULT_PARAMS = {
    "policy": "planned",        # "planned" (covering tour + TSP) or "greedy"
    "census": True,             # measure all 20 channels at the entry point
    "probe_spacing": 650.0,     # go at least this far before probing again
    "probe_min_angle": 22.0,    # min predicted intersection angle to re-measure
    "locate_sigma": 320.0,      # uncertainty radius accepted as "located"
    "term_iters": 9,            # iterations of the terminal homing loop
    "term_cap": 420.0,          # max length of one homing step
    "clear_try_radius": 42.0,   # try the clear action when the estimate is this close
    "endgame_radius": 90.0,     # switch to the local clear pattern below this
    "endgame_step": 11.0,       # spacing of the local clear pattern
    "sweep_center_first": True,  # try the estimate centre before the ring
    "orient_belief": False,    # 定向源朝向硬约束可行集（自主设计的改进）
    "orient_bins": 24,         # 朝向分箱数（24 = 每箱 15 度）
    "orient_len": 350.0,       # 前向侧取数点的距离
    "survey_max_r": 1800.0,    # truncate the certification lattice radius
    "vantage_b": VANTAGE_B,
    "vantage_phi": VANTAGE_PHI,
    "vantage_b_local": 550.0,   # short oblique offset used when no covering
    "vantage_phi_local": 55.0,  # stop is pending
    "vantage_max_tries": 3,
    "survey_spacing": 1000.0,   # lattice spacing of the survey stops
    "survey_mode": "ring",      # "ring" (problem 3) or "lattice" (problem 4)
    "search_cost_bias": 60.0,   # seconds of "fixed cost" per search stop
    "use_ring": True,           # force the planned search stops
    "ring_radius": 1280.0,      # radius of the primary covering ring
    "ring_n": 6,                # number of stops on that ring (6 = hexagon)
    "ring_rotation": 0.0,       # rotation (deg) of the covering hexagon
    "max_attempts": 6,          # per-channel budget of clear attempts
    "hard_attempt_cap": 24,     # absolute cap of clear attempts per channel
                                # (raised: the exhaustive fallback now
                                #  guarantees convergence on located sources)
    "progress_ratio": 0.7,      # a better localisation re-opens the budget
    "clear_bonus": 260.0,       # task priority bonus (seconds)
    "localise_bonus": 120.0,
    "probe_bonus": 150.0,
    "max_channels_probe": 20,
    "dir_search_r": 60.0,       # re-acquisition radius around an estimate
    "oracle_count": False,      # debug only
    # verification test
    "verify_grid": 60.0,        # spacing (m) of the certification lattice
    "verify_margin": 90.0,     # candidates closer to the rim than this
                                # are excluded: they can never be certified
                                # with in-domain readings (theorem 2)
    "verify_r": R_MIN,          # guaranteed reception radius used for the test
    "rim_patrol": False,         # visit points just outside the rim when a
                                # candidate location cannot be certified inside
    "rim_step": 130.0,          # radial offset (m) of those outside samples
    "rim_max_pts": 9,           # cap on outside samples per search step
    "max_rim_patrols": 12,     # total number of outside sampling trips
    "oropt_limit": 12,          # Or-opt prefix used when re-planning often
    "oropt_limit_batch": 60,    # ... and when re-planning rarely (batch mode)
    "replan_mode": "each",      # MEASURED NEGATIVE: re-plan after every task
                                # beats committing to a stale tour
    "adaptive_batch": 4,        # 自适应采样一次取几个候选站位交给巡回规划
    "rim_ring_n": 0,            # 贴边环：在 r=rim_ring_r 上补 n 个站位，
                                # 专门发现"朝外辐射"的贴边定向源
    "rim_ring_r": 1750.0,
    "spread_stops": True,       # order the survey stops by farthest-point
                                # sampling, so a cap keeps the arena covered
    "max_survey_stops": 0,      # cap on the number of primary survey stops
                                # (0 = no cap); an explicit time/ratio knob
    "periodic_cert": True,      # evaluate the certificate during the sweep so
                                # that certified channels stop being measured
    "periodic_cert_every": 2,   # ... after every N covering stops
    "cert_heard_channels": False,  # certification also covers channels that
                                # were already heard (wasteful: measured 18
                                # extra stops per case), kept as a switch
    "phase_separate": False,    # MEASURED NEGATIVE (see the report): clearing
                                # early removes channels from the certification
                                # burden, so the phases must stay interleaved
    "perp_step": 80.0,          # endgame perpendicular vantage offset (m)
    "perp_sigma": 26.0,         # only when sigma is still above this
    "perp_max": 3,              # cap on perpendicular cuts per channel
    "enroute_clear": False,     # C1 measured NEUTRAL (881.3 vs 882.2 s over
                                # 24 cases): the priority bonus already
                                # captures that coupling
    "enroute_radius": 260.0,    #     detour budget (m)
    "adaptive_probe": True,     # C2: shrink the probe interval while many
    "probe_spacing_busy": 320.0,#     channels are still unresolved
    "busy_channels": 5,         #     "many" = this many unresolved
    "vantage_short_step": 35.0,   # MEASURED NEGATIVE, see the report: unused
    "skip_useless_stops": True,  # 邻域已被完全认证的普查站位直接跳过
    "leg_probe_step": 0.0,      # 长距离移动的分段长度（m）；>0 时途中顺带测量
    "leg_probe_max_channels": 8,  # 每个中间测点最多测几个频道
    "enroute_clear": False,     # MEASURED NEGATIVE (24 cases): 1.0000 -> 0.9946
                                # and 540.3 -> 573.3 s; the opportunistic clear
                                # interrupts the sweep and its own homing costs
                                # more than the detour it saves
    "enroute_radius": 520.0,    # "附近"的半径（m）
    "skip_certified": True,     # 站位附近已全部认证的频道不再测量
    "exhaustive_clear": True,   # 末段兜底：σ 圆盘上栅格穷举清除
    "exhaustive_grid": 15.0,    # 栅格间距（m）；15/√2 = 10.6 < 20 m 保证覆盖
    "exhaustive_after": 2,      # 常规末段连续失败几次后启用
    "exhaustive_cap": 80,       # 单次穷举的清除动作上限
    "relocate": True,           # 单条方位的频道：横向偏移二分 + 沿射线爬行
    "relocate_deltas": [400.0, 250.0, 150.0, 90.0, 55.0, 33.0, 20.0],
    "relocate_crawls": 4,       # 全部偏移失败后沿射线前进的次数
    "relocate_crawl_step": 200.0,
    "relocate_sigma": 900.0,    # 估计 sigma 大于此值仍视为"未定位"
    "vantage_step_onray": 200.0,  # creep along the ray instead of jumping
    "vantage_onray_bisect": True,  # retreat and halve when the signal is lost
    "vantage_onray_tries": 16,     # hop budget while creeping
    "vantage_onray": True,      # shrink the 2nd-station offset and finally
                                # go on the bearing ray (rim sources)
    "no_plain_fallback": True,  # directional runs: do not travel for a stop
                                # that cannot complete a certificate
    "outer_ring_gap": 0.0,      # distance of the outside ring beyond the rim
                                # (0 disables it; it makes the verification of
                                #  rim positions possible but costs a lot of
                                #  travel, see the discussion in the paper)
    "max_search_stops": 40,     # safety cap on the additional search stops
}


class Brain(object):
    def __init__(self, client, params=None, arena_radius=ARENA_R, verbose=False,
                 seed=0):
        self.cl = client
        self.p = dict(DEFAULT_PARAMS)
        if params:
            self.p.update(params)
        self.arena_r = arena_radius
        self.verbose = verbose
        self.rng = random.Random(seed)

        self.channels = list(range(1, 21))
        self.obs = dict((c, []) for c in self.channels)      # [(x, y, bearing)]
        self.nosig = dict((c, []) for c in self.channels)    # [(x, y)] no_signal
        self.status = dict((c, "unknown") for c in self.channels)
        self.est = dict((c, None) for c in self.channels)    # (x, y, sigma)
        self.near_hits = dict((c, 0) for c in self.channels)
        self.measure_points = dict((c, set()) for c in self.channels)
        self.vantage_tries = dict((c, 0) for c in self.channels)
        self.attempts = dict((c, 0) for c in self.channels)
        self.last_attempt_sigma = dict((c, None) for c in self.channels)
        self.total_attempts = dict((c, 0) for c in self.channels)
        self.last_seen = dict((c, None) for c in self.channels)
        self.meas_cache = {}
        nb = int(self.p.get("orient_bins", 24) or 24)
        # 朝向可行集：每个频道一组仍可行的朝向分箱
        self.orient_ok = dict((c, set(range(nb))) for c in self.channels)

        self.pos = (0.0, 0.0)
        self.vtime = 0.0
        self.cur_channel = 1
        self.rid = 0
        self.last_probe_pos = None
        self.visited_stops = set()
        self.rim_patrols = 0
        self.perp_tries = {}
        self.last_attempt_obs = {}
        self.onray_scale = {}
        self.onray_tries = {}
        self.reloc = {}
        self.survey_stops = self._make_survey_stops()
        self._stops_cache = None
        self.trace = []
        self.fail_log = []
        self._task_travel = {"clear": 0.0, "localise": 0.0, "probe": 0.0, "census": 0.0}
        self._task_count = {"clear": 0, "localise": 0, "probe": 0, "census": 0}
        self._task_time = {"clear": 0.0, "localise": 0.0, "probe": 0.0, "census": 0.0}
        self._cur_task = "census"

    # ------------------------------------------------------------------ utils
    def _rid_new(self, tag):
        self.rid += 1
        return "%s-%d" % (tag, self.rid)

    def _dist(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def _inside(self, p, margin=0.0):
        return math.hypot(p[0], p[1]) <= self.arena_r + margin

    def _clip_to_arena(self, p):
        r = math.hypot(p[0], p[1])
        if r <= self.arena_r:
            return p
        k = self.arena_r / r
        return (p[0] * k, p[1] * k)

    def _make_survey_stops(self, spacing=None):
        """Triangular lattice of survey stops covering the arena.

        `survey_max_r` (default = arena radius) truncates the lattice: only the
        region that actually has to be certified needs the multi-directional
        coverage a lattice provides, so the outer shell can be dropped when a
        separate mechanism (the rim ring) covers it.
        """
        s = self.p["survey_spacing"] if spacing is None else spacing
        rmax = float(self.p.get("survey_max_r", self.arena_r))
        stops = []
        ny = int(self.arena_r / (s * math.sqrt(3.0) / 2.0)) + 2
        nx = int(2 * self.arena_r / s) + 2
        for iy in range(-ny, ny + 1):
            y = iy * s * math.sqrt(3.0) / 2.0
            for ix in range(-nx, nx + 1):
                x = ix * s + (s / 2.0 if iy % 2 else 0.0)
                rr = math.hypot(x, y)
                if rr <= self.arena_r + 1e-9 and rr <= rmax + 1e-9:
                    stops.append((x, y))
        stops.sort(key=lambda p: math.hypot(p[0], p[1]))
        return stops

    def _spread_order(self, pts):
        """
        Farthest-point ordering: start at the point nearest the origin, then
        repeatedly append the point farthest from everything chosen so far.

        Truncating this list to N stops therefore keeps the arena evenly covered,
        whereas truncating the radius-sorted list would drop the outer ring -- the
        only chance of finding a source near the rim.
        """
        rest = [tuple(q) for q in pts]
        if not rest:
            return []
        first = min(rest, key=lambda q: q[0] * q[0] + q[1] * q[1])
        order = [first]
        rest.remove(first)
        while rest:
            nxt = max(rest, key=lambda q: min(
                (q[0] - a[0]) ** 2 + (q[1] - a[1]) ** 2 for a in order))
            order.append(nxt)
            rest.remove(nxt)
        return order

    def _all_search_stops(self):
        """
        Search lattice in several resolutions: if the coarse lattice cannot rule
        out every position, a finer one around the remaining hole is used, which
        keeps the search complete instead of giving up.
        In addition a ring of positions OUTSIDE the target region is offered.
        It is indispensable for the mixed problem: a directional source sitting on
        the rim may radiate outwards, so no measurement taken inside the arena can
        ever rule it out (all those points lie in one half plane through the
        source).  Measuring from outside the region closes that loophole, and the
        simulator explicitly accepts positions outside the target area.
        """
        if getattr(self, "_stops_cache", None) is None:
            s = self.p["survey_spacing"]
            pts = []
            for lvl in range(2):
                for p in self._make_survey_stops(s / (2.0 ** lvl)):
                    pts.append(p)
            rr = self.arena_r + self.p["outer_ring_gap"]
            n = int(2.0 * math.pi * rr / max(s, 400.0)) + 6
            for k in range(n):
                a = 2.0 * math.pi * k / n
                pts.append((rr * math.cos(a), rr * math.sin(a)))
            self._stops_cache = pts
        return self._stops_cache

    def _make_ring_stops(self):
        """
        Stops on a circle of radius `ring_radius` (plus the entry point) whose
        detection disks (radius R_min = 1000 m) cover the whole arena.  With
        `ring_n` = 6 this is the minimal complete-search configuration of the
        seven-point covering theorem (Kershner 1939); more points keep a larger
        coverage margin and give better triangulation geometry at the cost of
        extra legs.
        """
        r = self.p["ring_radius"]
        n = int(self.p.get("ring_n", 6) or 6)
        a0 = math.radians(self.p["ring_rotation"])
        return [(r * math.cos(a0 + 2.0 * math.pi * k / n),
                 r * math.sin(a0 + 2.0 * math.pi * k / n)) for k in range(n)]

    # ------------------------------------------------------------ verification
    def _verify_grid(self):
        if getattr(self, "_vgrid", None) is None:
            s = self.p["verify_grid"]
            lim = self.arena_r - float(self.p.get("verify_margin", 90.0))
            pts = []
            ny = int(self.arena_r / s) + 1
            for iy in range(-ny, ny + 1):
                y = iy * s
                for ix in range(-ny, ny + 1):
                    x = ix * s
                    if math.hypot(x, y) <= lim:
                        pts.append((x, y))
            self._vgrid = pts
        return self._vgrid

    def certification_scan(self, channels):
        """
        Decide, for every channel, whether the readings collected so far prove
        that no source can be hiding, and collect the arena positions that are
        not ruled out yet.

        omni  : q is ruled out when some reading position p obeys |p-q| <= R,
                because the source would certainly have been received there.
        directional (problem 4): a source at q radiates into a 180 deg sector,
                so q is ruled out only when NO direction u can hide it, i.e.
                when q lies in the interior of the convex hull of the reading
                positions inside the R disk (theorem 2).

        The status is maintained incrementally: "ruled out" is monotone (a new
        reading only enlarges the hull, or turns an empty set into a non empty
        one), so once a grid point is ruled out it never comes back, and every
        new reading is only tested against the grid points that are still open.

        Returns (all_certified, uncovered_points, per_channel_flags)
        """
        grid = self._verify_grid()
        slack = self.p["verify_grid"] * 0.7072
        R = self.p["verify_r"] - slack
        R2 = R * R
        directional = bool(self.p.get("directional", False))

        if getattr(self, "_cert_ruled", None) is None:
            self._cert_ruled = {}
            self._cert_open = {}
            self._cert_done = {}

        for c in channels:
            ruled = self._cert_ruled.setdefault(c, set())
            open_ = self._cert_open.setdefault(c, set(range(len(grid))))
            done = self._cert_done.get(c, 0)
            fresh = self.nosig[c][done:]
            if not fresh:
                continue
            readings = self.nosig[c]
            for p in fresh:
                px, py = p[0], p[1]
                for gi in list(open_):
                    q = grid[gi]
                    dx, dy = px - q[0], py - q[1]
                    if dx * dx + dy * dy > R2:
                        continue
                    near = [(r[0] - q[0], r[1] - q[1]) for r in readings
                            if (r[0] - q[0]) ** 2 + (r[1] - q[1]) ** 2 <= R2]
                    if not near:
                        continue
                    if not directional or _origin_inside_hull(near):
                        ruled.add(gi)
                        open_.discard(gi)
            self._cert_done[c] = len(readings)

        flags = {}
        uncovered = []
        seen = set()
        for c in channels:
            open_ = self._cert_open.get(c, set())
            flags[c] = (len(open_) == 0)
            if open_:
                for gi in open_:
                    if gi not in seen:
                        seen.add(gi)
                        uncovered.append(grid[gi])
        return (not uncovered), uncovered, flags

    # -------------------------------------------------------------- actions
    def _enroute_survey(self, x, y):
        """
        On the way to (x, y), stop every `leg_probe_step` metres and measure the
        channels that have never been heard.

        Those intermediate points cost no extra travel -- the leg is walked
        anyway -- so they are free sampling positions, and the certificate is
        exactly what needs readings for the never-heard channels.  This is what
        lets the dedicated survey stops be dropped.
        """
        step = float(self.p.get("leg_probe_step", 0.0) or 0.0)
        if step <= 0.0:
            return 0
        x0, y0 = self.pos
        d = math.hypot(x - x0, y - y0)
        if d <= 1.5 * step:
            return 0
        todo_all = [c for c in self.channels
                    if not self.obs.get(c)
                    and self.status.get(c) not in ("cleared", "empty")]
        if not todo_all:
            return 0
        k_max = int(self.p.get("leg_probe_max_channels", 8))
        n = int(d // step)
        done = 0
        for k in range(1, n + 1):
            t = k * step / d
            if t >= 0.92 or self.vtime > self.p.get("max_virtual_guard", 1e18):
                break
            px, py = x0 + (x - x0) * t, y0 + (y - y0) * t
            todo = [c for c in self.channels
                    if not self.obs.get(c)
                    and self.status.get(c) not in ("cleared", "empty")][:k_max]
            todo.sort()
            for c in todo:
                self.move_measure(px, py, c)      # d <= step: no recursion
                done += 1
        return done

    def move_measure(self, x, y, channel):
        """measure action (includes the implied move); returns the result dict"""
        x = float(max(-2.0e6, min(2.0e6, x)))
        y = float(max(-2.0e6, min(2.0e6, y)))
        if self.p.get("leg_probe_step", 0.0):
            self._enroute_survey(x, y)
        d = self._dist(self.pos, (x, y))
        sw = 1.0 if channel != self.cur_channel else 0.0
        self.vtime += d / SPEED + sw + 5.0
        self.pos = (x, y)
        self.cur_channel = channel
        r = self.cl.measure(self._rid_new("m"), x, y, channel)
        r["virtual_time_s"] = self.vtime
        self._task_travel[self._cur_task] += d
        self._task_time[self._cur_task] += d / SPEED + sw + 5.0
        self._handle_measure(channel, (x, y), r)
        self.meas_cache[(channel, (round(x, 2), round(y, 2)))] = r
        return r

    def move_clear(self, x, y, channel):
        x = float(max(-2.0e6, min(2.0e6, x)))
        y = float(max(-2.0e6, min(2.0e6, y)))
        d = self._dist(self.pos, (x, y))
        self.vtime += d / SPEED
        self.pos = (x, y)
        r = self.cl.clear(self._rid_new("c"), x, y, channel)
        # virtual cost of a clear action: 5 s on success, 3 s otherwise
        ct = 5.0 if r["clear_result"] == "success" else 3.0
        self.vtime += ct
        self._task_travel[self._cur_task] += d
        self._task_time[self._cur_task] += d / SPEED + ct
        if r["clear_result"] == "success":
            self.status[channel] = "cleared"
        return r

    def _handle_measure(self, c, pos, r):
        res = r["measure_result"]
        key = (round(pos[0], 2), round(pos[1], 2))
        self.measure_points[c].add(key)
        if res == "direction":
            self.obs[c].append((pos[0], pos[1], r["svd_deg"]))
            self.last_seen[c] = pos
            if self.status[c] in ("unknown", "empty"):
                self.status[c] = "seen"
        elif res == "near":
            self.near_hits[c] += 1
            self.last_seen[c] = pos
            self.status[c] = "seen"
        else:
            self.nosig[c].append((pos[0], pos[1]))

    # ------------------------------------------------------------ estimation
    def _best_pair(self, c):
        obs = self.obs[c]
        best = None
        for i in range(len(obs)):
            for j in range(i + 1, len(obs)):
                p1, p2 = obs[i], obs[j]
                if self._dist(p1, p2) < 25.0:
                    continue
                pt = self._ray_intersect(p1, p2)
                if pt is None:
                    continue
                gam = self._intersection_angle(p1, p2, pt)
                if best is None or gam > best[0]:
                    best = (gam, i, j, pt)
        return best

    @staticmethod
    def _ray_intersect(p1, p2):
        """Intersection of the two measured rays (p, bearing)."""
        x1, y1, b1 = p1
        x2, y2, b2 = p2
        a1 = math.radians(b1)
        a2 = math.radians(b2)
        d1x, d1y = math.cos(a1), math.sin(a1)
        d2x, d2y = math.cos(a2), math.sin(a2)
        den = d1x * d2y - d1y * d2x
        if abs(den) < 1e-9:
            return None
        t = ((x2 - x1) * d2y - (y2 - y1) * d2x) / den
        return (x1 + t * d1x, y1 + t * d1y)

    @staticmethod
    def _intersection_angle(p1, p2, pt):
        b1 = math.degrees(math.atan2(pt[1] - p1[1], pt[0] - p1[0]))
        b2 = math.degrees(math.atan2(pt[1] - p2[1], pt[0] - p2[0]))
        return abs(g.ang_diff(b1, b2))

    def update_estimate(self, c):
        """Least-squares style estimate built from the cross-fixing region."""
        if len(self.obs[c]) < 2:
            return None
        sts = [(o[0], o[1]) for o in self.obs[c]]
        bs = [o[2] for o in self.obs[c]]
        res = g.region_from_bearings(sts, bs, EPS)
        if res["empty"] or not res["bounded"] or len(res["vertices"]) == 0:
            bp = self._best_pair(c)
            if bp is None:
                return None
            gam, i, j, pt = bp
            sigma = R_MAX / max(math.sin(math.radians(gam)), 1e-3) * math.radians(EPS)
            return (pt[0], pt[1], max(sigma, 5.0))
        cx, cy, r = res["mec"]
        # the source must lie in the arena and within 1500 m of every station
        if not self._inside((cx, cy), 5.0):
            cx, cy = self._clip_to_arena((cx, cy))
        return (cx, cy, max(r, 1.0))

    def _commit_estimates(self):
        for c in self.channels:
            if self.status[c] == "cleared":
                continue
            if len(self.obs[c]) >= 2:
                e = self.update_estimate(c)
                if e is None:
                    continue
                self.est[c] = e
                if e[2] <= self.p["locate_sigma"]:
                    self.status[c] = "located"
            elif len(self.obs[c]) == 1 and self.est[c] is None:
                # a single bearing: use the middle of the plausible ray
                p = self.obs[c][0]
                r_lim = self._ray_limit(p)
                self.est[c] = (p[0] + 0.6 * r_lim * math.cos(math.radians(p[2])),
                               p[1] + 0.6 * r_lim * math.sin(math.radians(p[2])),
                               r_lim)
                if self.status[c] == "unknown":
                    self.status[c] = "seen"

    def _ray_limit(self, obs, cap=R_MAX):
        """Length of the plausible ray from `obs` before leaving the arena."""
        x, y, b = obs
        a = math.radians(b)
        dx, dy = math.cos(a), math.sin(a)
        # solve |p + t d| = arena_r
        bq = 2.0 * (x * dx + y * dy)
        cq = x * x + y * y - self.arena_r ** 2
        disc = bq * bq - 4.0 * cq
        t = cap
        if disc > 0:
            t1 = (-bq + math.sqrt(disc)) / 2.0
            t2 = (-bq - math.sqrt(disc)) / 2.0
            cand = [v for v in (t1, t2) if v > 0]
            if cand:
                t = min(t, min(cand))
        return max(t, 30.0)

    # ------------------------------------------------------------- probing
    def _worth_measuring(self, c, pos):
        if self.status[c] in ("cleared", "empty"):
            return False
        key = (round(pos[0], 2), round(pos[1], 2))
        if key in self.measure_points[c]:
            return False
        if self.status[c] == "unknown":
            if (self.p.get("skip_certified", True)
                    and not self._cert_open_near(c, pos)):
                # 该站位附近已被完全认证：此处不可能有源，测了没有信息量
                return False
            return True
        if self.status[c] == "located":
            return False
        if self.status[c] == "seen":
            if not self.obs[c]:
                return True
            # predicted intersection angle with the best existing bearing
            best = 0.0
            for o in self.obs[c]:
                r_lim = self._ray_limit(o)
                pt = (o[0] + 0.6 * r_lim * math.cos(math.radians(o[2])),
                      o[1] + 0.6 * r_lim * math.sin(math.radians(o[2])))
                if self._dist(o, pos) < 25.0:
                    continue
                best = max(best, self._intersection_angle(o, (pos[0], pos[1], 0.0), pt))
            if best >= self.p["probe_min_angle"]:
                return True
            if self.status[c] == "seen" and len(self.obs[c]) == 1:
                # the source may be invisible from the existing ray estimate:
                # probe anyway with a reduced priority
                return self._dist(pos, self.est[c][:2]) < R_MAX if self.est[c] else True
            return False
        return False

    def _enroute_clears(self, pos):
        """
        C1: located sources close to `pos`.  Visiting a search stop already pays
        for the travel, so neutralising a known source inside a small radius
        costs almost nothing; doing it later means paying for the trip twice.
        """
        if not self.p.get("enroute_clear", True):
            return 0
        rad = float(self.p.get("enroute_radius", 260.0))
        done = 0
        for c in list(self.channels):
            if self.status.get(c) in ("cleared", "empty"):
                continue
            e = self.est.get(c)
            if e is None or e[2] > self.p["locate_sigma"] * 3.0:
                continue
            if self._dist(pos, (e[0], e[1])) > rad:
                continue
            if self.total_attempts.get(c, 0) >= self.p["hard_attempt_cap"]:
                continue
            self._cur_task = "clear"
            self._task_count["clear"] += 1
            self.attempts[c] = self.attempts.get(c, 0) + 1
            self.total_attempts[c] = self.total_attempts.get(c, 0) + 1
            self.last_attempt_sigma[c] = e[2]
            self.last_attempt_obs[c] = len(self.obs.get(c, []))
            if self.clear_channel(c):
                done += 1
            else:
                self.est[c] = None
        return done

    def probe(self, pos, force=False):
        """Measure the unresolved channels at the current position."""
        spacing = self.p["probe_spacing"]
        if self.p.get("adaptive_probe", True):
            busy = sum(1 for c in self.channels
                       if self.status.get(c) not in ("cleared", "empty"))
            if busy >= self.p.get("busy_channels", 5):
                spacing = min(spacing, self.p.get("probe_spacing_busy", 320.0))
        if not force and self.last_probe_pos is not None:
            if self._dist(pos, self.last_probe_pos) < spacing:
                return 0
        todo = [c for c in self.channels if self._worth_measuring(c, pos)]
        # order by channel number: minimises the channel switching time
        todo.sort()
        n = 0
        for c in todo[:self.p["max_channels_probe"]]:
            self.move_measure(pos[0], pos[1], c)
            n += 1
        self.last_probe_pos = pos
        return n

    # ------------------------------------------------------- terminal homing
    def hear(self, c, pos):
        """
        Move to `pos` and measure channel `c`.  Repeating a measurement at the
        same point is useless (the reading error is a property of the location),
        so a cached reading is reused: only the travel time is paid.
        """
        key = (round(pos[0], 2), round(pos[1], 2))
        hit = self.meas_cache.get((c, key))
        if hit is not None:
            d = self._dist(self.pos, pos)
            self.vtime += d / SPEED
            self.pos = (float(pos[0]), float(pos[1]))
            self._task_travel[self._cur_task] += d
            self._task_time[self._cur_task] += d / SPEED
            return hit
        r = self.move_measure(pos[0], pos[1], c)
        self.meas_cache[(c, key)] = r
        return r

    # ---------------------------------------------------- orientation belief
    def _orient_update(self, c, q):
        """
        把一次 no_signal 转成对朝向的半平面约束 (q-p).u < 0，更新可行分箱。
        仅当估计位置与检测点距离不超过 R_min 时该约束才成立（否则可能只是超距）。
        """
        if not self.p.get("orient_belief", False):
            return
        est = self.est.get(c)
        if est is None:
            return
        dx, dy = q[0] - est[0], q[1] - est[1]
        d = math.hypot(dx, dy)
        if d < 1e-6 or d > float(self.p["verify_r"]):
            return
        nb = int(self.p.get("orient_bins", 24) or 24)
        ok = self.orient_ok.get(c)
        if not ok:
            return
        # 可行朝向必须指向背离 q 的一侧，即与 (q-p) 的夹角 > 90 度
        keep = set()
        for b in ok:
            ang = 2.0 * math.pi * (b + 0.5) / nb
            if math.cos(ang) * dx + math.sin(ang) * dy < 0.0:
                keep.add(b)
        self.orient_ok[c] = keep

    def _orient_front(self, c):
        """
        返回"源的前向侧"取数点：p + L*u_hat。u_hat 取所有幸存分箱中最靠近当前
        位置的方向（这样移动距离最短）。可行集为空时退回 None。
        """
        est = self.est.get(c)
        ok = self.orient_ok.get(c)
        if est is None or not ok:
            return None
        nb = int(self.p.get("orient_bins", 24) or 24)
        L = float(self.p.get("orient_len", 350.0))
        best = None
        for b in ok:
            ang = 2.0 * math.pi * (b + 0.5) / nb
            pt = (est[0] + L * math.cos(ang), est[1] + L * math.sin(ang))
            d = self._dist(self.pos, pt)
            if best is None or d < best[0]:
                best = (d, pt)
        if best is None:
            return None
        return self._clip_to_arena(best[1])

    def _retreat(self, c):
        """
        The channel is silent here.  Go back to the last position where it was
        heard and listen again.  For a directional source this is the only safe
        move: the segment joining a hearing point to the source lies inside the
        radiation sector, therefore reception is guaranteed to come back.
        """
        seen = self.last_seen.get(c)
        if self.p.get("orient_belief", False):
            # 自主设计的改法：背向丢失时主动绕到源的前向侧，而不是退回去
            front = self._orient_front(c)
            if front is not None and self._dist(self.pos, front) > 2.0:
                r = self.hear(c, front)
                if r.get("measure_result") in ("direction", "near"):
                    return True
        if seen is None:
            return False
        if self._dist(self.pos, seen) < 1.0:
            return False
        r = self.hear(c, seen)
        return r["measure_result"] in ("direction", "near")

    def _try_clear(self, c, pos=None):
        """A clear attempt at `pos` (default: current position)."""
        p = self.pos if pos is None else pos
        return self.move_clear(p[0], p[1], c)["clear_result"] == "success"

    def _local_clear_sweep(self, c, center, radius=None, sigma=None):
        """
        Endgame: the estimate is a few tens of metres from the source, so try the
        clear action on a small hexagonal pattern around it.  A clear costs only
        3 s when it misses, which makes this far cheaper than another homing
        cycle.  The pattern radius follows the uncertainty radius of the estimate
        (a clear succeeds anywhere inside 20 m).
        """
        if radius is None:
            s = 30.0 if sigma is None else sigma
            radius = min(max(0.55 * s, 12.0), 45.0)
        # The centre is the single best guess, so by default it is tried FIRST
        # (a miss costs only 3 s) and repeated LAST, so that a failed sweep still
        # leaves the robot standing on the estimate -- the position where an extra
        # bearing is most useful.
        if self.p.get("sweep_center_first", True):
            if self._try_clear(c, center):
                return True
        for k in range(6):
            a = math.radians(60.0 * k)
            p = self._clip_to_arena((center[0] + radius * math.cos(a),
                                     center[1] + radius * math.sin(a)))
            if self._try_clear(c, p):
                return True
        if radius > 24.0:
            for k in range(6):
                a = math.radians(30.0 + 60.0 * k)
                p = self._clip_to_arena((center[0] + 2.0 * radius * math.cos(a),
                                         center[1] + 2.0 * radius * math.sin(a)))
                if self._try_clear(c, p):
                    return True
        # the centre last: see the note above
        if self._try_clear(c, center):
            return True
        return False

    def _perp_cut(self, c, est):
        """
        Take one bearing from a point perpendicular to the line of sight and
        refresh the estimate.  Returns True when a new bearing was obtained.
        """
        if not self.obs.get(c):
            return False
        o = self.obs[c][-1]
        los = math.atan2(est[1] - o[1], est[0] - o[0])
        step = float(self.p["perp_step"])
        for sgn in (1.0, -1.0):
            a = los + sgn * math.pi / 2.0
            q = self._clip_to_arena((est[0] + step * math.cos(a),
                                     est[1] + step * math.sin(a)))
            if self._dist(q, (est[0], est[1])) < step * 0.5:
                continue
            r = self.hear(c, q)
            if r.get("measure_result") == "direction":
                e2 = self.update_estimate(c)
                if e2 is not None:
                    self.est[c] = e2
                return True
        return False

    def _enroute_clear(self, radius):
        """
        顺路清除：把"已定位且就在附近"的源当场清掉。

        必须走到离源 20 m 以内才能清除，所以"接近行程"本身省不掉；
        省掉的是"从扫描路线专门拐出去再拐回来"的往返。
        radius 取得比典型站距小（默认 520 m），保证只处理真正顺路的那些，
        不会为了顺路而打乱远处源的最优顺序。
        """
        if not self.p.get("enroute_clear", True):
            return 0
        done = 0
        thresh = float(self.p.get("locate_sigma", 320.0)) * 1.732
        for c in list(self.channels):
            if self.status.get(c) in ("cleared", "empty"):
                continue
            e = self.est.get(c)
            if e is None or e[2] > thresh:
                continue
            if self._dist(self.pos, (e[0], e[1])) > radius:
                continue
            if self.clear_channel(c):
                done += 1
                # 刚清完一个，状态可能变化，重新读取位置
        return done

    def _cert_open_near(self, c, pos):
        """
        pos 的认证半径邻域内是否还有"尚未被排除"的候选点。

        返回 False 表示该处对频道 c 已无信息量（测了也不会改变任何结论）。
        """
        ruled = self._cert_ruled.get(c) if getattr(self, "_cert_ruled", None) else None
        if ruled is None:
            return True                      # 认证结构尚未建立：保守地测
        R = self.p["verify_r"] - self.p["verify_grid"] * 0.7072
        R2 = R * R
        for gi, q in enumerate(self._verify_grid()):
            dx, dy = q[0] - pos[0], q[1] - pos[1]
            if dx * dx + dy * dy > R2:
                continue
            if gi not in ruled:
                return True
        return False

    def _exhaustive_clear(self, c, center, sigma):
        """
        在 σ 圆盘上按 <=15 m 间距穷举清除。

        这是"有保证"的兜底：间距 g 的方形栅格中，圆盘内任一点到最近栅格点
        不超过 g/sqrt(2)。取 g=15 m 得 10.6 m < 20 m 的清除半径，
        因此只要真值落在 σ 圆盘内（由问题一的定位区域保证），必定命中。
        """
        g = float(self.p.get("exhaustive_grid", 15.0))
        cap = int(self.p.get("exhaustive_cap", 80))
        rad = max(sigma, 20.0)
        n = int(rad / g) + 1
        tried = 0
        pts = []
        for iy in range(-n, n + 1):
            for ix in range(-n, n + 1):
                dx, dy = ix * g, iy * g
                if dx * dx + dy * dy > rad * rad:
                    continue
                pts.append((dx * dx + dy * dy, center[0] + dx, center[1] + dy))
        pts.sort()                      # 从中心向外，先试最可能的
        for item in pts:
            q = (item[1], item[2])
            if tried >= cap:
                break
            tried += 1
            if self._try_clear(c, q):
                return True
        return False

    def _bracket_clear(self, c, p_from, p_to):
        """
        The channel went silent right after a step: the walk overran the source,
        so the source lies on the segment between the last hearing point and the
        current position.  Try the cheap clear action (3 s when it misses) along
        that segment.
        """
        for f in (0.5, 0.25, 0.7, 0.85, 0.15):
            p = (p_from[0] + f * (p_to[0] - p_from[0]),
                 p_from[1] + f * (p_to[1] - p_from[1]))
            if self._try_clear(c, p):
                return True
        return False

    def clear_channel(self, c):
        """
        Bearing homing: walk along the measured bearing, shrinking the step as
        the estimate improves, and clear as soon as the source is inside the
        20 m clear radius.  Returns True when the source has been cleared.
        """
        dbg = getattr(self, "debug_channel", None) == c
        step_scale = 1.0
        for it in range(self.p["term_iters"]):
            est = self.est[c]
            if est is None:
                est = self.update_estimate(c)
                if est is None:
                    return False
                self.est[c] = est
            d = self._dist(self.pos, est[:2])
            # 1) close enough according to the estimate: a miss only costs 3 s
            if d <= self.p["clear_try_radius"]:
                if self._try_clear(c):
                    return True
            # 2) endgame: small pattern around the estimate
            if d <= self.p["endgame_radius"]:
                if self._local_clear_sweep(c, est[:2], sigma=est[2]):
                    return True
                # 兜底：常规图案连续失败后，在 σ 圆盘上做有保证的栅格穷举
                if (self.p.get("exhaustive_clear", True)
                        and self.attempts.get(c, 0) >= int(
                            self.p.get("exhaustive_after", 2))
                        and self._exhaustive_clear(c, est[:2], est[2])):
                    return True
                # 2b) the estimate is coarse because the bearings were taken from
                #     nearly collinear points along the homing path.  One cut
                #     perpendicular to the line of sight constrains the range and
                #     collapses sigma, which is what makes the pattern work.
                if (est[2] > self.p["perp_sigma"]
                        and self.perp_tries.get(c, 0) < self.p["perp_max"]
                        and self._perp_cut(c, est)):
                    self.perp_tries[c] = self.perp_tries.get(c, 0) + 1
                if d <= self.p["endgame_radius"] * 0.5:
                    return False
            # 3) make sure we are standing on a point where the source is heard
            if self.last_seen[c] is None or self._dist(self.pos, self.last_seen[c]) > 2.0:
                res = self.hear(c, self.pos)
                if dbg:
                    print("   [home %s it%d] hear here %s pos=%s d_est=%.0f"
                          % (c, it, res.get("measure_result"),
                             tuple(round(v) for v in self.pos), d))
                if res.get("measure_result") == "near":
                    if self._try_clear(c):
                        return True
                    continue
                if res.get("measure_result") == "no_signal":
                    self._orient_update(c, self.pos)
                    if not self._retreat(c):
                        return False
                    continue
            # 4) walk along the last measured bearing towards the source.  The
            #    step is scaled down every time the walk overruns the source
            #    (bisection), so the source is approached from the side on which
            #    it was heard -- which also keeps a directional source inside
            #    its radiation sector.
            o = self.obs[c][-1]
            step = max(6.0, min(float(self.p.get("term_step_frac", 0.7)) * d,
                               self.p["term_cap"])) * step_scale
            # Walk towards the ESTIMATE, not along the raw last bearing: that
            # bearing was measured at o[:2] and is only valid there.  Reusing its
            # angle from a position hundreds of metres away sent the robot the
            # wrong way (58 deg off, every step away from the target).  When the
            # robot does stand on the observation point the two coincide.
            b = math.atan2(est[1] - self.pos[1], est[0] - self.pos[0])
            tgt = self._clip_to_arena((self.pos[0] + step * math.cos(b),
                                       self.pos[1] + step * math.sin(b)))
            if self._dist(tgt, self.pos) < 5.0:
                a = self.rng.uniform(0.0, 2.0 * math.pi)
                tgt = (self.pos[0] + 8.0 * math.cos(a), self.pos[1] + 8.0 * math.sin(a))
            res = self.move_measure(tgt[0], tgt[1], c)
            self.meas_cache[(c, (round(tgt[0], 2), round(tgt[1], 2)))] = res
            if dbg:
                print("   [home %s it%d] walk %.0f m -> %s  res=%s scale=%.2f" %
                      (c, it, step, tuple(round(v) for v in tgt),
                       res.get("measure_result"), step_scale))
            if res["measure_result"] == "near":
                if self._try_clear(c, tgt):
                    return True
            elif res["measure_result"] == "direction":
                e2 = self.update_estimate(c)
                if e2 is not None:
                    self.est[c] = e2
                step_scale = min(1.0, step_scale * 1.3)
                if dbg:
                    print("       new est %s" % (tuple(round(v) for v in self.est[c]),))
            else:
                self._orient_update(c, tgt)
                step_scale *= 0.45
                if self.p.get("bracket_clear", True) and self._bracket_clear(c, self.last_seen[c], tgt):
                    return True
                if not self._retreat(c):
                    return False
        return False

    # --------------------------------------------------------------- vantage
    def vantage_point(self, c, local=False):
        """
        Second-station rule of problem 2.  `local=True` uses the short oblique
        offset (cheap, used when a covering stop is not available); otherwise the
        robust rule |S1S2| ~ R_min at +-37 deg off the measured bearing.
        """
        o = self.obs[c][-1]
        r_lim = self._ray_limit(o)
        tries = self.vantage_tries.get(c, 0)
        onray = False
        if local:
            b = min(self.p["vantage_b_local"], max(220.0, 0.6 * r_lim))
            phi0 = self.p["vantage_phi_local"]
        else:
            b = min(self.p["vantage_b"], max(260.0, 0.85 * r_lim))
            phi0 = self.p["vantage_phi"]
        # For a directional source on the rim the lit cap is thin, so a large
        # offset lands on the dark side.  Shrink the offset as attempts fail and
        # finally go ON the bearing ray, which the ray lemma guarantees is lit.
        if self.p.get("vantage_onray", True):
            if tries <= 0:
                phi0 = min(phi0, 45.0)
            elif tries == 1:
                phi0 = min(phi0, 20.0)
            else:
                # On-ray: creep instead of jumping.  A long hop can pass the
                # source and land on the dark side (the range is unknown), so the
                # step is short and is halved whenever the signal is lost.
                phi0 = 0.0
                onray = True
                b = min(float(self.p.get("vantage_step_onray", 200.0))
                        * self.onray_scale.get(c, 1.0), max(r_lim - 1.0, 12.0))
                b = max(b, 12.0)
        phis = (phi0, -phi0)
        best = None
        for sgn in (+1.0, -1.0):
            for phi in phis:
                ang = math.radians(o[2] + sgn * abs(phi))
                p = (o[0] + b * math.cos(ang), o[1] + b * math.sin(ang))
                if not self._inside(p, 60.0):
                    p = self._clip_to_arena(p)
                # prefer the side that keeps the robot inside the arena and
                # requires the least travel
                cost = self._dist(self.pos, p) / SPEED
                if not self._inside(p, 0.0):
                    cost += 200.0
                if best is None or cost < best[0]:
                    best = (cost, p)
        if best is None:
            return None
        return best[1] if not onray else (best[1], True)

    # ------------------------------------------------------------ main loop
    def run(self, max_actions=6000):
        self.cl.enter()
        n_act = 0
        if self.p["census"]:
            self._cur_task = "census"
            for c in self.channels:
                self.move_measure(0.0, 0.0, c)
                n_act += 1
            self._task_count["census"] += 1
            self.last_probe_pos = (0.0, 0.0)
        self._ring_stops = self._make_ring_stops()
        if self.p["policy"] == "planned":
            n_act = self._run_planned(n_act, max_actions)
        else:
            n_act = self._run_greedy(n_act, max_actions)
        try:
            self.cl.exit()
        except Exception:
            pass
        return self.stats()

    # -------------------------------------------------------- planned policy
    def _rim_ring_stops(self):
        """
        贴边环：在半径 rim_ring_r 上均匀放 n 个站位。

        贴边且朝外辐射的定向源，其域内受光区是一条贴着边界的薄月牙；
        任何方向的月牙都会与这圈站位相交，因此在环上均匀取样就能发现它。
        这些站位只服务于**发现**，与认证边距（verify_margin）无关。
        """
        n = int(self.p.get("rim_ring_n", 0) or 0)
        if n <= 0:
            return []
        r = float(self.p.get("rim_ring_r", 1750.0))
        rot = math.radians(float(self.p.get("ring_rotation", 0.0)))
        return [(r * math.cos(rot + 2.0 * math.pi * k / n),
                 r * math.sin(rot + 2.0 * math.pi * k / n)) for k in range(n)]

    def _primary_stops(self):
        """
        The planned search positions.
          'ring'    : centre + six stops on a circle; the minimal configuration
                      whose 1000 m reception disks cover the arena, sufficient
                      for omnidirectional sources (problem 3).
          'lattice' : a triangular lattice of the whole arena; each position is
                      surrounded from several directions in less than 1000 m,
                      which is what a directional source requires before it can
                      be declared absent (problem 4).
        """
        cached = getattr(self, "_primary_cache", None)
        if cached is not None:
            return list(cached)
        if self.p.get("survey_mode") == "adaptive":
            # 自适应：不预置任何站位，全部由认证扫描按需给出
            base = []
        elif self.p.get("survey_mode", "ring") == "lattice":
            base = list(self.survey_stops)
        else:
            base = self._make_ring_stops()
        # 贴边环在**任何模式**下都生效：它是"贴边朝外定向源"的唯一发现手段，
        # 与普查用什么形状无关。单独记下来，好让站位上限只作用于格点部分。
        self._rim_only = list(self._rim_ring_stops())
        base = base + self._rim_only
        if self.p.get("spread_stops", True) and base:
            # 最远点采样排序：截断时保留均匀覆盖，而不是砍掉外圈
            base = self._spread_order(base)
        self._primary_cache = list(base)
        self.survey_stops = list(base)
        return list(base)

    def _stop_is_useless(self, p):
        """
        True when p no longer needs a visit: every certification candidate within
        the certification radius of p is already ruled out for every channel that
        has not been certified yet.

        Then no source can hide there (so the visit would discover nothing) and the
        certificate does not need p's readings either.
        """
        if not self.p.get("skip_useless_stops", True):
            return False
        ruled_map = getattr(self, "_cert_ruled", None)
        if not ruled_map:
            return False
        open_ch = [c for c in self.channels
                   if self.status.get(c) not in ("cleared", "empty")
                   and not self.obs.get(c)]
        if not open_ch:
            return True
        R = self.p["verify_r"] - self.p["verify_grid"] * 0.7072
        R2 = R * R
        grid = self._verify_grid()
        for gi, q in enumerate(grid):
            dx, dy = q[0] - p[0], q[1] - p[1]
            if dx * dx + dy * dy > R2:
                continue
            for c in open_ch:
                if gi not in ruled_map.get(c, ()):
                    return False
        return True

    def _pending_stops(self):
        """
        Covering stops that still have to be visited.

        `max_survey_stops` caps only the LATTICE part.  The rim ring is always
        kept: it is the only way to discover sources that radiate outward from the
        rim, and capping the combined list silently dropped it entirely (which is
        why the earlier cap experiments looked so bad).
        """
        cap = int(self.p.get("max_survey_stops", 0) or 0)
        rim = set((round(q[0], 1), round(q[1], 1))
                  for q in getattr(self, "_rim_only", ()))
        out = []
        n_base = 0
        visited_base = sum(1 for k in self.visited_stops if k not in rim)
        for p in self._primary_stops():
            key = (round(p[0], 1), round(p[1], 1))
            if key in self.visited_stops:
                continue
            if self._stop_is_useless(p):
                continue
            if key not in rim:
                if cap > 0 and visited_base + n_base >= cap:
                    continue
                n_base += 1
            out.append(p)
        return out

    def _needs_stops(self):
        for c in self.channels:
            if self.status[c] == "cleared":
                continue
            if self.status[c] in ("unknown", "seen", "located"):
                return True
        return False

    def _build_tasks(self):
        """
        Task list.  Clearing targets always have priority; the covering stops are
        used for the second bearing whenever some of them are still pending, so
        that no extra detour is paid for the localisation.
        """
        tasks = []
        pending = self._pending_stops() if (self.p["use_ring"] and self._needs_stops()) else []
        clears = []
        for c in self.channels:
            if self.status[c] == "cleared":
                continue
            e = self.est[c]
            if e is None:
                continue
            good = (len(self.obs[c]) >= 2 and e[2] <= self.p["locate_sigma"]) or \
                   (len(self.obs[c]) >= 3 and e[2] <= self.p["locate_sigma"] * 3.0)
            if not good:
                continue
            # the attempt budget only throttles repeated failures at the same
            # quality: a clearly better localisation re-opens it, but a hard cap
            # prevents an endless loop on a source that cannot be cleared
            if self.total_attempts.get(c, 0) >= self.p["hard_attempt_cap"]:
                continue
            if self.attempts.get(c, 0) >= self.p["max_attempts"]:
                prev = self.last_attempt_sigma.get(c)
                prev_obs = self.last_attempt_obs.get(c, 0)
                # reopen when the localisation improved, or when new bearings
                # have arrived since the last attempt (a fresh cut can turn a
                # hopeless estimate into a solvable one)
                if (prev is not None and e[2] > self.p["progress_ratio"] * prev
                        and len(self.obs[c]) <= prev_obs):
                    continue
                self.attempts[c] = 0
            clears.append(("clear", c, (e[0], e[1])))
        if self.p.get("phase_separate", True) and pending:
            # SURVEY PHASE: while any covering stop is still unvisited, the tour
            # contains stops only.  Mixing a clearing detour into the sweep makes
            # the robot leave the survey area and come back, and the same detour is
            # then paid twice.
            return [("stop", None, q) for q in pending]
        tasks.extend(clears)
        # second bearings are preferably taken at positions the robot visits
        # anyway (probe after every action); a dedicated oblique offset is only
        # bought when no clearing target is left
        if not clears:
            for c in self.channels:
                if self.status[c] == "cleared":
                    continue
                if len(self.obs[c]) < 1:
                    continue
                if self._relocate_needed(c):
                    continue          # 由 relocate 机制负责，不用旧的斜向站位
                if (self.vantage_tries.get(c, 0) >= self.p["vantage_max_tries"]
                        and self.onray_tries.get(c, 0)
                        >= self.p.get("vantage_onray_tries", 16)):
                    continue
                p = self.vantage_point(c, local=True)
                if p is not None:
                    if isinstance(p, tuple) and len(p) == 2 and p[1] is True:
                        tasks.append(("vantage", c, p[0],
                                      {"onray": True,
                                       "origin": self.obs[c][-1][:2]}))
                    else:
                        tasks.append(("vantage", c, p))
                elif self.est[c] is not None:
                    tasks.append(("clear", c, (self.est[c][0], self.est[c][1])))
        cap = int(self.p.get("max_survey_stops", 0) or 0)
        if cap > 0:
            room = cap - len(self.visited_stops)
            pending = pending[:max(room, 0)]
        # 只有一条方位的频道：给它安排一次"横向偏移二分"观测。
        # 放在清除任务之后、覆盖站位之前——它便宜（短距离往返），
        # 而且一旦成功就把一个"已听到"的频道变成可清除的目标。
        if self.p.get("relocate", True):
            for c in self.channels:
                if self.status.get(c) in ("cleared", "empty"):
                    continue
                if not self._relocate_needed(c):
                    continue
                r = self._relocate_point(c)
                if r is not None:
                    tasks.append(("relocate", c, r[0]))
        for p in pending:
            tasks.append(("stop", None, p))
        return tasks

    # ------------------------------------------------- targeted search stops
    def next_search_stop(self, unresolved):
        """
        Greedy set-cover step for the verification search: among the candidate
        survey stops pick the one that rules out the largest number of arena
        positions per second of travel.
        Returns (stop, certified_flags) or (None, flags) when nothing is left.
        """
        if not self.p.get("cert_heard_channels", False):
            # A channel that was heard exists: it needs locating and clearing, not
            # a proof of absence.  Certifying it is logically pointless and, as
            # measured, costs about eighteen wasted stops per case.
            cert_set = [c for c in unresolved if not self.obs.get(c)]
        else:
            cert_set = list(unresolved)
        if not cert_set:
            return None, {}
        ok, uncov, flags = self.certification_scan(cert_set)
        for c, v in flags.items():
            if v:
                self.status[c] = "empty"
        if ok or not uncov:
            return None, flags
        slack = self.p["verify_grid"] * 0.7072
        R = self.p["verify_r"] - slack
        directional = bool(self.p.get("directional", False))
        best = None
        fallback = None
        for p in self._all_search_stops():
            if (round(p[0], 1), round(p[1], 1)) in self.visited_stops:
                continue
            gain = 0
            gain_plain = 0
            for q in uncov:
                dx, dy = p[0] - q[0], p[1] - q[1]
                if dx * dx + dy * dy > R * R:
                    continue
                gain_plain += 1
                if not directional:
                    gain += 1
                    continue
                # directional sources also need a NEW direction of observation
                a = math.atan2(dy, dx)
                fresh = True
                for c in unresolved:
                    for rp in self.nosig[c]:
                        ex, ey = rp[0] - q[0], rp[1] - q[1]
                        if ex * ex + ey * ey > R * R:
                            continue
                        if abs(g.ang_diff(math.degrees(a),
                                          math.degrees(math.atan2(ey, ex)))) < 55.0:
                            fresh = False
                            break
                    if not fresh:
                        break
                if fresh:
                    gain += 1
            cost = self._dist(self.pos, p) / SPEED + self.p["search_cost_bias"]
            if gain > 0:
                score = gain / cost
                if best is None or score > best[0]:
                    best = (score, p)
            elif gain_plain > 0 and not (directional
                                         and self.p.get("no_plain_fallback")):
                score = gain_plain / cost * 0.5
                if fallback is None or score > fallback[0]:
                    fallback = (score, p)
        if best is not None:
            return best[1], flags
        if not self.p.get("rim_patrol", True):
            return (fallback[1] if fallback else None), flags
        if self.rim_patrols >= int(self.p.get("max_rim_patrols", 12)):
            return (fallback[1] if fallback else None), flags
        # nothing inside the arena can help any more: try the outside samples
        # aimed at the rim candidates before giving up
        for p in self._rim_patrol_stops(uncov):
            gain = 0
            for q in uncov:
                dx, dy = p[0] - q[0], p[1] - q[1]
                if dx * dx + dy * dy <= R * R:
                    gain += 1
            if gain > 0:
                self.rim_patrols += 1
                return p, flags
        return (fallback[1] if fallback else None), flags

    def _mark_certified(self):
        """
        Evaluate the certificate during the sweep and mark the channels it proves
        absent as "empty".

        Nothing else would do it when the search stops are disabled, and a
        certified channel can never be heard again, so measuring it at every
        remaining stop is pure waste.
        """
        unresolved = [c for c in self.channels
                      if self.status[c] not in ("cleared", "empty")]
        if not self.p.get("cert_heard_channels", False):
            cert_set = [c for c in unresolved if not self.obs.get(c)]
        else:
            cert_set = list(unresolved)
        if not cert_set:
            return 0
        try:
            ok, uncov, flags = self.certification_scan(cert_set)
        except Exception:
            return 0
        n = 0
        for c, v in flags.items():
            if v and self.status.get(c) not in ("cleared", "empty"):
                self.status[c] = "empty"
                n += 1
        return n

    def _relocate_point(self, c):
        """
        为"只有一条方位"的频道给出**当前**候选观测点（纯查询，不改变状态）。

        状态机：按位于 self.reloc[c] 的 (d, side, crawl) 给出候选点；
        推进由 `_relocate_advance()` 在任务执行之后完成。
        """
        if not self.obs.get(c):
            return None
        st = self.reloc.setdefault(c, {"d": 0, "side": 0, "crawl": 0})
        deltas = list(self.p.get("relocate_deltas",
                                 [400.0, 250.0, 150.0, 90.0, 55.0, 33.0, 20.0]))
        if st["d"] >= len(deltas):
            return None
        o = self.obs[c][-1]
        anchor = self.reloc.get((c, "anchor"), (o[0], o[1]))
        brg = math.radians(o[2])
        d = deltas[st["d"]]
        sgn = 1.0 if st["side"] == 0 else -1.0
        a = brg + sgn * math.pi / 2.0
        q = self._clip_to_arena((anchor[0] + d * math.cos(a),
                                 anchor[1] + d * math.sin(a)))
        return q, "lateral %.0f m" % d

    def _relocate_advance(self, c):
        """任务执行之后推进状态：先换边，再放大 δ；都试完则沿射线爬行一步。"""
        st = self.reloc.setdefault(c, {"d": 0, "side": 0, "crawl": 0})
        deltas = list(self.p.get("relocate_deltas",
                                 [400.0, 250.0, 150.0, 90.0, 55.0, 33.0, 20.0]))
        if st["side"] == 0:
            st["side"] = 1
            return
        st["side"] = 0
        st["d"] += 1
        if st["d"] < len(deltas):
            return
        # 所有横向偏移都失败：沿射线前进，重新从最大偏移试起
        st["d"] = 0
        st["crawl"] += 1
        if st["crawl"] > int(self.p.get("relocate_crawls", 4)):
            return
        o = self.obs[c][-1]
        anchor = self.reloc.get((c, "anchor"), (o[0], o[1]))
        step = float(self.p.get("relocate_crawl_step", 200.0))
        brg = math.radians(o[2])
        nxt = self._clip_to_arena((anchor[0] + step * math.cos(brg),
                                   anchor[1] + step * math.sin(brg)))
        if self._dist(nxt, anchor) > 30.0:
            self.reloc[(c, "anchor")] = nxt

    def _relocate_needed(self, c):
        """频道听过但还没有可用估计。"""
        if not self.p.get("relocate", True):
            return False
        if not self.obs.get(c):
            return False
        e = self.est.get(c)
        return e is None or e[2] > float(self.p.get("relocate_sigma", 900.0))

    def next_search_batch(self, unresolved, k):
        """
        一次给出至多 k 个"认证最需要"的站位。

        单个站位交给巡回规划没有意义（只有一个点时无所谓顺序）；
        一批站位才能让 2-opt 在它们之间排出好路线。
        贪心地反复调用 next_search_stop，并把已选中的点临时视作已访问，
        以免一批里出现重复位置。
        """
        out = []
        for _ in range(max(int(k), 1)):
            stop, flags = self.next_search_stop(unresolved)
            if stop is None:
                break
            key = (round(stop[0], 1), round(stop[1], 1))
            if key in self.visited_stops:
                break
            self.visited_stops.add(key)          # 临时占位，避免重复
            out.append(stop)
        return out

    def _rim_patrol_stops(self, uncov):
        """
        Candidate positions just OUTSIDE the arena rim, aimed at the candidate
        locations that could not be certified from inside.

        For a candidate q close to the rim, every in-domain reading position p
        satisfies (p - q) pointing inward, so the origin can never lie inside
        the convex hull of the (p - q): no in-domain search can ever certify q
        (theorem 2).  Stepping a little outside, radially from the centre
        through q and slightly to both sides, produces directions that bracket
        q and makes the certificate reachable.
        """
        step = float(self.p.get("rim_step", 130.0))
        cap = int(self.p.get("rim_max_pts", 9))
        lim = self.arena_r - 2.0 * self.p["verify_grid"]
        out, seen = [], set()
        # nearest candidates first: the trip to the rim is the expensive part
        uncov = sorted(uncov, key=lambda q: self._dist(self.pos, q))
        for q in uncov:
            r = math.hypot(q[0], q[1])
            if r < lim:
                continue
            ux, uy = (q[0] / r, q[1] / r) if r > 1e-9 else (1.0, 0.0)
            for deg in (-38.0, 0.0, 38.0):
                a = math.radians(deg)
                dx = ux * math.cos(a) - uy * math.sin(a)
                dy = ux * math.sin(a) + uy * math.cos(a)
                k = step / max(0.35, math.cos(a))
                key = (round(q[0] + k * dx, 1), round(q[1] + k * dy, 1))
                if key in seen or key in self.visited_stops:
                    continue
                seen.add(key)
                out.append((q[0] + k * dx, q[1] + k * dy))
                if len(out) >= cap:
                    return out
        return out

    def _plan_tour(self, tasks, start):
        """
        Nearest-neighbour ordering of the task positions followed by a 2-opt
        improvement; the clear tasks receive a priority bonus so that they are
        visited early when they are not far away.
        """
        nodes = list(range(len(tasks)))
        if not nodes:
            return []
        pos = [t[2] for t in tasks]
        bonus = [self.p["clear_bonus"] if t[0] == "clear" else 0.0 for t in tasks]
        order = []
        cur = start
        remaining = set(nodes)
        while remaining:
            best = None
            for i in remaining:
                d = self._dist(cur, pos[i]) - bonus[i]
                if best is None or d < best[0]:
                    best = (d, i)
            order.append(best[1])
            remaining.discard(best[1])
            cur = pos[best[1]]
        # 2-opt improvement (open tour starting at `start`)
        improved = True
        guard = 0
        while improved and guard < 40:
            improved = False
            guard += 1
            for i in range(len(order) - 1):
                for j in range(i + 1, len(order)):
                    a = start if i == 0 else pos[order[i - 1]]
                    b = pos[order[i]]
                    c = pos[order[j]]
                    d = pos[order[j + 1]] if j + 1 < len(order) else None
                    old = self._dist(a, b) + (self._dist(c, d) if d else 0.0)
                    new = self._dist(a, c) + (self._dist(b, d) if d else 0.0)
                    if new < old - 1e-9:
                        order[i:j + 1] = order[i:j + 1][::-1]
                        improved = True

        # Or-opt over the WHOLE tour, with O(1) move evaluation.
        #
        # The plan is rebuilt after every executed task, so this has to stay
        # cheap; the constant-time delta below is what makes a full-tour Or-opt
        # affordable (the previous version only improved the first few tasks).
        def seg_delta(seq, i, j, k):
            """delta of moving seq[i:j+1] to just after position k"""
            n = len(seq)
            prev = start if i == 0 else pos[seq[i - 1]]
            first = pos[seq[i]]
            last = pos[seq[j]]
            nxt = pos[seq[j + 1]] if j + 1 < n else None
            gain = self._dist(prev, first)
            if nxt is not None:
                gain += self._dist(last, nxt) - self._dist(prev, nxt)
            else:
                gain += 0.0                       # open tour: nothing after
            if k < 0:
                a = start
                b = pos[seq[0]]
            else:
                a = pos[seq[k]]
                b = pos[seq[k + 1]] if k + 1 < n else None
            cost = self._dist(a, first)
            if b is not None:
                cost += self._dist(last, b) - self._dist(a, b)
            return cost - gain

        limit = int(self.p.get("oropt_limit_batch", 60))
        if self.p.get("replan_mode") == "each":
            limit = int(self.p.get("oropt_limit_full", 60))
        rounds = 0
        improved = True
        while improved and rounds < 12 and len(order) > 4:
            improved = False
            rounds += 1
            n = len(order)
            for L in (3, 2, 1):
                for i in range(n - L + 1):
                    if i >= limit:
                        break
                    j = i + L - 1
                    for k in range(-1, n - L):
                        if i <= k + 1 <= j:
                            continue
                        if seg_delta(order, i, j, k) < -1e-9:
                            seg = order[i:j + 1]
                            rest = order[:i] + order[j + 1:]
                            at = k + 1 if k < i else k + 1 - L
                            order = rest[:at] + seg + rest[at:]
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
        return [tasks[i] for i in order]

    def _run_planned(self, n_act, max_actions):
        replan = True
        tour = []
        extra_stops = []
        batch = self.p.get("replan_mode", "batch") == "batch"

        def heard_count():
            return sum(1 for c in self.channels if self.obs.get(c))

        def clear_count():
            return sum(1 for c in self.channels if self.status.get(c) == "cleared")

        last_heard, last_cleared = heard_count(), clear_count()
        while n_act < max_actions:
            self._commit_estimates()
            if self._all_done():
                break
            if replan or not tour:
                tasks = self._build_tasks()
                for p in extra_stops:
                    tasks.append(("stop", None, p))
                tour = self._plan_tour(tasks, self.pos)
                replan = False
                if not tour:
                    # no task left: decide whether the search may stop
                    unresolved = [c for c in self.channels
                                  if self.status[c] not in ("cleared", "empty")]
                    if not unresolved:
                        break
                    if self.p.get("survey_mode") == "adaptive":
                        # 自适应采样：一次取一批"认证最需要"的站位，
                        # 交给巡回规划排序（单个站位无顺序可言）
                        stops = self.next_search_batch(
                            unresolved, int(self.p.get("adaptive_batch", 4)))
                        if not stops:
                            break
                        tour = [("stop", None, q) for q in stops]
                    else:
                        stop, flags = self.next_search_stop(unresolved)
                        if (stop is None
                                or len(extra_stops) >= self.p["max_search_stops"]):
                            break
                        extra_stops.append(stop)
                        tour = [("stop", None, extra_stops.pop(0))]
            last_heard, last_cleared = heard_count(), clear_count()
            task = tour.pop(0)
            kind = task[0]
            if kind == "stop":
                # C1: the trip is already paid for, so take any located source
                # that sits next to this stop
                self._enroute_clears(task[2])
            if kind == "clear":
                self._cur_task = "clear"
                self._task_count["clear"] += 1
                self.attempts[task[1]] = self.attempts.get(task[1], 0) + 1
                self.total_attempts[task[1]] = self.total_attempts.get(task[1], 0) + 1
                if self.est[task[1]] is not None:
                    self.last_attempt_sigma[task[1]] = self.est[task[1]][2]
                self.last_attempt_obs[task[1]] = len(self.obs.get(task[1], []))
                ok = self.clear_channel(task[1])
                n_act += 1
                if not ok:
                    self.fail_log.append({"channel": task[1], "reason": "clear_failed",
                                          "pos": self.pos, "vtime": self.vtime})
                    self.est[task[1]] = None
                # a visited source position is a free vantage point: probe the
                # still unresolved channels here (discovery + verification)
                self.probe(self.pos)
                replan = (not batch) or heard_count() > last_heard or clear_count() > last_cleared
            elif kind == "relocate":
                self._cur_task = "localise"
                self._task_count["localise"] += 1
                c = task[1]
                p = task[2]
                r = self.move_measure(p[0], p[1], c)
                n_act += 1
                if r.get("measure_result") in ("direction", "near"):
                    # 拿到了第二条方位：重新估计，若可用则立刻转为可清除
                    e = self.update_estimate(c)
                    if e is not None:
                        self.est[c] = e
                    self.reloc.pop(c, None)
                    self.reloc.pop((c, "anchor"), None)
                else:
                    self._relocate_advance(c)
                self.probe(self.pos)
                replan = (not batch) or heard_count() > last_heard or clear_count() > last_cleared
            elif kind == "vantage":
                self._cur_task = "localise"
                self._task_count["localise"] += 1
                c = task[1]
                p = task[2]
                meta = task[3] if len(task) > 3 else {}
                self.vantage_tries[c] = self.vantage_tries.get(c, 0) + 1
                r = self.move_measure(p[0], p[1], c)
                n_act += 1
                if meta.get("onray") and self.p.get("vantage_onray_bisect", True):
                    self.onray_tries[c] = self.onray_tries.get(c, 0) + 1
                    if r.get("measure_result") in ("direction", "near"):
                        self.onray_scale[c] = 1.0
                    else:
                        # overshot: return to the hearing point and shorten the
                        # next hop so that it lands inside the lit part of the ray
                        self.onray_scale[c] = max(
                            0.08, self.onray_scale.get(c, 1.0) * 0.45)
                        o = meta.get("origin")
                        if o is not None:
                            self.hear(c, (o[0], o[1]))
                self.probe(self.pos)
                replan = (not batch) or heard_count() > last_heard or clear_count() > last_cleared
            else:                                    # covering stop
                self._cur_task = "probe"
                self._task_count["probe"] += 1
                p = task[2]
                self.visited_stops.add((round(p[0], 1), round(p[1], 1)))
                self.probe(p, force=True)
                n_act += 1
                self._commit_estimates()
                self._enroute_clear(float(self.p.get("enroute_radius", 520.0)))
                if self.p.get("periodic_cert", True):
                    self._since_cert = getattr(self, "_since_cert", 0) + 1
                    if self._since_cert >= int(self.p.get("periodic_cert_every", 2)):
                        self._since_cert = 0
                        self._mark_certified()
                replan = (not batch) or heard_count() > last_heard or clear_count() > last_cleared
        return n_act

    # --------------------------------------------------------- greedy policy
    def _run_greedy(self, n_act, max_actions):
        while n_act < max_actions:
            self._commit_estimates()
            if self._all_done():
                break
            task = self._choose_task()
            if task is None:
                break
            kind = task[0]
            if kind == "clear":
                self._cur_task = "clear"
                self._task_count["clear"] += 1
                c = task[1]
                ok = self.clear_channel(c)
                n_act += 1
                if not ok:
                    self.fail_log.append({"channel": c, "reason": "clear_failed",
                                          "pos": self.pos, "vtime": self.vtime})
                    # give up on this channel for a while
                    self.est[c] = None
                    if len(self.obs[c]) == 0:
                        self.status[c] = "seen"
            elif kind == "localise":
                self._cur_task = "localise"
                self._task_count["localise"] += 1
                c = task[1]
                p = task[2]
                self.move_measure(p[0], p[1], c)
                n_act += 1
                self._commit_estimates()
                self.probe(self.pos)
            elif kind == "probe":
                self._cur_task = "probe"
                self._task_count["probe"] += 1
                p = task[1]
                self.visited_stops.add((round(p[0], 1), round(p[1], 1)))
                # travel in two hops so that bearings are refreshed on the way
                mid = ((self.pos[0] + p[0]) / 2.0, (self.pos[1] + p[1]) / 2.0)
                if self._dist(self.pos, mid) > 300.0:
                    self.probe(mid, force=False)
                    self._commit_estimates()
                self.probe(p, force=True)
                n_act += 1
                self._commit_estimates()
                # opportunistic clearance: clear anything that became located
                self._clear_nearby(700.0)
        return n_act

    def _clear_nearby(self, radius):
        """Clear located sources close to the current position."""
        cands = [c for c in self.channels
                 if self.status[c] == "located" and self.est[c]
                 and self._dist(self.pos, self.est[c][:2]) <= radius]
        cands.sort(key=lambda c: self._dist(self.pos, self.est[c][:2]))
        for c in cands[:2]:
            self.clear_channel(c)

    def _all_done(self):
        """Termination: every channel is either cleared or certified empty."""
        for c in self.channels:
            if self.status[c] in ("cleared", "empty"):
                continue
            return False
        return True

    def _choose_task(self):
        cands = []
        for c in self.channels:
            if self.status[c] == "located" and self.est[c] is not None:
                t = self._dist(self.pos, self.est[c][:2]) / SPEED + 40.0
                cands.append((t - self.p["clear_bonus"], ("clear", c)))
            elif self.status[c] == "seen" and len(self.obs[c]) == 1:
                p = self.vantage_point(c)
                if p is not None:
                    t = self._dist(self.pos, p) / SPEED + 30.0
                    cands.append((t - self.p["localise_bonus"], ("localise", c, p)))
        # survey stops for unknown / unresolved channels
        if any(self.status[c] in ("unknown", "seen") for c in self.channels):
            best = None
            for p in self.survey_stops:
                key = (round(p[0], 1), round(p[1], 1))
                if key in self.visited_stops:
                    continue
                t = self._dist(self.pos, p) / SPEED
                if best is None or t < best[0]:
                    best = (t, p)
            if best is not None:
                cands.append((best[0] - self.p["probe_bonus"], ("probe", best[1])))
        if not cands:
            return None
        cands.sort(key=lambda x: x[0])
        return cands[0][1]

    # ---------------------------------------------------------------- stats
    def stats(self):
        arena = getattr(self.cl, "arena", None)
        if arena is not None:
            st = arena.stats()
        else:
            st = {}
        st["brain_vtime"] = self.vtime
        # task accounting: how much travel / time every task class consumed
        st["task_travel"] = dict((k, round(v, 1)) for k, v in self._task_travel.items())
        st["task_count"] = dict(self._task_count)
        st["task_time"] = dict((k, round(v, 1)) for k, v in self._task_time.items())
        return st


def run_case(sources, params=None, seed=0, arena_radius=ARENA_R, verbose=False):
    """Run one complete test on an in-process arena and return the statistics."""
    arena = sim.Arena(sources, seed=seed)
    client = LocalClient(arena, robot_id="local-team")
    brain = Brain(client, params=params, arena_radius=arena_radius,
                  verbose=verbose, seed=seed)
    st = brain.run()
    st["n_requests"] = client.n_requests
    arena.close()
    return st, brain


if __name__ == "__main__":
    rng = random.Random(1)
    srcs = sim.make_case(rng, n_sources=13)
    st, brain = run_case(srcs, seed=1)
    print(json.dumps(st, indent=1, ensure_ascii=False))
