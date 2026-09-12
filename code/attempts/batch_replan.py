# -*- coding: utf-8 -*-
"""batch_replan.py -- 方向一：把搜索与清除解耦，并让巡回真正被走完。

Measured before the change (problem 4, 12 cases):

    25.0 stops per case, 39113 m of travel, 28275 m of it on the survey task
    a nearest-neighbour tour over the SAME stops costs only 18574 m

So the robot travels 1.5 times what the stop set requires.  The reason is that
`_run_planned` rebuilds the whole task tour after EVERY executed task, always by
nearest neighbour from the current position.  Each rebuild is locally optimal but
globally myopic: a task that was scheduled third can be pushed behind a task that
happens to be nearby now, and the robot keeps changing its mind.

Two changes, which reinforce each other:

  R1  batch re-planning.  The tour is kept until it is exhausted or something
      genuinely new appears (a previously unheard channel is discovered, or a
      clear succeeds).  Ordinary progress no longer invalidates the plan, so the
      robot walks the route it committed to.

  R2  because re-planning is now rare, the tour construction itself can be much
      more thorough: Or-opt over the WHOLE tour (not just the first twelve tasks)
      and more 2-opt rounds.  Twenty to forty tasks cost milliseconds, and the
      plan is rebuilt only a handful of times per case instead of every step.
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


rep('    "oropt_limit": 12,          # Or-opt only reorders this tour prefix',
    '    "oropt_limit": 12,          # Or-opt prefix used when re-planning often\n'
    '    "oropt_limit_batch": 60,    # ... and when re-planning rarely (batch mode)\n'
    '    "replan_mode": "batch",     # "each" (legacy) or "batch"',
    "parameters")

# --- R2: wider Or-opt and more 2-opt rounds in batch mode -------------------
rep("        LIMIT = int(self.p.get(\"oropt_limit\", 12))",
    "        if self.p.get(\"replan_mode\", \"batch\") == \"batch\":\n"
    "            LIMIT = int(self.p.get(\"oropt_limit_batch\", 60))\n"
    "        else:\n"
    "            LIMIT = int(self.p.get(\"oropt_limit\", 12))",
    "oropt limit")

rep("        while improved and guard < 12:", "        while improved and guard < 40:",
    "2-opt rounds")

rep("        while improved and rounds < 4 and len(head) > 3:",
    "        while improved and rounds < 8 and len(head) > 3:",
    "or-opt rounds")

# --- R1: batch re-planning --------------------------------------------------
rep("""    def _run_planned(self, n_act, max_actions):
        replan = True
        tour = []
        extra_stops = []""",
    """    def _run_planned(self, n_act, max_actions):
        replan = True
        tour = []
        extra_stops = []
        batch = self.p.get("replan_mode", "batch") == "batch"

        def heard_count():
            return sum(1 for c in self.channels if self.obs.get(c))

        def clear_count():
            return sum(1 for c in self.channels if self.status.get(c) == "cleared")

        last_heard, last_cleared = heard_count(), clear_count()""",
    "batch state")

# every place that sets replan = True becomes conditional
n_rep = s.count("                replan = True")
s = s.replace("                replan = True",
              "                replan = (not batch) or heard_count() > last_heard"
              " or clear_count() > last_cleared")
print("  ok: %d replan sites made conditional" % n_rep)

# refresh the baselines after each executed task
rep("""            task = tour.pop(0)""",
    """            last_heard, last_cleared = heard_count(), clear_count()
            task = tour.pop(0)""",
    "baseline refresh")

io.open(p, "w", encoding="utf-8").write(s)
print("batch re-planning + whole-tour Or-opt installed")
