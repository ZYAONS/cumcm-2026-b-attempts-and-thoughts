#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
measure_profile.py -- 扫描过程中每站到底测了多少频道、当时的状态分布。

若扫描中每站都接近 20 次检测，说明"已听到/已清除"的频道并没有被跳过，
那将是一处大的时间浪费。本脚本把它量出来。

usage: python measure_profile.py [seed]
"""
import random
import sys

import robot_core as rc
import simulator as sim

from make_data import P4

P = dict(rc.DEFAULT_PARAMS)
P.update(P4)
P.update({"survey_spacing": 900.0, "max_search_stops": 0, "verify_margin": 900.0,
          "periodic_cert_every": 1, "spread_stops": True, "max_survey_stops": 0,
          "clear_bonus": 500.0, "locate_sigma": 400.0})

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 30000
    srcs = sim.make_case(random.Random(seed), kind_mix=0.5)
    ar = sim.Arena(srcs, seed=seed)
    br = rc.Brain(rc.LocalClient(ar), params=P, seed=seed)

    rec = []
    counter = {"n": 0}
    orig_measure = br.move_measure

    def wrapped_measure(x, y, c):
        counter["n"] += 1
        return orig_measure(x, y, c)

    br.move_measure = wrapped_measure
    orig_probe = br.probe

    def wrapped_probe(pos, force=False):
        st = {k: sum(1 for c in br.channels if br.status[c] == k)
              for k in ("unknown", "seen", "located", "cleared", "empty")}
        n0 = counter["n"]
        r = orig_probe(pos, force=force)
        rec.append((force, st, counter["n"] - n0))
        print("%5s | unk %2d seen %2d loc %2d clr %2d emp %2d | measured %2d"
              % ("F" if force else "-", st["unknown"], st["seen"], st["located"],
                 st["cleared"], st["empty"], counter["n"] - n0), flush=True)
        return r

    br.probe = wrapped_probe
    st = br.run()
    print("total measurements %d for %d sources, time %.0f s/source"
          % (counter["n"], len(srcs), st["mean_time"]))
