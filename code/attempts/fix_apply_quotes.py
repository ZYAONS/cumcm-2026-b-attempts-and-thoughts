# -*- coding: utf-8 -*-
"""fix_apply_quotes.py -- apply_tuned.py wrote string values without quotes
("survey_mode": ring).  Repair the three files."""
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))
KEYS = ("ring_radius", "survey_spacing", "probe_spacing", "locate_sigma",
        "clear_bonus", "probe_min_angle", "search_cost_bias", "term_cap",
        "endgame_radius", "max_attempts", "rim_step", "max_rim_patrols")


def load(tag):
    p = os.path.join(OUT, "optimize_%s.json" % tag)
    if not os.path.exists(p):
        return {}
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)["params"]


def fmt(v):
    if isinstance(v, str):
        return '"%s"' % v
    if isinstance(v, bool):
        return "True" if v else "False"
    if isinstance(v, float):
        return "%.1f" % v
    return str(v)


def block(tag, params):
    base = {"q3": {"survey_mode": "ring"},
            "q4": {"survey_mode": "lattice", "survey_spacing": 1000.0,
                   "directional": True, "outer_ring_gap": 0.0}}[tag]
    for k in KEYS:
        if k in params:
            base[k] = params[k]
    return ", ".join('"%s": %s' % (k, fmt(v)) for k, v in base.items())


q3, q4 = load("q3"), load("q4")
b3, b4 = block("q3", q3), block("q4", q4)

for fname, tag in (("make_data.py", "P3"), ("make_data.py", "P4"),
                   ("make_figures.py", "P3"), ("make_figures.py", "P4")):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    new = "P3 = {%s}" % b3 if tag == "P3" else "P4 = {%s}" % b4
    s2, n = re.subn(r"%s = \{[^}]*\}" % tag, new.replace("\\", "\\\\"), s, count=1)
    if n:
        io.open(p, "w", encoding="utf-8").write(s2)
        print("  %s : %s rewritten" % (fname, tag))

# run_http_tests.py: the two update() calls
p = os.path.join(HERE, "run_http_tests.py")
s = io.open(p, encoding="utf-8").read()
s = re.sub(r'p\.update\(\{"survey_mode": "ring"[^}]*\}\)',
           'p.update({"survey_mode": "ring", "ring_radius": %s})'
           % fmt(q3.get("ring_radius", 1250.0)), s, count=1)
s = re.sub(r'p\.update\(\{"survey_mode": "lattice", "directional": True[^}]*\}\)',
           'p.update({"survey_mode": "lattice", "directional": True, '
           '"survey_spacing": %s})' % fmt(q4.get("survey_spacing", 1000.0)),
           s, count=1)
io.open(p, "w", encoding="utf-8").write(s)
print("  run_http_tests.py rewritten")
print("P3 =", b3)
print("P4 =", b4)
