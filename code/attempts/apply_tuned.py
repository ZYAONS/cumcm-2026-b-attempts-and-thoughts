#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apply_tuned.py -- write the tuned parameter values into the experiment scripts.

Reads data/optimize_q3.json and data/optimize_q4.json (written by
optimize_q34.py) and rewrites the P3 / P4 dictionaries of make_data.py,
run_http_tests.py and make_figures.py so that every generated result uses the
verified configuration.
"""
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
    if isinstance(v, bool):
        return "True" if v else "False"
    if isinstance(v, float):
        return "%.1f" % v
    return str(v)


def block(tag, params):
    base = {"q3": {"survey_mode": "ring"},
            "q4": {"survey_mode": "lattice", "survey_spacing": 1000.0,
                   "directional": True,
                   "outer_ring_gap": 0.0}}[tag]
    for k in KEYS:
        if k in params:
            base[k] = params[k]
    items = ", ".join('"%s": %s' % (k, fmt(v)) for k, v in base.items())
    return items


def patch(path, pattern, repl, count=1):
    full = os.path.join(HERE, path)
    s = io.open(full, encoding="utf-8").read()
    new, n = re.subn(pattern, repl, s, count=count, flags=re.S)
    if n == 0:
        print("  !! pattern not found in", path)
        return
    io.open(full, "w", encoding="utf-8").write(new)
    print("  patched %s (%d site)" % (path, n))


if __name__ == "__main__":
    q3 = load("q3")
    q4 = load("q4")
    print("q3 tuned:", {k: q3.get(k) for k in KEYS if k in q3})
    print("q4 tuned:", {k: q4.get(k) for k in KEYS if k in q4})
    b3 = block("q3", q3)
    b4 = block("q4", q4)

    patch("make_data.py", r"P3 = \{[^}]*\}", "P3 = {%s}" % b3)
    patch("make_data.py", r"P4 = \{[^}]*\}", "P4 = {%s}" % b4)

    # make_figures.py: the two case maps
    patch("make_figures.py",
          r'p\.update\(\{"survey_mode": "ring"\} if mode == "q3" else\n'
          r'\s*\{"survey_mode": "lattice", "survey_spacing": 1000\.0, "directional": True\}\)',
          'p.update(P3 if mode == "q3" else P4)')
    patch("make_figures.py",
          r'p\.update\(\{"survey_mode": "ring"\}\)',
          'p.update(P3)')
    if "P3 = {" not in io.open(os.path.join(HERE, "make_figures.py"),
                              encoding="utf-8").read():
        s = io.open(os.path.join(HERE, "make_figures.py"), encoding="utf-8").read()
        s = s.replace("HERE = os.path.dirname(os.path.abspath(__file__))",
                      "P3 = {%s}\nP4 = {%s}\n\nHERE = os.path.dirname(os.path.abspath(__file__))"
                      % (b3, b4), 1)
        io.open(os.path.join(HERE, "make_figures.py"), "w",
                encoding="utf-8").write(s)
        print("  inserted P3/P4 into make_figures.py")

    patch("run_http_tests.py",
          r'p\.update\(\{"survey_mode": "ring"\}\)',
          'p.update({"survey_mode": "ring", "ring_radius": %s})' % fmt(q3.get("ring_radius", 1250.0)))
    patch("run_http_tests.py",
          r'p\.update\(\{"survey_mode": "lattice", "directional": True\}\)',
          'p.update({"survey_mode": "lattice", "directional": True, '
          '"survey_spacing": %s})' % fmt(q4.get("survey_spacing", 1000.0)))
    print("done")
