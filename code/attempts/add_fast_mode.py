# -*- coding: utf-8 -*-
"""add_fast_mode.py -- register the validated sub-500 s configuration as a named
preset, keeping the accurate configuration as the default."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- make_data
p = os.path.join(HERE, "make_data.py")
s = io.open(p, encoding="utf-8").read()
anchor = "def w(name, rows, header=None):"
assert anchor in s, "make_data anchor"
preset = '''# ---------------------------------------------------------------------------
# P4_FAST : the "finish under 500 s" preset.
#
# Validated on two independent pools of 40 cases each (seeds 62000+ and 51000+),
# neither of which took part in any tuning:
#
#     pool A   476.5 s   completion 0.9823   median 475.7
#     pool B   498.2 s   completion 0.9699   median 485.0
#
# against the accurate configuration (P4), which runs 864.9 s / 945.7 s at
# completion 1.0000 / 0.9983 on the same pools.  The preset buys a 45 % cut in
# time for 1.6 to 3.0 percentage points of completion rate; the full derivation,
# including the measurements that turned out to be negative, is in
# docs/time_optimization.pdf.
P4_FAST = dict(P4)
P4_FAST.update({
    "survey_spacing": 1000.0,     # the lattice is only used as a discovery sweep
    "max_survey_stops": 10,       # ... and is cut to ten well-spread positions
    "spread_stops": True,         # farthest-point ordering, so the cut keeps the
                                  # arena covered instead of dropping the rim
    "max_search_stops": 0,        # no certification search at all
    "verify_margin": 900.0,       # candidates near the rim are excluded: they can
                                  # never be certified from inside (theorem 2)
    "periodic_cert": True,        # certify during the sweep so certified channels
    "periodic_cert_every": 1,     # stop being measured
    "locate_sigma": 400.0,
    "clear_bonus": 500.0,
    "probe_spacing": 2000.0,
})


'''
s = s.replace(anchor, preset + anchor, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("P4_FAST added to make_data.py")

# ------------------------------------------------------------ run_http_tests
p = os.path.join(HERE, "run_http_tests.py")
s = io.open(p, encoding="utf-8").read()
a = "    from make_data import P3, P4\n    p = dict(rc.DEFAULT_PARAMS)\n    p.update(P3 if mode == \"q3\" else P4)"
b = ("    import os as _os\n"
     "    from make_data import P3, P4, P4_FAST\n"
     "    fast = _os.environ.get(\"Q4_FAST\", \"\") not in (\"\", \"0\")\n"
     "    base = P4_FAST if (mode == \"q4\" and fast) else (P3 if mode == \"q3\" else P4)\n"
     "    p = dict(rc.DEFAULT_PARAMS)\n"
     "    p.update(base)")
assert a in s, "run_http_tests anchor"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("run_http_tests.py accepts Q4_FAST=1")
