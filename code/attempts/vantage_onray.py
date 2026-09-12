# -*- coding: utf-8 -*-
"""vantage_onray.py -- adaptive second-station offset.

Diagnosis of the residual failures (independent pool seeds 62016 and 62029):
both are directional sources sitting ON the rim and radiating OUTWARD
(r = 1784 m, dir = 224 deg; and r = 1692 m, dir = 93 deg).  For such a source the
lit region inside the arena is a thin cap, so the problem-2 offset (a point
+-37/+55 deg off the measured bearing, about 550 m away) lands on the DARK side
and the measurement comes back no_signal.  Case 62029 obtained exactly ONE bearing
and then burned its whole vantage budget on three such points.

Fix: as the vantage attempts fail, shrink the offset angle and finally fall back
to a point ON the bearing ray.  The ray from a hearing point to the source stays
inside the radiation sector (the ray-approach lemma), so an on-ray station is
guaranteed to hear the source; the small remaining angular diversity still
constrains the range.

This trades a little geometric quality for the guarantee that a second bearing is
actually obtained -- which is the binding constraint at the rim.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

a = """        o = self.obs[c][-1]
        r_lim = self._ray_limit(o)
        if local:
            b = min(self.p["vantage_b_local"], max(220.0, 0.6 * r_lim))
            phis = (self.p["vantage_phi_local"], -self.p["vantage_phi_local"])
        else:
            b = min(self.p["vantage_b"], max(260.0, 0.85 * r_lim))
            phis = (self.p["vantage_phi"], -self.p["vantage_phi"])"""
b = """        o = self.obs[c][-1]
        r_lim = self._ray_limit(o)
        tries = self.vantage_tries.get(c, 0)
        if local:
            b = min(self.p["vantage_b_local"], max(220.0, 0.6 * r_lim))
            phi0 = self.p["vantage_phi_local"]
        else:
            b = min(self.p["vantage_b"], max(260.0, 0.85 * r_lim))
            phi0 = self.p["vantage_phi"]
        # For a directional source on the rim the lit cap is thin, so a large
        # offset lands on the dark side.  Shrink the offset as attempts fail and
        # finally go ON the bearing ray, which the ray lemma guarantees is lit.
        if self.p.get("vantage_onray", True):
            if tries <= 0:
                phi0 = min(phi0, 45.0)
            elif tries == 1:
                phi0 = min(phi0, 20.0)
            else:
                phi0 = 0.0
                b = min(b, max(180.0, 0.55 * r_lim))
        phis = (phi0, -phi0)"""
assert a in s, "vantage anchor"
s = s.replace(a, b, 1)

a = '    "no_plain_fallback": True,  # directional runs: do not travel for a stop'
b = ('    "vantage_onray": True,      # shrink the 2nd-station offset and finally\n'
     '                                # go on the bearing ray (rim sources)\n'
     '    "no_plain_fallback": True,  # directional runs: do not travel for a stop')
assert a in s, "param anchor"
s = s.replace(a, b, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("adaptive on-ray vantage installed")
