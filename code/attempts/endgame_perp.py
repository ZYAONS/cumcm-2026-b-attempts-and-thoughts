# -*- coding: utf-8 -*-
"""endgame_perp.py -- collapse the endgame uncertainty with one perpendicular cut.

Diagnosis of case seed 30017 / channel 11 (see trace_case.py):
  the homing path is a straight line, so the three bearings are taken from nearly
  collinear points.  Their wedges intersect in a long thin sliver whose minimum
  enclosing circle still has radius 77 m, while the true source sits only 20.5 m
  from the centre -- 0.5 m outside the 20 m clear radius -- and, worse, on the
  DARK side of the radiation sector, so the endgame sweep and every "hear here"
  fail.

Fix: when the sweep fails and sigma is still coarse, take ONE bearing from a
position perpendicular to the current line of sight, then re-estimate.  Three
collinear cuts leave the range unconstrained; a perpendicular cut fixes it.
Cost: one measurement plus about `perp_step` metres of travel (about 20 s),
against the 1000+ s the robot otherwise spends searching for a channel it has in
fact already located.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

# ---- parameters -----------------------------------------------------------
a = '    "oropt_limit": 12,          # Or-opt only reorders this tour prefix'
b = ('    "oropt_limit": 12,          # Or-opt only reorders this tour prefix\n'
     '    "perp_step": 80.0,          # endgame perpendicular vantage offset (m)\n'
     '    "perp_sigma": 26.0,         # only when sigma is still above this\n'
     '    "perp_max": 3,              # cap on perpendicular cuts per channel')
assert a in s, "param anchor"
s = s.replace(a, b, 1)

# ---- per channel counter --------------------------------------------------
a = "        self.visited_stops = set()\n        self.rim_patrols = 0"
b = ("        self.visited_stops = set()\n        self.rim_patrols = 0\n"
     "        self.perp_tries = {}")
assert a in s, "counter anchor"
s = s.replace(a, b, 1)

# ---- the endgame cut ------------------------------------------------------
a = """            # 2) endgame: small pattern around the estimate
            if d <= self.p["endgame_radius"]:
                if self._local_clear_sweep(c, est[:2], sigma=est[2]):
                    return True
                if d <= self.p["endgame_radius"] * 0.5:
                    return False"""
b = """            # 2) endgame: small pattern around the estimate
            if d <= self.p["endgame_radius"]:
                if self._local_clear_sweep(c, est[:2], sigma=est[2]):
                    return True
                # 2b) the estimate is coarse because the bearings were taken from
                #     nearly collinear points along the homing path.  One cut
                #     perpendicular to the line of sight constrains the range and
                #     collapses sigma, which is what makes the pattern work.
                if (est[2] > self.p["perp_sigma"]
                        and self.perp_tries.get(c, 0) < self.p["perp_max"]
                        and self._perp_cut(c, est)):
                    self.perp_tries[c] = self.perp_tries.get(c, 0) + 1
                if d <= self.p["endgame_radius"] * 0.5:
                    return False"""
assert a in s, "endgame anchor"
s = s.replace(a, b, 1)

# ---- the helper -----------------------------------------------------------
a = "    def _bracket_clear(self, c, p_from, p_to):"
b = '''    def _perp_cut(self, c, est):
        """
        Take one bearing from a point perpendicular to the line of sight and
        refresh the estimate.  Returns True when a new bearing was obtained.
        """
        if not self.obs.get(c):
            return False
        o = self.obs[c][-1]
        los = math.atan2(est[1] - o[1], est[0] - o[0])
        step = float(self.p["perp_step"])
        for sgn in (1.0, -1.0):
            a = los + sgn * math.pi / 2.0
            q = self._clip_to_arena((est[0] + step * math.cos(a),
                                     est[1] + step * math.sin(a)))
            if self._dist(q, (est[0], est[1])) < step * 0.5:
                continue
            r = self.hear(c, q)
            if r.get("measure_result") == "direction":
                e2 = self.update_estimate(c)
                if e2 is not None:
                    self.est[c] = e2
                return True
        return False

    def _bracket_clear(self, c, p_from, p_to):'''
assert a in s, "helper anchor"
s = s.replace(a, b, 1)

# ---- the attempt budget reopens when a new bearing arrives ----------------
a = """            if self.attempts.get(c, 0) >= self.p["max_attempts"]:
                prev = self.last_attempt_sigma.get(c)
                if prev is not None and e[2] > self.p["progress_ratio"] * prev:
                    continue
                self.attempts[c] = 0"""
b = """            if self.attempts.get(c, 0) >= self.p["max_attempts"]:
                prev = self.last_attempt_sigma.get(c)
                prev_obs = self.last_attempt_obs.get(c, 0)
                # reopen when the localisation improved, or when new bearings
                # have arrived since the last attempt (a fresh cut can turn a
                # hopeless estimate into a solvable one)
                if (prev is not None and e[2] > self.p["progress_ratio"] * prev
                        and len(self.obs[c]) <= prev_obs):
                    continue
                self.attempts[c] = 0"""
assert a in s, "budget anchor"
s = s.replace(a, b, 1)

a = """        self.perp_tries = {}"""
b = """        self.perp_tries = {}
        self.last_attempt_obs = {}"""
assert a in s, "obs counter anchor"
s = s.replace(a, b, 1)

a = """                if self.est[task[1]] is not None:
                    self.last_attempt_sigma[task[1]] = self.est[task[1]][2]"""
b = """                if self.est[task[1]] is not None:
                    self.last_attempt_sigma[task[1]] = self.est[task[1]][2]
                self.last_attempt_obs[task[1]] = len(self.obs.get(task[1], []))"""
assert a in s, "record anchor"
s = s.replace(a, b, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("perpendicular endgame cut installed")
