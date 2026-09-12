# -*- coding: utf-8 -*-
"""profile_cert.py -- where does the CPU go when the rim patrol is active?"""
import cProfile
import io
import pstats
import random
import time

import robot_core as rc
import simulator as sim

p = dict(rc.DEFAULT_PARAMS, survey_mode="lattice", survey_spacing=1000.0,
         directional=True)

calls = {"n": 0, "t": 0.0}
orig = rc.Brain.certification_scan


def wrapped(self, channels):
    t0 = time.time()
    r = orig(self, channels)
    calls["n"] += 1
    calls["t"] += time.time() - t0
    return r


rc.Brain.certification_scan = wrapped

for sd in (90000, 90001):
    srcs = sim.make_case(random.Random(sd), kind_mix=0.5)
    t0 = time.time()
    st, _ = rc.run_case(srcs, params=p, seed=sd)
    print("case %d ratio=%.3f time=%.0f  wall=%.1f s  scans=%d scan_s=%.1f"
          % (sd, st["clear_ratio"], st["mean_time"], time.time() - t0,
             calls["n"], calls["t"]), flush=True)

pr = cProfile.Profile()
pr.enable()
srcs = sim.make_case(random.Random(90002), kind_mix=0.5)
rc.run_case(srcs, params=p, seed=90002)
pr.disable()
buf = io.StringIO()
pstats.Stats(pr, stream=buf).sort_stats("cumulative").print_stats(14)
print(buf.getvalue()[:2600])
