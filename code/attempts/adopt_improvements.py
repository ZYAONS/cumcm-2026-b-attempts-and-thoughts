# -*- coding: utf-8 -*-
"""adopt_improvements.py -- turn the verified algorithmic improvements on by
default.

  no_plain_fallback : in a directional run the greedy search step no longer
                      accepts a stop that only provides "plain coverage".  For a
                      candidate near the rim every in-domain direction points
                      inward, so such a stop can never complete a certificate;
                      measured on ten problem 4 cases it removed 8.5 % of the
                      virtual time and 8.7 % of the travel with the clear ratio
                      unchanged at 1.0000.

The switch is inert for problem 3 (the condition also requires directional),
so it can safely live in DEFAULT_PARAMS.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()
a = '    "oropt_limit": 12,          # Or-opt only reorders this tour prefix'
b = ('    "oropt_limit": 12,          # Or-opt only reorders this tour prefix\n'
     '    "no_plain_fallback": True,  # directional runs: do not travel for a stop\n'
     '                                # that cannot complete a certificate')
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("no_plain_fallback enabled by default")
