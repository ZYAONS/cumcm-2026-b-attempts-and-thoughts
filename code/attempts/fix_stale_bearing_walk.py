# -*- coding: utf-8 -*-
"""fix_stale_bearing_walk.py -- the homing walk used a bearing measured somewhere
else.

`clear_channel` step 4 took the angle of the LAST observation and walked along it
from the CURRENT position.  A bearing is only meaningful at the point where it was
measured: in case seed 910001 / channel 18 the robot stood 439 m from the source
while the last bearing had been taken far away, so the walk direction was off by
58 degrees and every step moved it AWAY from the target.  The trace shows a
textbook oscillation:

    pos=(-1639,-178) -> walk 420 m -> (-818,-43)     (away)
                     -> walk 420 m -> (-1140,-313)   (back)
                     -> walk 189 m -> (-963,-164)    (away again)

while the estimate sat at (-1287,-443), i.e. 4.2 m from the true source, and the
clear radius is 20 m.  The robot never got within 400 m of a source it had already
located to 4 m.

Fix: walk towards the ESTIMATE.  When the robot does stand on the last observation
point the two directions coincide, so nothing is lost; when it does not, this is
the only direction that is actually meaningful.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

a = """            o = self.obs[c][-1]
            step = max(6.0, min(0.7 * d, self.p["term_cap"])) * step_scale
            b = math.radians(o[2])"""
b = """            o = self.obs[c][-1]
            step = max(6.0, min(0.7 * d, self.p["term_cap"])) * step_scale
            # Walk towards the ESTIMATE, not along the raw last bearing: that
            # bearing was measured at o[:2] and is only valid there.  Reusing its
            # angle from a position hundreds of metres away sent the robot the
            # wrong way (58 deg off, every step away from the target).  When the
            # robot does stand on the observation point the two coincide.
            b = math.atan2(est[1] - self.pos[1], est[0] - self.pos[0])"""
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("homing walk now heads for the estimate")
