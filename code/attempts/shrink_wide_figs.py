# -*- coding: utf-8 -*-
"""shrink_wide_figs.py -- the wide multi-panel figures were physically too large
(9.5-10.5 in), so their text became smaller than 9 pt once the figure was scaled
to 0.74-0.84 \\textwidth in the paper.  Shrinking the canvas (fonts unchanged)
raises the effective font size without costing any page space.
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

# figure -> (old figsize, new figsize)
CHANGES = [
    ("fig_q1_region",          "(9.8, 4.8)",  "(9.1, 4.5)"),
    ("fig_q1_cover_stats",     "(9.8, 4.2)",  "(9.1, 3.9)"),
    ("fig_q2_scan",            "(10.4, 4.5)", "(9.1, 3.9)"),
    ("fig_q2_montecarlo",      "(10.2, 4.3)", "(8.0, 3.4)"),
    ("fig_q2_region_rule",     "(11.2, 3.9)", "(9.1, 3.2)"),
    ("fig_q34_stats",          "(10.8, 4.5)", "(8.2, 3.4)"),
    ("fig_sensitivity",        "(10.4, 4.7)", "(9.1, 4.1)"),
    ("fig_q3_cases",           "(10.0, 4.3)", "(9.1, 3.9)"),
    ("fig_convergence",        "(10.0, 4.3)", "(8.2, 3.5)"),
    ("fig_coverage",           "(10.4, 5.0)", "(9.1, 4.4)"),
    ("fig_directional",        "(10.8, 4.3)", "(9.1, 3.6)"),
    ("fig_q3_errors",          "(10.8, 4.2)", "(9.1, 3.5)"),
]

for fn, old, new in CHANGES:
    i = s.find("def %s(" % fn)
    assert i > 0, fn
    j = s.find(old, i)
    assert j > 0 and j - i < 4000, "%s: figsize %s not found nearby" % (fn, old)
    s = s[:j] + new + s[j + len(old):]
    print("  %-22s %s -> %s" % (fn, old, new))

io.open(p, "w", encoding="utf-8").write(s)
print("canvas sizes reduced")
