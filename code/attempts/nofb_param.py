# -*- coding: utf-8 -*-
"""nofb_param.py -- add the no_plain_fallback switch used by the A/B test.

In a directional run the greedy search step can also return a "plain coverage"
stop: one that merely lies within R of an uncovered candidate.  For a rim
candidate such a stop can never complete a certificate (all in-domain directions
point inward), so it produces travel with no progress.  The switch lets the A/B
test measure how much of the 89 % search cost that accounts for.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

a = """            elif gain_plain > 0:
                score = gain_plain / cost * 0.5"""
b = """            elif gain_plain > 0 and not (directional
                                         and self.p.get("no_plain_fallback")):
                score = gain_plain / cost * 0.5"""
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("no_plain_fallback switch added")
