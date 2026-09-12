# -*- coding: utf-8 -*-
"""rim_budget.py -- bound the virtual-time cost of the rim patrol:

  * candidates are visited nearest-first instead of in grid order
  * the total number of patrol trips is capped (max_rim_patrols), so a rim
    candidate that stays uncertified cannot make the robot shuttle to the rim
    forever
  * a patrol point is only emitted when it is within reach of the candidate
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

a = '    "rim_max_pts": 9,           # cap on outside samples per search step'
b = ('    "rim_max_pts": 9,           # cap on outside samples per search step\n'
     '    "max_rim_patrols": 12,     # total number of outside sampling trips')
assert a in s, "param anchor"
s = s.replace(a, b, 1)

a = """        step = float(self.p.get("rim_step", 130.0))
        cap = int(self.p.get("rim_max_pts", 9))
        lim = self.arena_r - 2.0 * self.p["verify_grid"]
        out, seen = [], set()
        for q in uncov:"""
b = """        step = float(self.p.get("rim_step", 130.0))
        cap = int(self.p.get("rim_max_pts", 9))
        lim = self.arena_r - 2.0 * self.p["verify_grid"]
        out, seen = [], set()
        # nearest candidates first: the trip to the rim is the expensive part
        uncov = sorted(uncov, key=lambda q: self._dist(self.pos, q))
        for q in uncov:"""
assert a in s, "sort anchor"
s = s.replace(a, b, 1)

a = """        if not self.p.get("rim_patrol", True):
            return (fallback[1] if fallback else None), flags
        # nothing inside the arena can help any more: try the outside samples
        # aimed at the rim candidates before giving up
        for p in self._rim_patrol_stops(uncov):"""
b = """        if not self.p.get("rim_patrol", True):
            return (fallback[1] if fallback else None), flags
        if self.rim_patrols >= int(self.p.get("max_rim_patrols", 12)):
            return (fallback[1] if fallback else None), flags
        # nothing inside the arena can help any more: try the outside samples
        # aimed at the rim candidates before giving up
        for p in self._rim_patrol_stops(uncov):"""
assert a in s, "budget anchor"
s = s.replace(a, b, 1)

a = """            if gain > 0:
                return p, flags
        return (fallback[1] if fallback else None), flags"""
b = """            if gain > 0:
                self.rim_patrols += 1
                return p, flags
        return (fallback[1] if fallback else None), flags"""
assert a in s, "counter anchor"
s = s.replace(a, b, 1)

# initialise the counter next to the other per-run state
a = "        self.visited_stops = set()"
b = "        self.visited_stops = set()\n        self.rim_patrols = 0"
assert a in s, "init anchor"
s = s.replace(a, b, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("rim patrol budget installed")
