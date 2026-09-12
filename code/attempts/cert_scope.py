# -*- coding: utf-8 -*-
"""cert_scope.py -- 认证只针对"从未听到过"的频道。

Measured certification gap (cert_gap.py, 8 cases, spacing 1100):

    stops = 25.1 per case, of which 18.1 are certification search stops
    after the primary sweep: 10801 candidates still open, over 8.2 channels
    worst radius of an open candidate: 1708 m  (the rim margin, already excluded)
    smallest distance from an open candidate to a TRUE source: 6 m

So the open candidates are not at the rim -- they sit next to real sources.  The
reason is structural: for the channel of a source at q*, the readings around q*
are mixed (the lit side hears it, the dark side returns no_signal), so the
no-signal readings near q* all lie on the dark side and can never surround q*.
The candidate stays open forever, and the search keeps sending the robot out to
prove that a source it has already heard does not exist.

A channel that has been heard EXISTS.  It does not need a certificate of absence;
it needs to be located and cleared.  Only channels with no reading at all require
a proof of absence.  Restricting the certification to those is both logically
correct and removes the entire wasted search.

The termination logic is unchanged for the channels that matter: a "seen" channel
that is never located still blocks `_all_done`, so the robot keeps pursuing it
through the vantage machinery.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

a = '    "phase_separate": False,    # MEASURED NEGATIVE (see the report): clearing'
b = ('    "cert_heard_channels": False,  # certification also covers channels that\n'
     '                                # were already heard (wasteful: measured 18\n'
     '                                # extra stops per case), kept as a switch\n'
     '    "phase_separate": False,    # MEASURED NEGATIVE (see the report): clearing')
assert a in s, "param anchor"
s = s.replace(a, b, 1)

# next_search_stop: narrow the unresolved list it certifies
a = """        ok, uncov, flags = self.certification_scan(unresolved)"""
b = """        if not self.p.get("cert_heard_channels", False):
            # A channel that was heard exists: it needs locating and clearing, not
            # a proof of absence.  Certifying it is logically pointless and, as
            # measured, costs about eighteen wasted stops per case.
            cert_set = [c for c in unresolved if not self.obs.get(c)]
        else:
            cert_set = list(unresolved)
        if not cert_set:
            return None, {}
        ok, uncov, flags = self.certification_scan(cert_set)"""
assert a in s, "search anchor"
s = s.replace(a, b, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("certification narrowed to never-heard channels")
