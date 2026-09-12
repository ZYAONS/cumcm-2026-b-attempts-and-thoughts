# -*- coding: utf-8 -*-
"""vantage_creep.py -- the last residual failure mode.

Diagnosis of the two remaining failures (2 sources out of 914; both near-rim
directional sources with exactly one bearing):

    ch 2  source at (-1760, -76) r=1761   the bearing was taken at (-1800, 0)
    ch13  source at ( 1717,  21) r=1717   the bearing was taken at ( 1800, 0)

In both cases the robot stood ON the arena boundary, 85 m from the source and on
the lit side, and the on-ray vantage was placed 550 m further along the ray --
465 m BEYOND the source, i.e. on the dark side.  All three vantage attempts were
spent that way and the channel never obtained its second bearing, so it stayed
"seen" and no clear task was ever generated.

The ray-approach lemma guarantees only the segment from the hearing point TOWARDS
the source; what lies beyond is unknown, and the range is exactly what is not
known.  A long single hop is therefore a gamble.

Fix: creep along the ray.  Each on-ray attempt advances by `vantage_step_onray`
(200 m, scaled); if the reading comes back silent the robot has overshot, so it
returns to the hearing point and halves the hop.  The second bearing is then taken
from a point guaranteed to be inside the lit part of the ray.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()


def rep(a, b, tag):
    global s
    assert a in s, "anchor missing: " + tag
    s = s.replace(a, b, 1)
    print("  ok:", tag)


rep('    "vantage_onray": True,      # shrink the 2nd-station offset and finally',
    '    "vantage_step_onray": 200.0,  # creep along the ray instead of jumping\n'
    '    "vantage_onray_bisect": True,  # retreat and halve when the signal is lost\n'
    '    "vantage_onray_tries": 16,     # hop budget while creeping\n'
    '    "vantage_onray": True,      # shrink the 2nd-station offset and finally',
    "parameters")

rep("        self.perp_tries = {}\n        self.last_attempt_obs = {}",
    "        self.perp_tries = {}\n        self.last_attempt_obs = {}\n"
    "        self.onray_scale = {}\n        self.onray_tries = {}",
    "per-channel state")

rep("""        o = self.obs[c][-1]
        r_lim = self._ray_limit(o)
        tries = self.vantage_tries.get(c, 0)""",
    """        o = self.obs[c][-1]
        r_lim = self._ray_limit(o)
        tries = self.vantage_tries.get(c, 0)
        onray = False""",
    "vantage head")

rep("""            else:
                phi0 = 0.0
                b = min(b, max(180.0, 0.55 * r_lim))""",
    """            else:
                # On-ray: creep instead of jumping.  A long hop can pass the
                # source and land on the dark side (the range is unknown), so the
                # step is short and is halved whenever the signal is lost.
                phi0 = 0.0
                onray = True
                b = min(float(self.p.get("vantage_step_onray", 200.0))
                        * self.onray_scale.get(c, 1.0), max(r_lim - 1.0, 12.0))
                b = max(b, 12.0)""",
    "on-ray hop")

# the returned point must carry the flag: change the return value
rep("""        return None if best is None else best[1]""",
    """        if best is None:
            return None
        return best[1] if not onray else (best[1], True)""",
    "return flag")

rep("""                p = self.vantage_point(c, local=True)
                if p is not None:
                    tasks.append(("vantage", c, p))""",
    """                p = self.vantage_point(c, local=True)
                if p is not None:
                    if isinstance(p, tuple) and len(p) == 2 and p[1] is True:
                        tasks.append(("vantage", c, p[0],
                                      {"onray": True,
                                       "origin": self.obs[c][-1][:2]}))
                    else:
                        tasks.append(("vantage", c, p))""",
    "task build")

rep("""            elif kind == "vantage":
                self._cur_task = "localise"
                self._task_count["localise"] += 1
                p = task[2]
                self.vantage_tries[task[1]] = self.vantage_tries.get(task[1], 0) + 1
                self.move_measure(p[0], p[1], task[1])
                n_act += 1
                self.probe(self.pos)
                replan = True""",
    """            elif kind == "vantage":
                self._cur_task = "localise"
                self._task_count["localise"] += 1
                c = task[1]
                p = task[2]
                meta = task[3] if len(task) > 3 else {}
                self.vantage_tries[c] = self.vantage_tries.get(c, 0) + 1
                r = self.move_measure(p[0], p[1], c)
                n_act += 1
                if meta.get("onray") and self.p.get("vantage_onray_bisect", True):
                    self.onray_tries[c] = self.onray_tries.get(c, 0) + 1
                    if r.get("measure_result") in ("direction", "near"):
                        self.onray_scale[c] = 1.0
                    else:
                        # overshot: return to the hearing point and shorten the
                        # next hop so that it lands inside the lit part of the ray
                        self.onray_scale[c] = max(
                            0.08, self.onray_scale.get(c, 1.0) * 0.45)
                        o = meta.get("origin")
                        if o is not None:
                            self.hear(c, (o[0], o[1]))
                self.probe(self.pos)
                replan = True""",
    "task execute")

rep("""                if self.vantage_tries.get(c, 0) >= self.p["vantage_max_tries"]:
                    continue""",
    """                if (self.vantage_tries.get(c, 0) >= self.p["vantage_max_tries"]
                        and self.onray_tries.get(c, 0)
                        >= self.p.get("vantage_onray_tries", 16)):
                    continue""",
    "budget")

io.open(p, "w", encoding="utf-8").write(s)
print("on-ray creep with bisection installed")
