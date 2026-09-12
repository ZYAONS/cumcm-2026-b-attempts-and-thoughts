#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_http_tests.py -- run complete tests through the HTTP+JSON interface of the
local simulator (the same four actions /enter /measure /clear /exit that the
official simulator exposes) and export the behaviour logs, exactly like the
"formal tests" of the competition.

usage:
    python run_http_tests.py q3 3         # three formal tests, omni sources
    python run_http_tests.py q4 3         # three formal tests, mixed sources
    python run_http_tests.py drill q3 20  # 20 drill tests
"""
import json
import os
import random
import socket
import sys
import threading
import time

import robot_core as rc
import simulator as sim

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
LOGS = os.path.join(ROOT, "logs")
DATA = os.path.join(ROOT, "data")


def free_port(start=2026):
    for p in range(start, start + 60):
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", p))
            s.close()
            return p
        except OSError:
            continue
    raise RuntimeError("no free port")


def run_one(mode, seed, robot_id="202600000000", params=None, tag="test",
            log_dir=LOGS, verbose=True):
    """One complete test: simulator + HTTP robot; returns (stats, case, logpath)."""
    rng = random.Random(seed)
    mix = 0.0 if mode == "q3" else 0.5
    srcs = sim.make_case(rng, kind_mix=mix)
    os.makedirs(log_dir, exist_ok=True)
    port = free_port(2026 + (seed % 20) * 3)
    logpath = os.path.join(log_dir, "%s_seed%d.log" % (tag, seed))
    srv, arena = sim.run_server_thread(port=port, sources=srcs,
                                       log_path=logpath, robot_id=robot_id,
                                       seed=seed)
    client = rc.HTTPClient(robot_id, port=port)
    # use exactly the configuration that make_data validates: keeping a second
    # copy of the parameters here once let the formal tests run on untuned
    # values without anybody noticing
    import os as _os
    from make_data import P3, P4, P4_FAST
    fast = _os.environ.get("Q4_FAST", "") not in ("", "0")
    base = P4_FAST if (mode == "q4" and fast) else (P3 if mode == "q3" else P4)
    p = dict(rc.DEFAULT_PARAMS)
    p.update(base)
    if params:
        p.update(params)
    brain = rc.Brain(client, params=p, seed=seed)
    t0 = time.time()
    try:
        st = brain.run()
    finally:
        wall = time.time() - t0
        ast = arena.stats()                 # the arena holds the virtual-time truth
        ast.update(st)
        st = ast
        arena.close()
        srv.shutdown()
        srv.server_close()
    st["wall_s"] = wall
    st["n_requests"] = client.n_requests
    st["http_wall_s"] = client.t_wall
    st["case"] = [{"channel": s.channel, "x": s.x, "y": s.y,
                   "r_eff": s.r_eff, "kind": s.kind, "direction": s.direction}
                  for s in srcs]
    st["case_code"] = "%s-%d-%s" % (mode.upper(), seed,
                                    "".join(sorted("%02d" % s.channel for s in srcs)))
    st["log"] = logpath
    if verbose:
        print("[%s] case %s: n=%d cleared=%d ratio=%.2f mean=%.1f s "
              "vtime=%.0f travel=%.0f measures=%d clears=%d wall=%.1fs log=%s"
              % (tag, st["case_code"], st["n_sources"], st["n_cleared"],
                 st["clear_ratio"], st["mean_time"], st["virtual_time"],
                 st["travel_m"], st["n_measure"], st["n_clear"], wall,
                 os.path.basename(logpath)))
    return st, srcs, logpath


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "q3"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    tag = sys.argv[3] if len(sys.argv) > 3 else "formal"
    seeds = [int(sys.argv[4]) + k for k in range(n)] if len(sys.argv) > 4 else \
        [770001 + k for k in range(n)]
    out = []
    for sd in seeds:
        st, _, _ = run_one(mode, sd, tag=tag, log_dir=os.path.join(LOGS, tag))
        out.append(st)
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "formal_%s_%s.json" % (mode, tag)), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("mean ratio %.3f  mean time %.1f s" %
          (sum(s["clear_ratio"] for s in out) / len(out),
           sum(s["mean_time"] for s in out) / len(out)))


if __name__ == "__main__":
    main()
