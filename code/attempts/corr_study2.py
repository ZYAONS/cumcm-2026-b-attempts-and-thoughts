#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
corr_study2.py -- fair comparison of independent vs correlated bearing error,
and identification of the residual failures.

Two problems with the first design are fixed here:

  1. The comparison was not apples to apples.  The independent error is uniform
     on [-1,1] (sd = 0.577) while the sum-of-three-sinusoids field has sd = 0.419,
     i.e. the "100 % correlated" case was an EASIER problem, not a different one.
     The field is now rescaled to the same sd before mixing.

  2. The residual failures were not identified.  Even with completely independent
     errors the strategy misses about 2 sources in 900, so those cases are
     collected with their geometry, which is what a further improvement has to
     target.

usage: python corr_study2.py [cases_per_pool] [pools]
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
SD_UNIFORM = 2.0 / math.sqrt(12.0)          # sd of U(-1,1)


def corr_field(px, py):
    return sum(w * math.sin(kx * px + ky * py + ph)
               for (kx, ky, ph, w) in _FIELD) / _WSUM


def field_sd(n=40000):
    rng = random.Random(3)
    v = []
    for _ in range(n):
        x = rng.uniform(-1790, 1790)
        y = rng.uniform(-1790, 1790)
        if math.hypot(x, y) <= 1790:
            v.append(corr_field(x, y))
    m = sum(v) / len(v)
    return math.sqrt(sum((a - m) ** 2 for a in v) / len(v))


GAIN = SD_UNIFORM / field_sd()               # rescale the field to the same sd


def install(amp):
    def _loc_error(px, py, channel):
        key = "%.2f|%.2f|%d" % (round(px, 2), round(py, 2), channel)
        h = sim.zlib.crc32(key.encode("utf-8")) & 0xFFFFFFFF
        ind = -1.0 + 2.0 * (h / 4294967295.0)
        e = (1.0 - amp) * ind + amp * GAIN * corr_field(px, py)
        return max(-1.0, min(1.0, e))
    sim._loc_error = _loc_error


def stats(amp, n=30000):
    install(amp)
    rng = random.Random(7)
    v, dif = [], []
    for _ in range(n):
        x = rng.uniform(-1790, 1790)
        y = rng.uniform(-1790, 1790)
        if math.hypot(x, y) > 1790:
            continue
        v.append(sim._loc_error(x, y, 3))
    rng = random.Random(11)
    for _ in range(4000):
        x = rng.uniform(-1500, 1500)
        y = rng.uniform(-1500, 1500)
        if math.hypot(x, y) > 1500:
            continue
        dif.append((sim._loc_error(x, y, 3) - sim._loc_error(x + 50.0, y, 3)) ** 2)
    m = sum(v) / len(v)
    sd = math.sqrt(sum((a - m) ** 2 for a in v) / len(v))
    return {"mean": m, "sd": sd, "clip": sum(1 for a in v if abs(a) >= 1.0 - 1e-12)
            / float(len(v)), "rms50": math.sqrt(sum(dif) / len(dif))}


def evaluate(params, seeds, mix, collect):
    rs, ts, missed = [], [], []
    for sd in seeds:
        srcs = sim.make_case(random.Random(sd), kind_mix=mix)
        st, brain = rc.run_case(srcs, params=params, seed=sd)
        rs.append(st["clear_ratio"])
        ts.append(st["mean_time"])
        for s in srcs:
            if not s.cleared:
                missed.append({"seed": sd, "channel": s.channel,
                               "r": round(math.hypot(s.x, s.y)),
                               "kind": s.kind,
                               "dir": None if s.direction is None else round(s.direction),
                               "r_eff": round(s.r_eff),
                               "status": brain.status.get(s.channel),
                               "n_obs": len(brain.obs.get(s.channel, [])),
                               "n_nosig": len(brain.nosig.get(s.channel, []))})
    n = float(len(seeds))
    return {"ratio": sum(rs) / n, "min": min(rs), "time": sum(ts) / n,
            "missed": missed, "sources": sum(len(sim.make_case(random.Random(s),
                                                               kind_mix=mix))
                                             for s in seeds)}


if __name__ == "__main__":
    per = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    npool = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    pools = [[100000 + 1000 * k + i for i in range(per)] for k in range(npool)]
    print("field rescale factor %.3f (to match sd %.4f of U(-1,1))" % (GAIN, SD_UNIFORM),
          flush=True)
    print("\n--- error mixture, now with matched spread ---")
    st = {}
    for amp in (0.0, 0.5, 0.8, 1.0):
        s = stats(amp)
        st["%.1f" % amp] = s
        print("a=%.1f  sd=%.4f  clipped %4.1f%%  rms|e(p)-e(p+50m)|=%.3f"
              % (amp, s["sd"], 100 * s["clip"], s["rms50"]), flush=True)

    out = {"gain": GAIN, "stats": st, "runs": {}, "missed": {}}
    print("\n--- performance (identical pools, matched spread) ---")
    for amp in (0.0, 0.5, 1.0):
        install(amp)
        rows, allmissed = [], []
        for pi, seeds in enumerate(pools):
            r = evaluate(BASE, seeds, 0.5, True)
            allmissed += r["missed"]
            rows.append(r)
            print("a=%.1f pool%d  ratio=%.4f min=%.4f time=%7.1f  missed %d"
                  % (amp, pi, r["ratio"], r["min"], r["time"], len(r["missed"])),
                  flush=True)
        wr = sum(r["ratio"] for r in rows) / len(rows)
        tot = sum(len(sim.make_case(random.Random(sd), kind_mix=0.5))
                  for sd in [x for p in pools for x in p])
        print("a=%.1f TOTAL ratio=%.4f  missed %d/%d sources (%.3f%%)"
              % (amp, wr, len(allmissed), tot, 100.0 * len(allmissed) / tot),
              flush=True)
        out["runs"]["%.1f" % amp] = rows
        out["missed"]["%.1f" % amp] = allmissed
    sim._loc_error = _EXACT
    with open(os.path.join(OUT, "corr_study2.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print("\n--- the residual failures at a = 0 (the current implementation) ---")
    for m in out["missed"]["0.0"]:
        print("  seed %d ch %2d  r=%4d m  %-12s dir=%-4s R_eff=%4d  "
              "status=%-8s obs=%d nosig=%d"
              % (m["seed"], m["channel"], m["r"], m["kind"], m["dir"],
                 m["r_eff"], m["status"], m["n_obs"], m["n_nosig"]))
    print("\nreport -> data/corr_study2.json")
