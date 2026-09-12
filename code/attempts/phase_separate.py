# -*- coding: utf-8 -*-
"""phase_separate.py -- 方向一的本体：把"搜索"与"清除"真正分成两个阶段。

Why batch re-planning alone did not help (measured, 12 cases):

    before              10499 s virtual, 39113 m travel, 25.0 stops
    batch re-planning   11061 s virtual, 41659 m travel, 24.8 stops

Keeping a committed plan does not help while the plan still MIXES survey stops
with clearing detours: the robot walks out to a source, comes back to the survey,
walks out again.  Twenty-five stops spread over a 3600 m arena admit a tour of
roughly 10-12 km, yet the survey task alone consumes 23 km.

The fix is to separate the two phases explicitly:

    survey phase : visit every pending stop, nothing else
    clear phase  : neutralise everything that has been located
    repeat       : certification may ask for a few more stops, then clear again

A source that is located early is cleared a little later; nothing has a deadline,
whereas every avoided detour saves travel twice (out and back).
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


rep('    "replan_mode": "batch",     # "each" (legacy) or "batch"',
    '    "replan_mode": "batch",     # "each" (legacy) or "batch"\n'
    '    "phase_separate": True,     # survey stops and clearing never share a tour',
    "parameter")

# insert the phase gate at the head of the clear/vantage section of _build_tasks
rep("""        tasks.extend(clears)
        # second bearings are preferably taken at positions the robot visits""",
    """        if self.p.get("phase_separate", True) and pending:
            # SURVEY PHASE: while any covering stop is still unvisited, the tour
            # contains stops only.  Mixing a clearing detour into the sweep makes
            # the robot leave the survey area and come back, and the same detour is
            # then paid twice.
            return [("stop", None, q) for q in pending]
        tasks.extend(clears)
        # second bearings are preferably taken at positions the robot visits""",
    "phase gate")

io.open(p, "w", encoding="utf-8").write(s)
print("phase separation installed")
