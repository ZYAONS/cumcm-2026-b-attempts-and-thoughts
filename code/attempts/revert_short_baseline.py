# -*- coding: utf-8 -*-
"""revert_short_baseline.py -- the short-lateral-baseline stage measured as a
NEGATIVE optimisation and is reverted.

Evidence (three pools of 24 cases, 914 sources, identical seeds):

    creep only                 missed  2/914 (0.219 %)   ratio 0.9979   ~890 s
    creep + short baseline     missed  8/914 (0.875 %)   ratio 0.9917  ~1050 s

Four times the loss and 18 % more time, plus pathological behaviour on the
affected channels (5974 no-signal readings for one channel).  The reason is that
the relaxed budget condition let a channel with two bearings keep asking for
more vantages, which consumed survey budget and disturbed the covering stops
without actually tightening sigma.

The creep itself is kept: it is what obtains the second bearing at all.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

a = """            elif len(self.obs.get(c, [])) >= 2:
                # Two bearings exist but they were taken along the same ray, so
                # they are nearly parallel and sigma is huge.  The source is known
                # to be close (the creep had to halve its hop), so a SHORT lateral
                # offset is both safe and geometrically decisive.
                phi0 = 70.0
                b = float(self.p.get("vantage_short_step", 35.0))
                onray = False
            else:"""
b = """            else:"""
assert a in s, "stage anchor"
s = s.replace(a, b, 1)

a = """                if (self.vantage_tries.get(c, 0) >= self.p["vantage_max_tries"]
                        and self.onray_tries.get(c, 0)
                        >= self.p.get("vantage_onray_tries", 16)
                        and len(self.obs.get(c, [])) >= 2):
                    continue"""
b = """                if (self.vantage_tries.get(c, 0) >= self.p["vantage_max_tries"]
                        and self.onray_tries.get(c, 0)
                        >= self.p.get("vantage_onray_tries", 16)):
                    continue"""
assert a in s, "budget anchor"
s = s.replace(a, b, 1)

# keep the parameter but mark it as measured-negative
s = s.replace('    "vantage_short_step": 35.0,   # short lateral baseline once 2 bearings exist',
              '    "vantage_short_step": 35.0,   # MEASURED NEGATIVE, see the report: unused')
io.open(p, "w", encoding="utf-8").write(s)
print("short-baseline stage reverted")
