# -*- coding: utf-8 -*-
"""necessity_34.py -- are §10.2 items 3 and 4 worth modelling?

item 3 (spatially correlated bearing error)
    The simulator's error is currently a pure function of (position, channel) with
    no spatial structure: two points 1 m apart get completely independent errors.
    Real direction finders have correlated error (the same building reflection
    biases a whole neighbourhood).  This script adds a smooth correlated field

        err = (1-a) * independent + a * smooth_field(position)

    with the smooth field built from three sinusoids of 1200-3000 m wavelength, and
    re-runs the drill pool for a = 0, 0.5, 0.8.  If the results barely move, item 3
    is a modelling nicety rather than a risk; if they collapse, the strategy is
    leaning on an assumption that does not hold in practice.

item 4 (coupling of real time)
    Measures the actual wall-clock cost of one request and compares it with the
    1200 s budget.

usage: python necessity_34.py [n_cases]
"""
import json
import math
import os
import random
import sys
import time

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))
TUNED = {}
p = os.path.join(OUT, "optimize_q4.json")
if os.path.exists(p):
    with open(p, encoding="utf-8") as f:
        TUNED = json.load(f)["params"]
BASE = dict(rc.DEFAULT_PARAMS, survey_mode="lattice", survey_spacing=1100.0,
            directional=True)
for k in ("survey_spacing", "probe_spacing", "locate_sigma", "clear_bonus",
          "probe_min_angle", "search_cost_bias", "max_attempts"):
    if k in TUNED:
        BASE[k] = TUNED[k]

# ---------------------------------------------------------------------------
# a smooth pseudo-random field over the arena, wavelength 1200-3000 m
# ---------------------------------------------------------------------------
_rng = random.Random(20260911)
_FIELD = []
for _ in range(3):
    wl = _rng.uniform(1200.0, 3000.0)
    ang = _rng.uniform(0.0, 2 * math.pi)
    _FIELD.append((2 * math.pi * math.cos(ang) / wl,
                   2 * math.pi * math.sin(ang) / wl,
                   _rng.uniform(0.0, 2 * math.pi),
                   1.0))
_WSUM = sum(f[3] for f in _FIELD)


def corr_field(px, py):
    v = sum(w * math.sin(kx * px + ky * py + ph) for (kx, ky, ph, w) in _FIELD)
    return v / _WSUM


def install(amp):
    """Rewrite the bearing error to include a correlated fraction."""
    def _loc_error(px, py, channel):
        key = "%.2f|%.2f|%d" % (round(px, 2), round(py, 2), channel)
        h = sim.zlib.crc32(key.encode("utf-8")) & 0xFFFFFFFF
        ind = -1.0 + 2.0 * (h / 4294967295.0)
        e = (1.0 - amp) * ind + amp * corr_field(px, py)
        return max(-1.0, min(1.0, e))
    sim._loc_error = _loc_error


def ev(params, seeds, mix=0.5):
    rs, ts, tr = [], [], []
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        st, _ = rc.run_case(srcs, params=params, seed=sd)
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        tr.append(st["travel_m"])
    n = float(len(seeds))
    return {"ratio": sum(rs) / n, "min": min(rs), "time": sum(ts) / n,
            "travel": sum(tr) / n}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    seeds = list(range(30000, 30000 + n))
    exact = sim._loc_error
    out = {}
    print("=== item 3 : spatially correlated bearing error ===", flush=True)
    print("pool: %d cases, seeds %d..%d" % (n, seeds[0], seeds[-1]), flush=True)
    for amp in (0.0, 0.5, 0.8, 1.0):
        install(amp)
        r = ev(BASE, seeds)
        r["amp"] = amp
        out["corr_%.1f" % amp] = r
        print("correlated fraction %3.0f%%  ratio=%.4f min=%.4f time=%7.1f "
              "travel=%7.0f" % (100 * amp, r["ratio"], r["min"], r["time"],
                                r["travel"]), flush=True)
    sim._loc_error = exact

    print()
    print("=== item 4 : real-time cost of one request ===", flush=True)
    import threading
    import run_http_tests as rht
    st, srcs, logp = rht.run_one("q4", 910001, tag="realtime", verbose=False)
    print("case %s: %d requests, HTTP wall time %.2f s, "
          "simulator-internal wall %.2f s"
          % (st["case_code"], st["n_requests"], st["http_wall_s"], st["wall_s"]),
          flush=True)
    print("per request: %.2f ms (HTTP)   budget 1200 s   headroom factor %.0f"
          % (1000.0 * st["http_wall_s"] / max(st["n_requests"], 1),
             1200.0 / max(st["http_wall_s"], 1e-6)), flush=True)
    out["realtime"] = {"n_requests": st["n_requests"],
                       "http_wall_s": st["http_wall_s"],
                       "wall_s": st["wall_s"],
                       "ms_per_request": 1000.0 * st["http_wall_s"]
                       / max(st["n_requests"], 1)}
    with open(os.path.join(OUT, "necessity_34.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("report -> data/necessity_34.json")
