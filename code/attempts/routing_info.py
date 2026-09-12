# -*- coding: utf-8 -*-
"""routing_info.py -- §10.2 item 2: exploit the coupling between the clearing
order and future detection.

The current planner treats CLEAR, LOCALISE and PROBE as independent tasks ordered
by nearest neighbour + 2-opt with a fixed priority bonus.  Two couplings are not
used:

  C1  "clear on the way".  When the tour takes the robot to a search stop, any
      located-but-uncleared source within a short detour of that stop can be
      neutralised at almost no extra travel.  Today it is a separate task that
      may be visited much later (or never, if the search keeps winning).

  C2  adaptive probing.  The opportunistic probe fires every `probe_spacing`
      metres regardless of how much is still unknown.  While many channels are
      unresolved the information is worth more, so the interval can shrink; once
      nearly everything is certified it can grow.

Both are implemented behind switches so their effect can be measured (and, if
negative, reported as such).
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

# ---- parameters -----------------------------------------------------------
a = '    "vantage_onray": True,      # shrink the 2nd-station offset and finally'
b = ('    "enroute_clear": True,      # C1: clear located sources passed on the way\n'
     '    "enroute_radius": 260.0,    #     detour budget (m)\n'
     '    "adaptive_probe": True,     # C2: shrink the probe interval while many\n'
     '    "probe_spacing_busy": 320.0,#     channels are still unresolved\n'
     '    "busy_channels": 5,         #     "many" = this many unresolved\n'
     '    "vantage_onray": True,      # shrink the 2nd-station offset and finally')
assert a in s, "param anchor"
s = s.replace(a, b, 1)

# ---- C1: clear on the way -------------------------------------------------
a = """    def probe(self, pos, force=False):
        \"\"\"Measure the unresolved channels at the current position.\"\"\"
        if not force and self.last_probe_pos is not None:
            if self._dist(pos, self.last_probe_pos) < self.p["probe_spacing"]:
                return 0"""
b = """    def _enroute_clears(self, pos):
        \"\"\"
        C1: located sources close to `pos`.  Visiting a search stop already pays
        for the travel, so neutralising a known source inside a small radius
        costs almost nothing; doing it later means paying for the trip twice.
        \"\"\"
        if not self.p.get("enroute_clear", True):
            return 0
        rad = float(self.p.get("enroute_radius", 260.0))
        done = 0
        for c in list(self.channels):
            if self.status.get(c) in ("cleared", "empty"):
                continue
            e = self.est.get(c)
            if e is None or e[2] > self.p["locate_sigma"] * 3.0:
                continue
            if self._dist(pos, (e[0], e[1])) > rad:
                continue
            if self.total_attempts.get(c, 0) >= self.p["hard_attempt_cap"]:
                continue
            self._cur_task = "clear"
            self._task_count["clear"] += 1
            self.attempts[c] = self.attempts.get(c, 0) + 1
            self.total_attempts[c] = self.total_attempts.get(c, 0) + 1
            self.last_attempt_sigma[c] = e[2]
            self.last_attempt_obs[c] = len(self.obs.get(c, []))
            if self.clear_channel(c):
                done += 1
            else:
                self.est[c] = None
        return done

    def probe(self, pos, force=False):
        \"\"\"Measure the unresolved channels at the current position.\"\"\"
        spacing = self.p["probe_spacing"]
        if self.p.get("adaptive_probe", True):
            busy = sum(1 for c in self.channels
                       if self.status.get(c) not in ("cleared", "empty"))
            if busy >= self.p.get("busy_channels", 5):
                spacing = min(spacing, self.p.get("probe_spacing_busy", 320.0))
        if not force and self.last_probe_pos is not None:
            if self._dist(pos, self.last_probe_pos) < spacing:
                return 0"""
assert a in s, "probe anchor"
s = s.replace(a, b, 1)

# ---- hook C1 into the search-stop handling --------------------------------
a = """            kind = task[0]
            if kind == "clear":"""
b = """            kind = task[0]
            if kind == "stop":
                # C1: the trip is already paid for, so take any located source
                # that sits next to this stop
                self._enroute_clears(task[2])
            if kind == "clear":"""
assert a in s, "hook anchor"
s = s.replace(a, b, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("routing couplings C1 (clear on the way) and C2 (adaptive probe) installed")
