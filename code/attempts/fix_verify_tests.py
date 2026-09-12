# -*- coding: utf-8 -*-
"""fix_verify_tests.py -- four defects in the verification harness itself
(the simulator was right, the tests were wrong):

  1. movement_cost used the absolute coordinate instead of the travelled
     distance (the robot moves from the previous point, not from the origin)
  2. measure_before_enter / double_enter / measure_after_exit were executed on
     a server whose session had already been opened by an earlier group
  3. the response-contract group ran on a session that an earlier group had
     already closed with /exit
  4. the directional boundary test expected the +-90 deg generatrix to be dark,
     but attachment 1 says the 180 deg sector includes its boundary
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "verify_simulator.py")
s = io.open(p, encoding="utf-8").read()

# ---- 1. movement cost ------------------------------------------------------
a = """    ar, _ = mk_arena()
    ar.enter("t", "b-e2")
    for d in (1.0, 5.0, 123.4, 1000.0):
        before = ar.virtual_time
        ar.measure("t", "b-m-%s" % d, {"x": d, "y": 0.0}, 1)
        dt = ar.virtual_time - before
        exp = d / 5.0 + 5.0            # channel is already 1 -> no switch
        if not close(dt, exp, 1e-9):
            check(G, "movement_cost", False, "d=%.1f expected %.4f got %.4f" % (d, exp, dt))
            break
    else:
        check(G, "movement_cost", True, "d/5 for four distances", "d/5+5", "ok")"""
b = """    ar, _ = mk_arena()
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
          "0.0", "%.2e" % worst)"""
assert a in s, "anchor 1"
s = s.replace(a, b, 1)

# ---- 2. drop the duplicated before-enter check from group_a2 --------------
a = """    G = "A"
    st, b = post(port, "/measure", {"arena_id": sim.ARENA_ID, "robot_id": rid,
                                    "request_id": "a2-m0", "position": {"x": 0, "y": 0},
                                    "channel": 1})
    check(G, "measure_before_enter", st == 200 and b and b.get("accepted") is False,
          "measure without enter", "200/false", "%s/%s" % (st, (b or {}).get("accepted")))

    st, _ = post(port, "/enter", """
b = """    G = "A"
    st, _ = post(port, "/enter", """
assert a in s, "anchor 2"
s = s.replace(a, b, 1)

# ---- 3. one fresh server per protocol group -------------------------------
a = """    args = sys.argv[1:]
    port = 2026
    # start a dedicated server for the protocol checks
    rng = random.Random(4242)
    srcs = sim.make_case(rng, n_sources=12)
    srv, arena = sim.run_server_thread(port=port, sources=srcs, seed=4242,
                                       log_path=os.path.join(HERE, "_verify_srv.jsonl"))
    time.sleep(0.4)
    try:
        group_a(port)
        group_a2(port)
        group_d(port)
    finally:
        srv.shutdown()
        srv.server_close()
    # a second, fresh server for the "before enter" semantics
    srv2, arena2 = sim.run_server_thread(port=port + 1, sources=srcs, seed=4242)
    time.sleep(0.4)
    try:
        group_a_early(port + 1)
    finally:
        srv2.shutdown()
        srv2.server_close()"""
b = """    rng = random.Random(4242)
    srcs = sim.make_case(rng, n_sources=12)

    def with_server(fn):
        \"\"\"Every protocol group gets its own session, otherwise an earlier
        /exit or /enter leaks into the next group.\"\"\"
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
    with_server(group_d)"""
assert a in s, "anchor 3"
s = s.replace(a, b, 1)

# ---- 4. directional boundary expectation ----------------------------------
a = """    tests = [(100.0, 0.0, True), (0.0, 100.0, False), (0.0, -100.0, False),
             (0.0, 0.0001, True), (-100.0, 0.0, False)]
    oks = [sd.covers(x, y) == w for (x, y, w) in tests]
    check(G, "directional_halfplane", all(oks),
          "east half plane lit, west dark, boundary lit", "ok", oks)"""
b = """    # attachment 1: the sector is 180 deg *including its boundary*, so the
    # two generatrices (due north and due south of the source) are lit
    tests = [(100.0, 0.0, True), (0.0, 100.0, True), (0.0, -100.0, True),
             (0.0, 0.0001, True), (-100.0, 0.0, False), (-100.0, 100.0, False),
             (-100.0, -100.0, False), (0.0001, -100.0, True)]
    oks = [sd.covers(x, y) == w for (x, y, w) in tests]
    check(G, "directional_halfplane", all(oks),
          "180 deg sector incl. both generatrices; the opposite half is dark",
          "ok", oks)"""
assert a in s, "anchor 4"
s = s.replace(a, b, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("verification harness fixed (4 test defects)")
