# -*- coding: utf-8 -*-
"""sync_formal_params.py -- the formal test runner built its parameters from
DEFAULT_PARAMS plus two overrides, so it silently missed the tuned values that
live in make_data.P3/P4 (locate_sigma, probe_min_angle, search_cost_bias,
clear_bonus, max_attempts ...).  Result: the formal tests were run on a different
configuration than the one that was validated.

Point both at one place: run_http_tests imports P3/P4 from make_data.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "run_http_tests.py")
s = io.open(p, encoding="utf-8").read()

a = """    p = dict(rc.DEFAULT_PARAMS)
    if mode == "q3":
        p.update({"survey_mode": "ring", "ring_radius": 1250.0})
    else:
        p.update({"survey_mode": "lattice", "directional": True, "survey_spacing": 1100.0})"""
b = """    # use exactly the configuration that make_data validates: keeping a second
    # copy of the parameters here once let the formal tests run on untuned
    # values without anybody noticing
    from make_data import P3, P4
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P3 if mode == "q3" else P4)"""
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("run_http_tests now shares P3/P4 with make_data")
