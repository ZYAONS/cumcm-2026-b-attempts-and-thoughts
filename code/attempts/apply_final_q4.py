# -*- coding: utf-8 -*-
"""apply_final_q4.py -- write the final problem 4 configuration.

Evidence chain for every value:
  rim_patrol = False       drill pool 30 cases: ratio unchanged 0.9944,
                           18.8 % less time and travel  (confirm_rim.json)
  survey_spacing = 1100    with the patrol off: ratio 0.9958 -> 1.0000,
                           time 975 -> 900 s
  search_cost_bias = 0     ratio 1.0000, 900 -> 878 s
  probe_min_angle = 22     ratio 1.0000, 878 -> 872 s
  probe_spacing = 650      unchanged (450 degraded the ratio to 0.9919,
                           900 was slower than the incumbent)
  clear_bonus = 0          unchanged (200/450 were slower)
  locate_sigma = 220       from the earlier coordinate descent
"""
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))

FINAL_Q4 = {"survey_spacing": 1100.0, "search_cost_bias": 0.0,
            "probe_min_angle": 22.0, "probe_spacing": 650.0,
            "clear_bonus": 0.0, "locate_sigma": 220.0, "max_attempts": 6}

# 1) the default switch
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()
s = s.replace('    "rim_patrol": True,', '    "rim_patrol": False,', 1)
io.open(p, "w", encoding="utf-8").write(s)
print("DEFAULT_PARAMS['rim_patrol'] = False")

# 2) fold the values into the stored optimum so the other scripts pick them up
op = os.path.join(OUT, "optimize_q4.json")
if os.path.exists(op):
    with io.open(op, encoding="utf-8") as f:
        d = json.load(f)
    d["params"].update(FINAL_Q4)
    with io.open(op, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print("optimize_q4.json updated")

# 3) P4 in the three experiment scripts
base = {"survey_mode": "lattice", "survey_spacing": 1100.0, "directional": True,
        "outer_ring_gap": 0.0, "ring_radius": 1280.0, "probe_spacing": 650.0,
        "locate_sigma": 220.0, "clear_bonus": 0.0, "probe_min_angle": 22.0,
        "search_cost_bias": 0.0, "term_cap": 420.0, "endgame_radius": 90.0,
        "max_attempts": 6}
b4 = ", ".join('"%s": %s' % (k, ('"%s"' % v) if isinstance(v, str) else
                             ("True" if v is True else "False") if isinstance(v, bool)
                             else ("%.1f" % v if isinstance(v, float) else str(v)))
               for k, v in base.items())

for fname in ("make_data.py", "make_figures.py"):
    fp = os.path.join(HERE, fname)
    t = io.open(fp, encoding="utf-8").read()
    t2, n = re.subn(r"P4 = \{[^}]*\}", "P4 = {%s}" % b4, t, count=1)
    if n:
        io.open(fp, "w", encoding="utf-8").write(t2)
        print("  %s : P4 rewritten" % fname)

fp = os.path.join(HERE, "run_http_tests.py")
t = io.open(fp, encoding="utf-8").read()
t = re.sub(r'p\.update\(\{"survey_mode": "lattice", "directional": True[^}]*\}\)',
           'p.update({"survey_mode": "lattice", "directional": True, '
           '"survey_spacing": 1100.0})', t, count=1)
io.open(fp, "w", encoding="utf-8").write(t)
print("  run_http_tests.py rewritten")
print("P4 =", b4)
