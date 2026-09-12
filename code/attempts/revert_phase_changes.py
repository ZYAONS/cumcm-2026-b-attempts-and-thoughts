# -*- coding: utf-8 -*-
"""revert_phase_changes.py -- 方向一的两种实现都实测为负优化，撤销。

Measured on the same 12 cases (problem 4):

    baseline                     10499 s virtual   39113 m travel   25.0 stops
    batch re-planning            11061 s           41659 m          24.8 stops
    batch + phase separation     12034 s           46597 m          25.0 stops

Both are worse.  The reason only became visible after measuring: clearing a
channel REMOVES it from the certification burden, so clearing early shrinks the
remaining proof obligation.  Postponing the clears until after the sweep therefore
makes the sweep itself longer, which more than cancels the routing gain.

This is the opposite of what the "decouple search and clearing" intuition
suggests, and it is worth stating plainly: the two phases are coupled through the
certification, not only through the routing.
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


rep('    "phase_separate": True,     # survey stops and clearing never share a tour',
    '    "phase_separate": False,    # MEASURED NEGATIVE (see the report): clearing\n'
    '                                # early removes channels from the certification\n'
    '                                # burden, so the phases must stay interleaved',
    "phase switch off")

rep('    "replan_mode": "batch",     # "each" (legacy) or "batch"',
    '    "replan_mode": "each",      # MEASURED NEGATIVE: re-plan after every task\n'
    '                                # beats committing to a stale tour',
    "replan mode back to each")

io.open(p, "w", encoding="utf-8").write(s)
print("both changes reverted")
