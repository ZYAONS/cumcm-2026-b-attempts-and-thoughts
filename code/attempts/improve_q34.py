# -*- coding: utf-8 -*-
"""improve_q34.py -- two algorithmic improvements on top of the parameter tuning.

  I1  rim patrol (problem 4).  A candidate location q close to the arena rim can
      never be certified from inside: every in-domain reading position lies in
      the half plane facing the centre, so no set of them contains q in its
      convex hull (theorem 2).  Instead of a full outside ring (very expensive)
      the planner now, and only when nothing inside can help, walks a few metres
      radially outward from the uncertified rim candidates.

  I2  Or-opt in the tour planner: relocate segments of 1..3 tasks on top of the
      nearest-neighbour + 2-opt construction.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

# ------------------------------------------------------------------ I1 -----
a = """    "outer_ring_gap": 0.0,      # distance of the outside ring beyond the rim"""
b = """    "rim_patrol": True,         # visit points just outside the rim when a
                                # candidate location cannot be certified inside
    "rim_step": 130.0,          # radial offset (m) of those outside samples
    "rim_max_pts": 9,           # cap on outside samples per search step
    "outer_ring_gap": 0.0,      # distance of the outside ring beyond the rim"""
assert a in s, "I1 param anchor"
s = s.replace(a, b, 1)

a = """    def _plan_tour(self, tasks, start):"""
b = """    def _rim_patrol_stops(self, uncov):
        \"\"\"
        Candidate positions just OUTSIDE the arena rim, aimed at the candidate
        locations that could not be certified from inside.

        For a candidate q close to the rim, every in-domain reading position p
        satisfies (p - q) pointing inward, so the origin can never lie inside
        the convex hull of the (p - q): no in-domain search can ever certify q
        (theorem 2).  Stepping a little outside, radially from the centre
        through q and slightly to both sides, produces directions that bracket
        q and makes the certificate reachable.
        \"\"\"
        step = float(self.p.get("rim_step", 130.0))
        cap = int(self.p.get("rim_max_pts", 9))
        lim = self.arena_radius - 2.0 * self.p["verify_grid"]
        out, seen = [], set()
        for q in uncov:
            r = math.hypot(q[0], q[1])
            if r < lim:
                continue
            ux, uy = (q[0] / r, q[1] / r) if r > 1e-9 else (1.0, 0.0)
            for deg in (-38.0, 0.0, 38.0):
                a = math.radians(deg)
                dx = ux * math.cos(a) - uy * math.sin(a)
                dy = ux * math.sin(a) + uy * math.cos(a)
                k = step / max(0.35, math.cos(a))
                key = (round(q[0] + k * dx, 1), round(q[1] + k * dy, 1))
                if key in seen or key in self.visited_stops:
                    continue
                seen.add(key)
                out.append((q[0] + k * dx, q[1] + k * dy))
                if len(out) >= cap:
                    return out
        return out

    def _plan_tour(self, tasks, start):"""
assert a in s, "I1 method anchor"
s = s.replace(a, b, 1)

# hook the patrol into the greedy search step
a = """        if best is not None:
            return best[1], flags
        return (fallback[1] if fallback else None), flags"""
b = """        if best is not None:
            return best[1], flags
        if not self.p.get("rim_patrol", True):
            return (fallback[1] if fallback else None), flags
        # nothing inside the arena can help any more: try the outside samples
        # aimed at the rim candidates before giving up
        for p in self._rim_patrol_stops(uncov):
            gain = 0
            for q in uncov:
                dx, dy = p[0] - q[0], p[1] - q[1]
                if dx * dx + dy * dy <= R * R:
                    gain += 1
            if gain > 0:
                return p, flags
        return (fallback[1] if fallback else None), flags"""
assert a in s, "I1 hook anchor"
s = s.replace(a, b, 1)

# ------------------------------------------------------------------ I2 -----
a = """                    if new < old - 1e-9:
                        order[i:j + 1] = order[i:j + 1][::-1]
                        improved = True
        return [tasks[i] for i in order]"""
b = """                    if new < old - 1e-9:
                        order[i:j + 1] = order[i:j + 1][::-1]
                        improved = True

        # Or-opt: relocate segments of one to three tasks
        def tlen(seq):
            if not seq:
                return 0.0
            tot = self._dist(start, pos[seq[0]])
            for u, v in zip(seq, seq[1:]):
                tot += self._dist(pos[u], pos[v])
            return tot

        improved = True
        rounds = 0
        while improved and rounds < 6:
            improved = False
            rounds += 1
            base = tlen(order)
            for seg in (1, 2, 3):
                if improved or seg > len(order):
                    break
                for i in range(len(order) - seg + 1):
                    block = order[i:i + seg]
                    rest = order[:i] + order[i + seg:]
                    for k in range(len(rest) + 1):
                        if k == i:
                            continue
                        cand = rest[:k] + block + rest[k:]
                        if tlen(cand) < base - 1e-9:
                            order = cand
                            improved = True
                            break
                    if improved:
                        break
        return [tasks[i] for i in order]"""
assert a in s, "I2 anchor"
s = s.replace(a, b, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("robot_core patched: I1 rim patrol, I2 Or-opt")
