# -*- coding: utf-8 -*-
"""fix_endgame_position.py -- the endgame clear pattern left the robot standing on
its LAST pattern point.

Why that is a defect (case seed 30017, channel 11):
  the estimate was 20.1 m from the true source (just outside the 20 m clear
  radius) and the robot stood at (38.5, 1428) -- a point on the LIT side of the
  directional source, 57 m away, from which the source is audible.  The hexagonal
  sweep walked it out to (184, 1359): 104 m from the source and on the DARK side.
  The next "hear here" therefore returned no_signal, the retreat fired, and the
  loop repeated until the attempt budget ran out.  One more bearing taken from the
  original position would have localised the source to a few metres.

Fix: try the pattern points first and the CENTRE LAST, so a failed sweep always
leaves the robot standing on the estimate -- the best place to re-measure from.
Cost: zero (the same number of clear attempts, in a different order).
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

a = """        if radius is None:
            s = 30.0 if sigma is None else sigma
            radius = min(max(0.55 * s, 12.0), 45.0)
        if self._try_clear(c):
            return True
        for k in range(6):"""
b = """        if radius is None:
            s = 30.0 if sigma is None else sigma
            radius = min(max(0.55 * s, 12.0), 45.0)
        # NB the centre is tried LAST.  A failed sweep then leaves the robot
        # standing on the estimate, which is where an extra bearing is most
        # useful; trying the centre first would leave it on the last ring point,
        # possibly on the dark side of a directional source.
        for k in range(6):"""
assert a in s, "anchor 1"
s = s.replace(a, b, 1)

# find the tail of the sweep and append the centre attempt
i = s.index("    def _local_clear_sweep(self, c, center, radius=None, sigma=None):")
j = s.index("    def _bracket_clear", i)
tail = s[i:j]
assert "return False" in tail, "no return in the sweep"

# insert the centre attempt just before the final "return False"
k = tail.rindex("return False")
tail2 = (tail[:k]
         + "# the centre last: see the note above\n"
         + "        if self._try_clear(c, center):\n"
         + "            return True\n"
         + "        " + tail[k:])
s = s[:i] + tail2 + s[j:]
io.open(p, "w", encoding="utf-8").write(s)
print("endgame sweep now tries the centre last")
