#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
simulator.py -- local replica of the official "radio interference source"
environment simulator for 2026 CUMCM problem B.

The official simulator (downloadable only from the competition's Baidu-Netdisk
link, GUI + online registration required) could not be obtained in this
environment, therefore this module re-implements the documented behaviour
exactly as specified by 附件1 (simulator manual) and 附件2 (HTTP+JSON protocol):

  * POST /enter  /measure  /clear  /exit   on http://127.0.0.1:<port>
  * virtual clock: measure = move/5 + channel_switch(1 s if changed) + 5 s
                   clear   = move/5 + (5 s if cleared else 3 s)
  * move is implied by the position of the previous accepted action
  * /clear does NOT change the current channel
  * measure results: no_signal | near (<=5 m and inside coverage) | direction
  * bearing error: bounded by +-1 deg, FIXED for a given location (the local
    electromagnetic environment does not change), so repeating a measurement at
    the same point returns the same reading
  * effective reception radius per source: uniform in [1000, 1500] m
  * omni sources radiate in 360 deg; directional sources radiate in the 180 deg
    sector centred on their direction
  * clear radius 20 m, independent of the radiation pattern
  * request_id idempotency, strict field checking, HTTP status codes

Two entry points are provided:
  * class Arena           -- pure python API (used for massive Monte-Carlo runs)
  * serve(port, ...)      -- HTTP server implementing the protocol of 附件2
                             (used for the formal tests, identical to the
                             official interface, producing log files)
"""

import json
import math
import os
import random
import threading
import time
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ARENA_RADIUS = 1800.0
SPEED = 5.0                 # m/s
MEASURE_TIME = 5.0          # s
SWITCH_TIME = 1.0           # s
CLEAR_TIME_HIT = 5.0        # s (optical 3 s + laser 2 s)
CLEAR_TIME_MISS = 3.0       # s (optical only)
NEAR_RADIUS = 5.0           # m
CLEAR_RADIUS = 20.0         # m
R_EFF_LO, R_EFF_HI = 1000.0, 1500.0
MAX_VIRTUAL_DURATION = 360000.0
MAX_REAL_DURATION = 1200.0
BEARING_ERROR = 1.0         # deg, bounded and location dependent
ARENA_ID = "default"


# ---------------------------------------------------------------------------
# a single interference source
# ---------------------------------------------------------------------------
class Source(object):
    def __init__(self, channel, x, y, r_eff, kind="omni", direction=None):
        self.channel = channel
        self.x = x
        self.y = y
        self.r_eff = r_eff
        self.kind = kind                  # "omni" or "directional"
        self.direction = direction        # deg, None for omni
        self.cleared = False

    def pos(self):
        return (self.x, self.y)

    def covers(self, px, py):
        """Is the point inside the radiation sector (angular condition only)?"""
        if self.kind == "omni":
            return True
        vx, vy = px - self.x, py - self.y
        if vx * vx + vy * vy < 1e-18:
            return True
        a = math.radians(self.direction)
        # sector = +-90 deg around the direction vector
        return (vx * math.cos(a) + vy * math.sin(a)) >= 0.0


def make_case(rng, n_sources=None, n_channels=20, kind_mix=0.0, r_eff_lo=R_EFF_LO,
              r_eff_hi=R_EFF_HI, radius=ARENA_RADIUS, min_sep=0.0):
    """
    Random test case.  kind_mix = probability that a source is directional.
    Returns the list of sources (channels are distinct by construction).
    """
    if n_sources is None:
        n_sources = rng.randint(10, 16)
    chans = rng.sample(range(1, n_channels + 1), n_sources)
    srcs = []
    guard = 0
    while len(srcs) < n_sources and guard < 20000:
        guard += 1
        a = 2.0 * math.pi * rng.random()
        r = radius * math.sqrt(rng.random())
        x, y = r * math.cos(a), r * math.sin(a)
        if min_sep > 0 and any(math.hypot(x - s.x, y - s.y) < min_sep for s in srcs):
            continue
        kind = "directional" if rng.random() < kind_mix else "omni"
        direc = rng.uniform(0.0, 360.0) if kind == "directional" else None
        srcs.append(Source(chans[len(srcs)], x, y, rng.uniform(r_eff_lo, r_eff_hi),
                           kind, direc))
    return srcs


def _round_within_error(value, truth, bound):
    """
    Round `value` to two decimals without letting the deviation from `truth`
    exceed `bound`.  Rounding alone can push a value that sits exactly on the
    limit a few thousandths of a degree outside it, which would violate the
    +-1 deg guarantee of attachment 1.
    """
    v = round(value, 2)
    d = ((v - truth + 180.0) % 360.0) - 180.0
    while abs(d) > bound and abs(round(d, 6)) > 0.0:
        v = round(v - math.copysign(0.01, d), 2)
        d = ((v - truth + 180.0) % 360.0) - 180.0
    return v


def _loc_error(px, py, channel):
    """
    Bounded, location dependent bearing error in [-1, 1] deg.
    Identical for repeated measurements at the same (rounded) location, which
    reproduces the assumption of the problem statement.
    """
    key = "%.2f|%.2f|%d" % (round(px, 2), round(py, 2), channel)
    h = zlib.crc32(key.encode("utf-8")) & 0xFFFFFFFF
    return -BEARING_ERROR + 2.0 * BEARING_ERROR * (h / 4294967295.0)


# ---------------------------------------------------------------------------
# the arena (pure python API, mirrors the HTTP protocol one-to-one)
# ---------------------------------------------------------------------------
class Arena(object):
    def __init__(self, sources, log_path=None, seed=0):
        self.sources = list(sources)
        self.by_channel = {}
        for s in self.sources:
            self.by_channel[s.channel] = s
        self.virtual_time = 0.0
        self.pos = (0.0, 0.0)
        self.channel = 1
        self.robot_id = None
        self.started = False
        self.finished = False
        self.n_measure = 0
        self.n_clear = 0
        self.n_clear_hit = 0
        self.n_switch = 0
        self.n_no_signal = 0
        self.travel = 0.0
        self.log_path = log_path
        self.seed = seed
        self._rid_cache = {}
        self.log_handle = None
        if log_path:
            self.log_handle = open(log_path, "w", encoding="utf-8")

    # ---- logging ---------------------------------------------------------
    def _log(self, record):
        if self.log_handle is not None:
            self.log_handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            self.log_handle.flush()

    def close(self):
        if self.log_handle is not None:
            self.log_handle.close()
            self.log_handle = None

    # ---- helpers ---------------------------------------------------------
    def _step(self, target):
        """Advance the virtual clock for the movement towards `target`."""
        d = math.hypot(target[0] - self.pos[0], target[1] - self.pos[1])
        t = d / SPEED
        self.travel += d
        self.pos = (float(target[0]), float(target[1]))
        self.virtual_time += t
        return d, t

    def cleared_count(self):
        return sum(1 for s in self.sources if s.cleared)

    def stats(self):
        n_total = len(self.sources)
        n_clr = self.cleared_count()
        return {
            "n_sources": n_total,
            "n_cleared": n_clr,
            "clear_ratio": (n_clr / float(n_total)) if n_total else 0.0,
            "mean_time": (self.virtual_time / n_clr) if n_clr else float("inf"),
            "virtual_time": self.virtual_time,
            "travel_m": self.travel,
            "n_measure": self.n_measure,
            "n_clear": self.n_clear,
            "n_switch": self.n_switch,
            "n_no_signal": self.n_no_signal,
        }

    # ---- the four actions ------------------------------------------------
    def enter(self, robot_id, request_id):
        if self.started:
            return self._reject()
        self.started = True
        if self.robot_id is None:
            # the official runtime knows the team; binding on the first enter
            # reproduces that, so a later different id is rejected
            self.robot_id = robot_id
        rec = {"t": 0.0, "action": "enter", "pos": list(self.pos),
               "channel": self.channel, "request_id": request_id}
        self._log(rec)
        return {"accepted": True, "virtual_time_s": self.virtual_time,
                "max_virtual_duration_s": MAX_VIRTUAL_DURATION,
                "max_real_duration_s": MAX_REAL_DURATION,
                "remaining_real_duration_s": MAX_REAL_DURATION}

    def exit(self, robot_id, request_id):
        if not self.started:
            return self._reject()
        self.finished = True
        self._log({"t": self.virtual_time, "action": "exit",
                   "pos": list(self.pos), "channel": self.channel,
                   "request_id": request_id})
        return {"accepted": True, "virtual_time_s": self.virtual_time,
                "exit_reason": "user_exit"}

    def measure(self, robot_id, request_id, position, channel):
        if not self.started or self.finished:
            return self._reject()
        channel = int(channel)
        target = (float(position["x"]), float(position["y"]))
        moved, move_t = self._step(target)
        switch = 0.0
        if channel != self.channel:
            switch = SWITCH_TIME
            self.n_switch += 1
        self.channel = channel
        self.virtual_time += switch + MEASURE_TIME
        self.n_measure += 1

        src = self.by_channel.get(channel)
        result = "no_signal"
        svd = None
        dist = None
        if src is not None and not src.cleared:
            dist = math.hypot(target[0] - src.x, target[1] - src.y)
            if dist <= src.r_eff and src.covers(target[0], target[1]):
                if dist <= NEAR_RADIUS:
                    result = "near"
                else:
                    result = "direction"
                    true_brg = math.degrees(math.atan2(src.y - target[1],
                                                       src.x - target[0])) % 360.0
                    svd = (true_brg + _loc_error(target[0], target[1], channel)) % 360.0
                    svd = _round_within_error(svd, true_brg, BEARING_ERROR)
        if result == "no_signal":
            self.n_no_signal += 1

        out = {"accepted": True, "virtual_time_s": self.virtual_time,
               "measure_result": result}
        if svd is not None:
            out["svd_deg"] = svd
        self._log({"t": self.virtual_time, "action": "measure",
                   "pos": list(target), "channel": channel,
                   "move_m": moved, "move_s": move_t, "switch_s": switch,
                   "result": result, "svd_deg": svd, "request_id": request_id,
                   "n_cleared": self.cleared_count()})
        return out

    def clear(self, robot_id, request_id, position, channel):
        if not self.started or self.finished:
            return self._reject()
        channel = int(channel)
        target = (float(position["x"]), float(position["y"]))
        moved, move_t = self._step(target)
        self.n_clear += 1

        src = self.by_channel.get(channel)
        hit = False
        if src is not None and not src.cleared:
            if math.hypot(target[0] - src.x, target[1] - src.y) <= CLEAR_RADIUS:
                src.cleared = True
                hit = True
        self.virtual_time += CLEAR_TIME_HIT if hit else CLEAR_TIME_MISS
        if hit:
            self.n_clear_hit += 1
        out = {"accepted": True, "virtual_time_s": self.virtual_time,
               "clear_result": "success" if hit else "no_target_in_range"}
        self._log({"t": self.virtual_time, "action": "clear",
                   "pos": list(target), "channel": channel,
                   "move_m": moved, "move_s": move_t,
                   "result": out["clear_result"], "request_id": request_id,
                   "n_cleared": self.cleared_count()})
        return out

    def _reject(self):
        return {"accepted": False, "virtual_time_s": 0.0}


# ---------------------------------------------------------------------------
# HTTP layer (mirrors 附件2 exactly)
# ---------------------------------------------------------------------------
class _State(object):
    def __init__(self):
        self.arena = None
        self.robot_id = None


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "LocalArenaSim/1.0"

    def log_message(self, fmt, *args):
        pass                                   # keep the console clean

    # ---- utilities -------------------------------------------------------
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _err(self, code, msg):
        st = self.server.state
        vt = st.arena.virtual_time if st.arena else 0.0
        self._send(code, {"accepted": False,
                          "real_timestamp_ms": int(time.time() * 1000),
                          "virtual_time_s": vt, "error": msg})

    def do_POST(self):
        st = self.server.state
        path = self.path
        if path not in ("/enter", "/measure", "/clear", "/exit"):
            return self._err(404, "unknown path")
        ctype = self.headers.get("Content-Type", "")
        if not ctype.lower().startswith("application/json"):
            return self._err(415, "content type")
        ce = self.headers.get("Content-Encoding", "identity")
        if ce.lower() not in ("", "identity"):
            return self._err(415, "content encoding")
        try:
            n = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self._err(400, "bad length")
        if n > 65536:
            return self._err(413, "body too large")
        raw = self.rfile.read(n)
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            return self._err(400, "bad json")
        if not isinstance(body, dict):
            return self._err(400, "body must be an object")

        allowed = {"enter": {"arena_id", "robot_id", "request_id"},
                   "measure": {"arena_id", "robot_id", "request_id", "position", "channel"},
                   "clear": {"arena_id", "robot_id", "request_id", "position", "channel"},
                   "exit": {"arena_id", "robot_id", "request_id"}}[path[1:]]
        if set(body.keys()) - allowed:
            return self._send(200, {"accepted": False,
                                    "real_timestamp_ms": int(time.time() * 1000),
                                    "virtual_time_s": 0.0})
        for f in ("arena_id", "robot_id", "request_id"):
            if f not in body:
                return self._err(400, "missing " + f)
        if body["arena_id"] != ARENA_ID:
            return self._send(200, {"accepted": False,
                                    "real_timestamp_ms": int(time.time() * 1000),
                                    "virtual_time_s": 0.0})
        # the id is either fixed at launch or bound by the first /enter
        bound = st.robot_id
        if bound is None and st.arena is not None:
            bound = getattr(st.arena, "robot_id", None)
        if bound is not None and body["robot_id"] != bound:
            return self._send(200, {"accepted": False,
                                    "real_timestamp_ms": int(time.time() * 1000),
                                    "virtual_time_s": 0.0})
        if path in ("/measure", "/clear"):
            if "position" not in body or "channel" not in body:
                return self._err(400, "missing position/channel")
            p = body["position"]
            if not isinstance(p, dict) or "x" not in p or "y" not in p:
                return self._err(400, "bad position")
            if set(p.keys()) - {"x", "y"}:
                return self._send(200, {"accepted": False,
                                        "real_timestamp_ms": int(time.time() * 1000),
                                        "virtual_time_s": 0.0})
            for k in ("x", "y"):
                v = p[k]
                if isinstance(v, bool) or not isinstance(v, (int, float)):
                    return self._err(400, "bad coordinate")
                if not math.isfinite(v) or abs(v) > 2000000:
                    return self._err(400, "coordinate range")
            c = body["channel"]
            if isinstance(c, bool) or not isinstance(c, (int, float)):
                return self._err(400, "bad channel")
            if float(c) != int(c) or not (1 <= int(c) <= 20):
                return self._err(400, "channel range")

        # idempotency
        rid = body["request_id"]
        key = (path, rid)
        if key in st.arena._rid_cache:
            return self._send(200, st.arena._rid_cache[key])

        if st.arena is None:
            return self._err(400, "arena not ready")
        try:
            if path == "/enter":
                resp = st.arena.enter(body["robot_id"], rid)
            elif path == "/measure":
                resp = st.arena.measure(body["robot_id"], rid, body["position"],
                                        int(body["channel"]))
            elif path == "/clear":
                resp = st.arena.clear(body["robot_id"], rid, body["position"],
                                      int(body["channel"]))
            else:
                resp = st.arena.exit(body["robot_id"], rid)
        except Exception as exc:                            # pragma: no cover
            return self._err(500, str(exc))
        resp = dict(resp)
        resp["real_timestamp_ms"] = int(time.time() * 1000)
        st.arena._rid_cache[key] = resp
        return self._send(200, resp)


class ArenaHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def serve(port=2026, sources=None, log_path=None, robot_id=None, seed=0,
          ready_file=None):
    """Start the HTTP simulator (blocking).  Returns nothing."""
    arena = Arena(sources if sources is not None else make_case(random.Random(seed)),
                  log_path=log_path, seed=seed)
    st = _State()
    st.arena = arena
    st.robot_id = robot_id
    srv = ArenaHTTPServer(("127.0.0.1", port), _Handler)
    srv.state = st
    if ready_file:
        with open(ready_file, "w", encoding="utf-8") as f:
            f.write(str(port))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        arena.close()


def run_server_thread(port=2026, sources=None, log_path=None, robot_id=None, seed=0):
    arena = Arena(sources if sources is not None else make_case(random.Random(seed)),
                  log_path=log_path, seed=seed)
    st = _State()
    st.arena = arena
    st.robot_id = robot_id
    srv = ArenaHTTPServer(("127.0.0.1", port), _Handler)
    srv.state = st
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    return srv, arena


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=2026)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--log", default=None)
    ap.add_argument("--robot-id", default=None)
    ap.add_argument("--dir-mix", type=float, default=0.0)
    ap.add_argument("--n", type=int, default=0)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    srcs = make_case(rng, n_sources=(a.n or None), kind_mix=a.dir_mix)
    print("case: %d sources (%d directional)"
          % (len(srcs), sum(1 for s in srcs if s.kind == "directional")))
    serve(port=a.port, sources=srcs, log_path=a.log, robot_id=a.robot_id, seed=a.seed)
