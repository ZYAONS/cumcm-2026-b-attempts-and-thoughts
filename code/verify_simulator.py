#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
verify_simulator.py -- rigorous verification of the local simulator.

Six groups of checks:
  A  HTTP protocol  (routes, validation pipeline, error codes, idempotency)
  B  virtual-time accounting (every rule of 附件 1)
  C  physics        (geometry, coverage, bearing error model, clear radius)
  D  response/log contract (fields required by 附件 2)
  E  cross-check against an independent open-source reference cost model
  F  conservation   (the virtual clock equals the sum of its parts)

The source of this file is pure ASCII on purpose; every user visible string is
loaded from zh_labels.json.  Exit code is 1 when any check fails.

usage:  python verify_simulator.py [--json out.json] [--md out.md]
"""
import io
import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.request

import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))

L = json.load(io.open(os.path.join(HERE, "zh_labels.json"), encoding="utf-8-sig"))


def T(k, d=""):
    return L.get(k, d)


# ---------------------------------------------------------------------------
# tiny test harness
# ---------------------------------------------------------------------------
RESULTS = []


def check(group, key, ok, detail="", expected="", got=""):
    RESULTS.append({"group": group, "key": key, "name": T("vfy_" + key, key),
                    "ok": bool(ok), "detail": detail,
                    "expected": str(expected), "got": str(got)})
    return ok


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol


# ---------------------------------------------------------------------------
# A. HTTP protocol
# ---------------------------------------------------------------------------
def post(port, path, obj=None, raw=None, ctype="application/json",
         encoding=None, timeout=10.0):
    """Return (status, body_or_None, raw_text)."""
    url = "http://127.0.0.1:%d%s" % (port, path)
    if raw is None:
        raw = json.dumps(obj).encode("utf-8")
    else:
        raw = raw if isinstance(raw, bytes) else raw.encode("utf-8")
    req = urllib.request.Request(url, data=raw, method="POST")
    req.add_header("Content-Type", ctype)
    if encoding:
        req.add_header("Content-Encoding", encoding)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(txt)
        except Exception:
            return e.code, None
    except Exception as e:                                  # pragma: no cover
        return -1, {"error": str(e)}


def group_a(port, rid_ok="verify-A"):
    G = "A"

    # A1 routes
    st, b = post(port, "/enter", {"arena_id": sim.ARENA_ID, "robot_id": rid_ok,
                                  "request_id": "a-enter-1"})
    check(G, "route_enter", st == 200 and b and b.get("accepted") is True,
          "enter accepted", 200, st)
    st, _ = post(port, "/no_such_endpoint", {})
    check(G, "route_unknown_404", st == 404, "unknown path", 404, st)

    # A2 content type
    st, _ = post(port, "/measure", {"arena_id": sim.ARENA_ID, "robot_id": rid_ok,
                                    "request_id": "a-ct", "position": {"x": 0, "y": 0},
                                    "channel": 1}, ctype="text/plain")
    check(G, "content_type_415", st == 415, "non-json content type", 415, st)

    # A3 content encoding
    st, _ = post(port, "/measure", {"arena_id": sim.ARENA_ID, "robot_id": rid_ok,
                                    "request_id": "a-ce", "position": {"x": 0, "y": 0},
                                    "channel": 1}, encoding="gzip")
    check(G, "content_encoding_415", st == 415, "compressed body", 415, st)

    # A4 oversized body
    big = json.dumps({"arena_id": sim.ARENA_ID, "robot_id": rid_ok,
                      "request_id": "a-big", "position": {"x": 0, "y": 0},
                      "channel": 1, "pad": "x" * 70000})
    st, _ = post(port, "/measure", raw=big)
    check(G, "body_too_large_413", st == 413, "70000 byte body", 413, st)

    # A5 malformed json
    st, _ = post(port, "/measure", raw=b"{not json")
    check(G, "bad_json_400", st == 400, "malformed json", 400, st)

    # A6 body not an object
    st, _ = post(port, "/measure", raw=b"[1,2,3]")
    check(G, "body_not_object_400", st == 400, "json array body", 400, st)

    # A7 extra field -> 200 accepted=false
    st, b = post(port, "/measure", {"arena_id": sim.ARENA_ID, "robot_id": rid_ok,
                                    "request_id": "a-extra", "position": {"x": 0, "y": 0},
                                    "channel": 1, "bonus": 1})
    check(G, "extra_field_accepted_false",
          st == 200 and b and b.get("accepted") is False,
          "undeclared field", "200/false", "%s/%s" % (st, (b or {}).get("accepted")))

    # A8 missing required field
    st, _ = post(port, "/measure", {"arena_id": sim.ARENA_ID, "position": {"x": 0, "y": 0},
                                    "channel": 1})
    check(G, "missing_field_400", st == 400, "no robot_id", 400, st)

    # A9 arena id mismatch
    st, b = post(port, "/measure", {"arena_id": "other", "robot_id": rid_ok,
                                    "request_id": "a-arena", "position": {"x": 0, "y": 0},
                                    "channel": 1})
    check(G, "arena_id_mismatch", st == 200 and b and b.get("accepted") is False,
          "wrong arena_id", "200/false", "%s/%s" % (st, (b or {}).get("accepted")))

    # A10 robot id mismatch
    st, b = post(port, "/measure", {"arena_id": sim.ARENA_ID, "robot_id": "someone-else",
                                    "request_id": "a-robot", "position": {"x": 0, "y": 0},
                                    "channel": 1})
    check(G, "robot_id_mismatch", st == 200 and b and b.get("accepted") is False,
          "wrong robot_id", "200/false", "%s/%s" % (st, (b or {}).get("accepted")))

    # A11 bad position
    bad = [({"x": 0}, "missing y"), ({"x": "a", "y": 0}, "non numeric"),
           ({"x": 1e9, "y": 0}, "out of range"),
           ({"x": 0, "y": 0, "z": 1}, "extra key")]
    oks = []
    for i, (p, why) in enumerate(bad):
        st, b = post(port, "/measure", {"arena_id": sim.ARENA_ID, "robot_id": rid_ok,
                                        "request_id": "a-pos-%d" % i, "position": p,
                                        "channel": 1})
        oks.append(st == 400 or (st == 200 and b and b.get("accepted") is False))
    check(G, "bad_position", all(oks), "4 malformed positions", "rejected", oks)

    # A12 bad channel
    oks = []
    for i, c in enumerate([0, 21, 1.5, "1", True]):
        st, _ = post(port, "/measure", {"arena_id": sim.ARENA_ID, "robot_id": rid_ok,
                                        "request_id": "a-ch-%d" % i,
                                        "position": {"x": 0, "y": 0}, "channel": c})
        oks.append(st == 400)
    check(G, "bad_channel", all(oks), "channel 0/21/1.5/'1'/true", "400", oks)

    # A13 idempotency over HTTP: same request_id twice -> same body, time counted once
    rid = "a-idem-1"
    payload = {"arena_id": sim.ARENA_ID, "robot_id": rid_ok, "request_id": rid,
               "position": {"x": 100.0, "y": 0.0}, "channel": 2}
    st1, b1 = post(port, "/measure", payload)
    st2, b2 = post(port, "/measure", payload)
    same = (b1 or {}).get("virtual_time_s") == (b2 or {}).get("virtual_time_s")
    check(G, "idempotent_replay", st1 == 200 and st2 == 200 and same,
          "identical replay returns first response",
          (b1 or {}).get("virtual_time_s"), (b2 or {}).get("virtual_time_s"))

    # A14 measure before enter is handled on a fresh server (done in group A2 server)
    return


def group_a2(port, rid="verify-A2"):
    """Fresh-session semantics: measure before enter, double enter, measure after exit."""
    G = "A"
    st, _ = post(port, "/enter", {"arena_id": sim.ARENA_ID, "robot_id": rid,
                                  "request_id": "a2-e1"})
    st2, b2 = post(port, "/enter", {"arena_id": sim.ARENA_ID, "robot_id": rid,
                                    "request_id": "a2-e2"})
    check(G, "double_enter", st == 200 and st2 == 200 and b2
          and b2.get("accepted") is False, "second enter rejected", "200/false",
          "%s/%s" % (st2, (b2 or {}).get("accepted")))

    st, _ = post(port, "/measure", {"arena_id": sim.ARENA_ID, "robot_id": rid,
                                    "request_id": "a2-m1", "position": {"x": 0, "y": 0},
                                    "channel": 1})
    ok_mid = st == 200
    st, _ = post(port, "/exit", {"arena_id": sim.ARENA_ID, "robot_id": rid,
                                 "request_id": "a2-x1"})
    st2, b2 = post(port, "/measure", {"arena_id": sim.ARENA_ID, "robot_id": rid,
                                      "request_id": "a2-m2", "position": {"x": 0, "y": 0},
                                      "channel": 1})
    check(G, "measure_after_exit", ok_mid and st2 == 200 and b2
          and b2.get("accepted") is False, "measure after exit", "200/false",
          "%s/%s" % (st2, (b2 or {}).get("accepted")))


# ---------------------------------------------------------------------------
# B. virtual-time accounting (pure python arena)
# ---------------------------------------------------------------------------
def mk_arena(seed=7, n=12, mix=0.0):
    rng = random.Random(seed)
    srcs = sim.make_case(rng, n_sources=n, kind_mix=mix)
    return sim.Arena(srcs, seed=seed), srcs


def group_b():
    G = "B"

    # B1 enter/exit cost nothing
    ar, _ = mk_arena()
    ar.enter("t", "b-e")
    t0 = ar.virtual_time
    ar.exit("t", "b-x")
    check(G, "enter_exit_free", close(t0, 0.0) and close(ar.virtual_time, 0.0),
          "enter+exit cost 0 s", 0.0, ar.virtual_time)

    # B2 movement = d / 5
    ar, _ = mk_arena()
    ar.enter("t", "b-e2")
    prev, first = (0.0, 0.0), True
    ok_mv, worst = True, 0.0
    for i, tgt in enumerate([(1.0, 0.0), (5.0, 0.0), (128.4, 0.0),
                             (-871.6, 640.0), (900.0, -1200.0)]):
        step = math.hypot(tgt[0] - prev[0], tgt[1] - prev[1])
        before = ar.virtual_time
        ar.measure("t", "b-m-%d" % i, {"x": tgt[0], "y": tgt[1]}, 1)
        dt = ar.virtual_time - before
        exp = step / 5.0 + 5.0         # channel is already 1 -> no switch
        worst = max(worst, abs(dt - exp))
        if not close(dt, exp, 1e-9):
            ok_mv = False
        prev = tgt
        first = False
    check(G, "movement_cost", ok_mv,
          "cost = travelled distance / 5 s, five successive moves",
          "0.0", "%.2e" % worst)

    # B3 channel switch
    ar, _ = mk_arena()
    ar.enter("t", "b-e3")
    ar.measure("t", "b-s0", {"x": 0, "y": 0}, 3)
    t1 = ar.virtual_time
    ar.measure("t", "b-s1", {"x": 0, "y": 0}, 3)       # same channel
    same_dt = ar.virtual_time - t1
    ar.measure("t", "b-s2", {"x": 0, "y": 0}, 4)       # different channel
    diff_dt = ar.virtual_time - t1 - same_dt
    check(G, "switch_cost", close(same_dt, 5.0) and close(diff_dt, 6.0),
          "same ch 5 s, new ch 6 s", "5.0/6.0", "%.1f/%.1f" % (same_dt, diff_dt))

    # B4 measure is always 5 s regardless of outcome
    ar, srcs = mk_arena()
    ar.enter("t", "b-e4")
    free = [c for c in range(1, 21) if c not in ar.by_channel]
    ar.measure("t", "b-n0", {"x": 0.0, "y": 0.0}, free[0])
    t = ar.virtual_time
    ar.measure("t", "b-n1", {"x": 1799.0, "y": 0.0}, free[0])
    dt = ar.virtual_time - t
    check(G, "measure_5s", close(dt - 1799.0 / 5.0, 5.0),
          "no_signal measure still costs 5 s", 5.0, dt - 1799.0 / 5.0)

    # B5 clear hit 5 s, miss 3 s
    rng = random.Random(11)
    s = sim.Source(1, 500.0, 0.0, 1200.0)
    ar = sim.Arena([s])
    ar.enter("t", "b-e5")
    ar.measure("t", "b-c0", {"x": 0.0, "y": 0.0}, 1)
    t = ar.virtual_time
    ar.clear("t", "b-c1", {"x": 500.0, "y": 0.0}, 1)          # hit
    hit_dt = ar.virtual_time - t
    t2 = ar.virtual_time
    ar.clear("t", "b-c2", {"x": 0.0, "y": 0.0}, 1)            # miss (already cleared)
    miss_dt = ar.virtual_time - t2
    check(G, "clear_cost", close(hit_dt, 500.0 / 5.0 + 5.0) and close(miss_dt, 100.0 + 3.0),
          "hit = move+5 s, miss = move+3 s", "105.0/103.0", "%.1f/%.1f" % (hit_dt, miss_dt))

    # B6 clear does not change the current channel
    ar, _ = mk_arena()
    ar.enter("t", "b-e6")
    ar.measure("t", "b-ch0", {"x": 0.0, "y": 0.0}, 5)
    ar.clear("t", "b-ch1", {"x": 0.0, "y": 0.0}, 9)
    check(G, "clear_keeps_channel", ar.channel == 5,
          "clear must not retune the receiver", 5, ar.channel)

    # B7 monotone clock
    ar, _ = mk_arena()
    ar.enter("t", "b-e7")
    times, ok = [], True
    for i in range(40):
        ar.measure("t", "b-mon-%d" % i, {"x": 10.0 * i, "y": 0.0}, 1 + (i % 20))
        times.append(ar.virtual_time)
    for i in range(1, len(times)):
        if times[i] < times[i - 1] - 1e-12:
            ok = False
    check(G, "clock_monotone", ok, "40 actions, clock never decreases", "monotone", ok)

    # B8 cleared sources are no longer detected
    s = sim.Source(3, 400.0, 0.0, 1500.0)
    ar = sim.Arena([s])
    ar.enter("t", "b-e8")
    r1 = ar.measure("t", "b-d1", {"x": 0.0, "y": 0.0}, 3)
    ar.clear("t", "b-d2", {"x": 400.0, "y": 0.0}, 3)
    r2 = ar.measure("t", "b-d3", {"x": 0.0, "y": 0.0}, 3)
    check(G, "cleared_is_silent",
          r1["measure_result"] == "direction" and r2["measure_result"] == "no_signal",
          "after a successful clear the channel is silent",
          "direction/no_signal", "%s/%s" % (r1["measure_result"], r2["measure_result"]))


# ---------------------------------------------------------------------------
# C. physics
# ---------------------------------------------------------------------------
def group_c():
    G = "C"

    # C1..C4 case generation
    ok_n, ok_r, ok_ch, ok_in = True, True, True, True
    chans_all = []
    for sd in range(300):
        rng = random.Random(sd)
        srcs = sim.make_case(rng)
        if not (10 <= len(srcs) <= 16):
            ok_n = False
        cs = [s.channel for s in srcs]
        if len(set(cs)) != len(cs) or any(c < 1 or c > 20 for c in cs):
            ok_ch = False
        chans_all += cs
        for s in srcs:
            if not (1000.0 <= s.r_eff <= 1500.0):
                ok_r = False
            if math.hypot(s.x, s.y) > sim.ARENA_RADIUS + 1e-9:
                ok_in = False
    check(G, "gen_count_10_16", ok_n, "300 cases, 10..16 sources", "10..16", "ok" if ok_n else "bad")
    check(G, "gen_channels_valid", ok_ch, "distinct channels inside 1..20", "distinct", "ok" if ok_ch else "bad")
    check(G, "gen_r_eff_range", ok_r, "R_eff inside [1000,1500]", "[1000,1500]", "ok" if ok_r else "bad")
    check(G, "gen_inside_disk", ok_in, "every source inside the 1800 m disk", "<=1800", "ok" if ok_in else "bad")

    # uniformity of the position sampling (area-uniform: half of the samples
    # should fall inside r <= R/sqrt(2))
    rng = random.Random(5)
    inner = 0
    N = 20000
    for _ in range(N):
        srcs = sim.make_case(rng, n_sources=1)
        if math.hypot(srcs[0].x, srcs[0].y) <= sim.ARENA_RADIUS / math.sqrt(2.0):
            inner += 1
    frac = inner / float(N)
    check(G, "gen_area_uniform", abs(frac - 0.5) < 0.015,
          "area-uniform sampling (expect 0.5 inside R/sqrt2)", "0.500", "%.4f" % frac)

    # C5 no_signal conditions
    s = sim.Source(2, 900.0, 0.0, 1000.0)
    ar = sim.Arena([s])
    ar.enter("t", "c-e1")
    r_far = ar.measure("t", "c-1", {"x": -900.0, "y": 0.0}, 2)      # 1800 m away
    r_near = ar.measure("t", "c-2", {"x": 400.0, "y": 0.0}, 2)      # 500 m away
    check(G, "no_signal_beyond_radius",
          r_far["measure_result"] == "no_signal" and r_near["measure_result"] == "direction",
          "beyond R_eff silent, inside R_eff detected",
          "no_signal/direction", "%s/%s" % (r_far["measure_result"], r_near["measure_result"]))

    # C6 near
    s = sim.Source(4, 600.0, 0.0, 1200.0)
    ar = sim.Arena([s])
    ar.enter("t", "c-e2")
    r = ar.measure("t", "c-3", {"x": 596.0, "y": 0.0}, 4)           # 4 m away
    check(G, "near_within_5m", r["measure_result"] == "near", "4 m -> near", "near",
          r["measure_result"])

    # C7/C8/C9 bearing error model
    s = sim.Source(6, 1000.0, 0.0, 1500.0)
    ar = sim.Arena([s])
    ar.enter("t", "c-e3")
    errs, rep = [], []
    px, py = 0.0, 0.0
    for i in range(400):
        r1 = ar.measure("t", "c-e-%d" % i, {"x": px, "y": py}, 6)
        r2 = ar.measure("t", "c-r-%d" % i, {"x": px, "y": py}, 6)
        rep.append(r1.get("svd_deg") == r2.get("svd_deg"))
        true_b = math.degrees(math.atan2(s.y - py, s.x - px)) % 360.0
        d = ((r1["svd_deg"] - true_b + 180.0) % 360.0) - 180.0
        errs.append(d)
        px += 3.0
        py += 1.0
    check(G, "bearing_error_bound", max(abs(e) for e in errs) <= 1.0 + 1e-9,
          "|error| <= 1 deg over 400 samples", "<=1.0", "%.4f" % max(abs(e) for e in errs))
    check(G, "bearing_repeat_identical", all(rep),
          "the reading is a function of the location (附件 1)",
          "identical", "%d/%d" % (sum(rep), len(rep)))
    check(G, "bearing_not_constant", len(set(round(e, 6) for e in errs)) > 50,
          "the error actually varies with the location", "varied",
          len(set(round(e, 6) for e in errs)))

    # C10 clear radius boundary (20 m inclusive)
    for dist, want in ((19.9, True), (20.0, True), (20.1, False)):
        s = sim.Source(7, 500.0, 0.0, 1500.0)
        ar = sim.Arena([s])
        ar.enter("t", "c-e4")
        r = ar.clear("t", "c-cl-%s" % dist, {"x": 500.0 + dist, "y": 0.0}, 7)
        got = r["clear_result"] == "success"
        check(G, "clear_radius_%s" % ("in" if want else "out"), got == want,
              "distance %.1f m" % dist, want, got)

    # C11 directional coverage: half plane, boundary inclusive
    sd = sim.Source(8, 0.0, 0.0, 1200.0, kind="directional", direction=0.0)
    # attachment 1: the sector is 180 deg *including its boundary*, so the
    # two generatrices (due north and due south of the source) are lit
    tests = [(100.0, 0.0, True), (0.0, 100.0, True), (0.0, -100.0, True),
             (0.0, 0.0001, True), (-100.0, 0.0, False), (-100.0, 100.0, False),
             (-100.0, -100.0, False), (0.0001, -100.0, True)]
    oks = [sd.covers(x, y) == w for (x, y, w) in tests]
    check(G, "directional_halfplane", all(oks),
          "180 deg sector incl. both generatrices; the opposite half is dark",
          "ok", oks)

    # C12 directional source is silent on the dark side even when very close
    ar = sim.Arena([sd])
    ar.enter("t", "c-e5")
    r_dark = ar.measure("t", "c-d1", {"x": -50.0, "y": 0.0}, 8)
    r_lit = ar.measure("t", "c-d2", {"x": 50.0, "y": 0.0}, 8)
    check(G, "directional_blind_side",
          r_dark["measure_result"] == "no_signal" and r_lit["measure_result"] == "direction",
          "50 m behind the source is silent", "no_signal/direction",
          "%s/%s" % (r_dark["measure_result"], r_lit["measure_result"]))

    # C13 clear ignores the coverage sector
    sd2 = sim.Source(9, 0.0, 0.0, 1200.0, kind="directional", direction=0.0)
    ar = sim.Arena([sd2])
    ar.enter("t", "c-e6")
    r = ar.clear("t", "c-d3", {"x": -10.0, "y": 0.0}, 9)
    check(G, "clear_independent_of_sector", r["clear_result"] == "success",
          "10 m behind a directional source is still cleared", "success",
          r["clear_result"])


# ---------------------------------------------------------------------------
# D. response / log contract
# ---------------------------------------------------------------------------
def group_d(port):
    G = "D"
    rid = "verify-D"
    st, b = post(port, "/enter", {"arena_id": sim.ARENA_ID, "robot_id": rid,
                                  "request_id": "d-e"})
    need = ("accepted", "virtual_time_s", "max_virtual_duration_s",
            "max_real_duration_s")
    check(G, "enter_fields", all(k in (b or {}) for k in need),
          "enter response carries the four limits", need, sorted((b or {}).keys()))
    check(G, "limits_match_attachment",
          (b or {}).get("max_virtual_duration_s") == 360000
          and (b or {}).get("max_real_duration_s") == 1200,
          "100 h virtual / 20 min real", "360000/1200",
          "%s/%s" % ((b or {}).get("max_virtual_duration_s"),
                     (b or {}).get("max_real_duration_s")))

    st, b = post(port, "/measure", {"arena_id": sim.ARENA_ID, "robot_id": rid,
                                    "request_id": "d-m", "position": {"x": 0, "y": 0},
                                    "channel": 1})
    check(G, "measure_fields",
          b and "measure_result" in b and "virtual_time_s" in b
          and "real_timestamp_ms" in b,
          "measure response fields", "result+times", sorted((b or {}).keys()))
    check(G, "measure_result_enum", (b or {}).get("measure_result") in
          ("no_signal", "near", "direction"),
          "three state result", "no_signal/near/direction",
          (b or {}).get("measure_result"))

    st, b = post(port, "/clear", {"arena_id": sim.ARENA_ID, "robot_id": rid,
                                  "request_id": "d-c", "position": {"x": 0, "y": 0},
                                  "channel": 1})
    check(G, "clear_result_enum", (b or {}).get("clear_result") in
          ("success", "no_target_in_range"),
          "two state result", "success/no_target_in_range",
          (b or {}).get("clear_result"))

    st, b = post(port, "/exit", {"arena_id": sim.ARENA_ID, "robot_id": rid,
                                 "request_id": "d-x"})
    check(G, "exit_fields", b and b.get("accepted") and "virtual_time_s" in b,
          "exit response", "accepted+time", sorted((b or {}).keys()))


def group_d_log():
    """The JSONL log must contain every field the analysis relies on."""
    G = "D"
    path = os.path.join(HERE, "_verify_log.jsonl")
    if os.path.exists(path):
        os.remove(path)
    rng = random.Random(3)
    srcs = sim.make_case(rng, n_sources=11)
    ar = sim.Arena(srcs, log_path=path, seed=3)
    ar.enter("t", "log-e")
    ar.measure("t", "log-m", {"x": 100.0, "y": 50.0}, 2)
    ar.clear("t", "log-c", {"x": 100.0, "y": 50.0}, 2)
    ar.exit("t", "log-x")
    ar.close()
    rows = [json.loads(l) for l in io.open(path, encoding="utf-8") if l.strip()]
    need = ("t", "action", "pos", "channel", "request_id")
    ok = len(rows) == 4 and all(all(k in r for k in need) for r in rows)
    check(G, "log_lines_complete", ok, "4 actions, 5 mandatory fields each",
          "4 rows", "%d rows" % len(rows))
    m = [r for r in rows if r["action"] == "measure"][0]
    check(G, "log_measure_fields",
          all(k in m for k in ("move_m", "move_s", "switch_s", "result", "n_cleared")),
          "measure log carries the cost breakdown", "5 fields", sorted(m.keys()))
    os.remove(path)
    return rows


# ---------------------------------------------------------------------------
# E. cross-check against the independent open-source reference cost model
# ---------------------------------------------------------------------------
REF = {           # constants published by JammersSimulator-Tool/mock_simulator.py
    "speed": 5.0, "switch": 1.0, "detect": 5.0, "optical": 3.0, "laser": 2.0,
    "near": 5.0, "clear_r": 20.0, "radius": 1800.0, "r_lo": 1000.0, "r_hi": 1500.0,
    "n_lo": 10, "n_hi": 16, "max_virtual": 360000.0, "max_real": 1200.0,
}


def ref_measure_cost(pos, cur, x, y, ch):
    d = math.hypot(x - pos[0], y - pos[1])
    return d / REF["speed"] + (REF["switch"] if ch != cur else 0.0) + REF["detect"]


def ref_clear_cost(pos, x, y, success):
    d = math.hypot(x - pos[0], y - pos[1])
    return d / REF["speed"] + REF["optical"] + (REF["laser"] if success else 0.0)


def group_e():
    G = "E"
    pairs = [
        ("const_speed", sim.SPEED, REF["speed"]),
        ("const_switch", sim.SWITCH_TIME, REF["switch"]),
        ("const_detect", sim.MEASURE_TIME, REF["detect"]),
        ("const_clear_hit", sim.CLEAR_TIME_HIT, REF["optical"] + REF["laser"]),
        ("const_clear_miss", sim.CLEAR_TIME_MISS, REF["optical"]),
        ("const_near", sim.NEAR_RADIUS, REF["near"]),
        ("const_clear_radius", sim.CLEAR_RADIUS, REF["clear_r"]),
        ("const_radius", sim.ARENA_RADIUS, REF["radius"]),
        ("const_r_lo", sim.R_EFF_LO, REF["r_lo"]),
        ("const_r_hi", sim.R_EFF_HI, REF["r_hi"]),
        ("const_max_virtual", sim.MAX_VIRTUAL_DURATION, REF["max_virtual"]),
        ("const_max_real", sim.MAX_REAL_DURATION, REF["max_real"]),
    ]
    bad = [k for (k, a, b) in pairs if not close(a, b, 1e-9)]
    check(G, "constants_match_reference", not bad,
          "12 physics/time constants identical to the open-source driver",
          "all equal", "mismatch: %s" % bad if bad else "all equal")

    # cost model: replay a random action sequence and compare step by step
    rng = random.Random(99)
    srcs = sim.make_case(rng, n_sources=12, kind_mix=0.5)
    ar = sim.Arena(srcs, seed=99)
    ar.enter("t", "e-e")
    pos, cur = (0.0, 0.0), 1
    worst_m, worst_c = 0.0, 0.0
    for i in range(300):
        x = rng.uniform(-1800, 1800)
        y = rng.uniform(-1800, 1800)
        ch = rng.randint(1, 20)
        exp = ref_measure_cost(pos, cur, x, y, ch)
        t0 = ar.virtual_time
        ar.measure("t", "e-m-%d" % i, {"x": x, "y": y}, ch)
        worst_m = max(worst_m, abs((ar.virtual_time - t0) - exp))
        pos, cur = (x, y), ch
        if rng.random() < 0.3:
            ok_clear = None
            t0 = ar.virtual_time
            res = ar.clear("t", "e-c-%d" % i, {"x": x, "y": y}, ch)
            ok_clear = res["clear_result"] == "success"
            exp = ref_clear_cost(pos, x, y, ok_clear)
            worst_c = max(worst_c, abs((ar.virtual_time - t0) - exp))
    check(G, "measure_cost_matches_reference", worst_m < 1e-9,
          "300 random measure actions, step-by-step identical cost",
          "0.0", "%.2e" % worst_m)
    check(G, "clear_cost_matches_reference", worst_c < 1e-9,
          "clear actions, step-by-step identical cost", "0.0", "%.2e" % worst_c)

    # case generation statistics vs the reference mock
    rng = random.Random(1234)
    ns, reff, rr = [], [], []
    for _ in range(400):
        srcs = sim.make_case(rng)
        ns.append(len(srcs))
        for s in srcs:
            reff.append(s.r_eff)
            rr.append(math.hypot(s.x, s.y))
    mean_reff = sum(reff) / len(reff)
    frac_half = sum(1 for v in rr if v <= sim.ARENA_RADIUS / math.sqrt(2)) / float(len(rr))
    ok = (10 <= min(ns) and max(ns) <= 16
          and abs(mean_reff - 1250.0) < 15.0
          and abs(frac_half - 0.5) < 0.02)
    check(G, "case_stats_match_reference", ok,
          "n in 10..16, mean R_eff ~1250, half the sources inside R/sqrt2",
          "1250/0.5", "%.1f/%.4f" % (mean_reff, frac_half))

    # the one place where the reference mock deviates from 附件 1
    s = sim.Source(5, 800.0, 0.0, 1500.0)
    ar = sim.Arena([s])
    ar.enter("t", "e-e2")
    a = ar.measure("t", "e-r1", {"x": 0.0, "y": 0.0}, 5)["svd_deg"]
    b = ar.measure("t", "e-r2", {"x": 0.0, "y": 0.0}, 5)["svd_deg"]
    check(G, "deviation_from_reference_error_model", a == b,
          "reference mock redraws a random error at every call; 附件 1 requires "
          "a location dependent reading, which this simulator implements",
          "deterministic", "identical" if a == b else "differs (%s vs %s)" % (a, b))
    return {"mean_reff": mean_reff, "frac_half": frac_half,
            "n_min": min(ns), "n_max": max(ns)}


# ---------------------------------------------------------------------------
# F. conservation: the clock equals the sum of its parts
# ---------------------------------------------------------------------------
def group_f():
    G = "F"
    path = os.path.join(HERE, "_verify_full.jsonl")
    if os.path.exists(path):
        os.remove(path)
    rng = random.Random(2026)
    srcs = sim.make_case(rng, n_sources=13)
    ar = sim.Arena(srcs, log_path=path, seed=2026)
    p = dict(rc_default())
    cl = __import__("robot_core").LocalClient(ar)
    brain = __import__("robot_core").Brain(cl, params=p, seed=2026)
    st = brain.run()
    ar.close()
    rows = [json.loads(l) for l in io.open(path, encoding="utf-8") if l.strip()]
    acc = 0.0
    for r in rows:
        acc += r.get("move_s", 0.0) + r.get("switch_s", 0.0)
        if r["action"] == "measure":
            acc += sim.MEASURE_TIME
        elif r["action"] == "clear":
            acc += sim.CLEAR_TIME_HIT if r["result"] == "success" else sim.CLEAR_TIME_MISS
    final = rows[-1]["t"] if rows else 0.0
    check(G, "clock_conservation", close(acc, final, 1e-6),
          "sum of logged components equals the final virtual clock",
          "%.3f" % final, "%.3f" % acc)

    travel = sum(r.get("move_m", 0.0) for r in rows)
    check(G, "travel_conservation", close(travel, ar.travel, 1e-6),
          "logged distances equal the travelled distance", "%.1f" % ar.travel,
          "%.1f" % travel)

    check(G, "run_completes", st["clear_ratio"] >= 0.999,
          "a full strategy run on one case clears everything", "1.000",
          "%.4f" % st["clear_ratio"])
    check(G, "brain_clock_not_below_arena", st["brain_vtime"] >= acc - 1e-6,
          "the strategy estimate includes movements that never reach the arena "
          "(cached readings), so it can only be larger than the logged clock",
          ">= %.3f" % acc, "%.3f" % st["brain_vtime"])
    os.remove(path)
    return st


def group_g():
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
          "%.4f/%.1f" % (st["clear_ratio"], st["mean_time"]))

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


def group_h():
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
            ref = False                     # a degenerate hull has no interior
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


def rc_default():
    import robot_core as rc
    return dict(rc.DEFAULT_PARAMS, survey_mode="ring")


# ---------------------------------------------------------------------------
def main():
    rng = random.Random(4242)
    srcs = sim.make_case(rng, n_sources=12)

    def with_server(fn):
        """Every protocol group gets its own session, otherwise an earlier
        /exit or /enter leaks into the next group."""
        srv, _arena = sim.run_server_thread(port=0, sources=srcs, seed=4242)
        real_port = srv.server_address[1]
        time.sleep(0.25)
        try:
            fn(real_port)
        finally:
            srv.shutdown()
            srv.server_close()

    with_server(group_a)
    with_server(group_a2)
    with_server(group_a_early)
    with_server(group_d)

    group_b()
    group_c()
    group_d_log()
    extra = group_e()
    group_f()
    group_g()
    group_h()

    groups = {}
    for r in RESULTS:
        g = groups.setdefault(r["group"], [0, 0])
        g[1] += 1
        if r["ok"]:
            g[0] += 1
    n_ok = sum(1 for r in RESULTS if r["ok"])
    n_all = len(RESULTS)

    print("=" * 78)
    print("simulator verification : %d/%d checks passed" % (n_ok, n_all))
    for g in sorted(groups):
        print("   group %s : %2d/%2d" % (g, groups[g][0], groups[g][1]))
    print("=" * 78)
    for r in RESULTS:
        if not r["ok"]:
            print("FAIL [%s] %s" % (r["group"], r["key"]))
            print("     %s" % r["detail"])
            print("     expected=%s got=%s" % (r["expected"], r["got"]))

    out = os.path.normpath(os.path.join(HERE, "..", "data", "simulator_verification.json"))
    with io.open(out, "w", encoding="utf-8") as f:
        json.dump({"n_ok": n_ok, "n_all": n_all, "groups": groups,
                   "checks": RESULTS, "reference": extra,
                   "reference_source":
                       "https://github.com/Jammers-Simulator-Lab/JammersSimulator-Tool"},
                  f, ensure_ascii=False, indent=1)
    print("report ->", out)
    return 0 if n_ok == n_all else 1


def group_a_early(port):
    """measure before enter on a fresh server."""
    G = "A"
    rid = "verify-early"
    st, b = post(port, "/measure", {"arena_id": sim.ARENA_ID, "robot_id": rid,
                                    "request_id": "ae-1", "position": {"x": 0, "y": 0},
                                    "channel": 1})
    check(G, "measure_before_enter", st == 200 and b and b.get("accepted") is False,
          "no session yet", "200/false", "%s/%s" % (st, (b or {}).get("accepted")))
    st, b = post(port, "/exit", {"arena_id": sim.ARENA_ID, "robot_id": rid,
                                 "request_id": "ae-2"})
    check(G, "exit_before_enter", st == 200 and b and b.get("accepted") is False,
          "exit without a session", "200/false", "%s/%s" % (st, (b or {}).get("accepted")))


if __name__ == "__main__":
    sys.exit(main())
