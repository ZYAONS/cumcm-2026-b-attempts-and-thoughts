#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
corr_study.py -- is the failure at 50 % correlation real or noise?

The first sweep used one pool of 24 cases and produced
    0 %  -> 1.0000      50 % -> 0.9968 (one source missed)      80/100 % -> 1.0000
One missed source out of ~320 is weak evidence, so this study repeats the
comparison on SEVERAL independent pools and reports the per-pool breakdown, the
number of missed sources, and a paired comparison on the SAME cases.

It also reports what the correlated field actually does to the readings:
mean error, spread, and the share of readings that sit on the +-1 deg clip.

usage: python corr_study.py [cases_per_pool] [pools]
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
_rng = random.Random(20260911)
_FIELD = []
for _ in range(3):
    wl = _rng.uniform(1200.0, 3000.0)
    ang = _rng.uniform(0.0, 2 * math.pi)
    _FIELD.append((2 * math.pi * math.cos(ang) / wl,
                   2 * math.pi * math.sin(ang) / wl,
                   _rng.uniform(0.0, 2 * math.pi), 1.0))
_WSUM = sum(f[3] for f in _FIELD)
_EXACT = sim._loc_error


def corr_field(px, py):
    return sum(w * math.sin(kx * px + ky * py + ph)
               for (kx, ky, ph, w) in _FIELD) / _WSUM


def install(amp):
    def _loc_error(px, py, channel):
        key = "%.2f|%.2f|%d" % (round(px, 2), round(py, 2), channel)
        h = sim.zlib.crc32(key.encode("utf-8")) & 0xFFFFFFFF
        ind = -1.0 + 2.0 * (h / 4294967295.0)
        return max(-1.0, min(1.0, (1.0 - amp) * ind + amp * corr_field(px, py)))
    sim._loc_error = _loc_error


def err_stats(amp, n=20000):
    """What does this mixture actually look like?"""
    install(amp)
    rng = random.Random(7)
    vals = []
    for _ in range(n):
        x = rng.uniform(-1790, 1790)
        y = rng.uniform(-1790, 1790)
        if math.hypot(x, y) > 1790:
            continue
        vals.append(sim._loc_error(x, y, 3))
    m = sum(vals) / len(vals)
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / len(vals))
    clipped = sum(1 for v in vals if abs(abs(v) - 1.0) < 1e-12) / float(len(vals))
    # local correlation: how similar are two points 50 m apart?
    pairs = []
    rng2 = random.Random(11)
    for _ in range(4000):
        x = rng2.uniform(-1500, 1500)
        y = rng2.uniform(-1500, 1500)
        if math.hypot(x, y) > 1500:
            continue
        a = sim._loc_error(x, y, 3)
        b = sim._loc_error(x + 50.0, y, 3)
        pairs.append((a - b) ** 2)
    local = math.sqrt(sum(pairs) / len(pairs))
    return {"mean": m, "sd": sd, "clip_frac": clipped, "rms_diff_50m": local}


def evaluate(params, seeds, mix=0.5):
    rs, ts, missed, ntot = [], [], 0, 0
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        st, _ = rc.run_case(srcs, params=params, seed=sd)
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        missed += st["n_sources"] - st["n_cleared"]
        ntot += st["n_sources"]
    n = float(len(seeds))
    return {"n_cases": len(seeds), "ratio": sum(rs) / n, "min": min(rs),
            "time": sum(ts) / n, "missed": missed, "sources": ntot,
            "fail_cases": sum(1 for v in rs if v < 0.999)}


if __name__ == "__main__":
    per = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    npool = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    pools = [[100000 + 1000 * k + i for i in range(per)] for k in range(npool)]
    print("pools of %d cases each: %d pools" % (per, npool), flush=True)

    print("\n--- what the error mixture looks like ---")
    stats = {}
    for amp in (0.0, 0.5, 0.8, 1.0):
        s = err_stats(amp)
        stats["%.1f" % amp] = s
        print("a=%.1f  mean=%+.3f  sd=%.3f  at the +-1 deg clip: %5.1f%%  "
              "rms|e(p)-e(p+50m)|=%.3f deg"
              % (amp, s["mean"], s["sd"], 100 * s["clip_frac"], s["rms_diff_50m"]),
              flush=True)

    out = {"stats": stats, "pools": {}}
    print("\n--- strategy performance ---")
    for amp in (0.0, 0.5, 1.0):
        install(amp)
        tot_m, tot_s, agg = 0, 0, []
        for pi, seeds in enumerate(pools):
            r = evaluate(BASE, seeds)
            r["pool"] = pi
            r["amp"] = amp
            agg.append(r)
            tot_m += r["missed"]
            tot_s += r["sources"]
            print("a=%.1f pool%d  ratio=%.4f min=%.4f time=%7.1f  "
                  "missed %d/%d sources  failing cases %d/%d"
                  % (amp, pi, r["ratio"], r["min"], r["time"], r["missed"],
                     r["sources"], r["fail_cases"], r["n_cases"]), flush=True)
        wr = sum(a["ratio"] * a["n_cases"] for a in agg) / (per * npool)
        print("a=%.1f TOTAL  weighted ratio=%.4f  missed %d/%d sources"
              % (amp, wr, tot_m, tot_s), flush=True)
        out["pools"]["%.1f" % amp] = agg
    sim._loc_error = _EXACT
    with open(os.path.join(OUT, "corr_study.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("\nreport -> data/corr_study.json")
