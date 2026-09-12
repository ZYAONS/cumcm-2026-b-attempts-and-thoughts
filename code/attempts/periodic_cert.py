# -*- coding: utf-8 -*-
"""periodic_cert.py -- 扫描过程中周期性认证，已认证的频道立刻停止检测。

Why this matters: with the certification search switched off, pure_sweep measured
19 stops and 367 detections (2202 s) per case -- about 19 stations times 19
channels, i.e. EVERY channel is measured at EVERY stop.

The reason is that the certificate is only evaluated inside next_search_stop, and
with no search stops allowed it is never called at all: no channel is ever marked
"empty", so `_worth_measuring` keeps saying yes for all twenty of them.

But the certificate does not need extra stops.  A sweep at 900 m spacing already
gives every candidate three readings from three directions -- the three vertices
of its containing lattice triangle, all inside the 958 m certification radius and
surrounding it.  So evaluating the certificate DURING the sweep, and marking the
proved-absent channels as empty, lets every later stop skip them.

Expected: detections drop from ~367 to ~150, saving about 1300 s.
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


rep('    "cert_heard_channels": False,  # certification also covers channels that',
    '    "periodic_cert": True,      # evaluate the certificate during the sweep so\n'
    '                                # that certified channels stop being measured\n'
    '    "periodic_cert_every": 2,   # ... after every N covering stops\n'
    '    "cert_heard_channels": False,  # certification also covers channels that',
    "parameter")

rep("""                self.visited_stops.add((round(p[0], 1), round(p[1], 1)))
                self.probe(p, force=True)
                n_act += 1
                self._commit_estimates()
                replan = (not batch) or heard_count() > last_heard or clear_count() > last_cleared
        return n_act""",
    """                self.visited_stops.add((round(p[0], 1), round(p[1], 1)))
                self.probe(p, force=True)
                n_act += 1
                self._commit_estimates()
                if self.p.get("periodic_cert", True):
                    self._since_cert = getattr(self, "_since_cert", 0) + 1
                    if self._since_cert >= int(self.p.get("periodic_cert_every", 2)):
                        self._since_cert = 0
                        self._mark_certified()
                replan = (not batch) or heard_count() > last_heard or clear_count() > last_cleared
        return n_act""",
    "periodic call")

rep("    def _rim_patrol_stops(self, uncov):",
    '''    def _mark_certified(self):
        """
        Evaluate the certificate during the sweep and mark the channels it proves
        absent as "empty".

        Nothing else would do it when the search stops are disabled, and a
        certified channel can never be heard again, so measuring it at every
        remaining stop is pure waste.
        """
        unresolved = [c for c in self.channels
                      if self.status[c] not in ("cleared", "empty")]
        if not self.p.get("cert_heard_channels", False):
            cert_set = [c for c in unresolved if not self.obs.get(c)]
        else:
            cert_set = list(unresolved)
        if not cert_set:
            return 0
        try:
            ok, uncov, flags = self.certification_scan(cert_set)
        except Exception:
            return 0
        n = 0
        for c, v in flags.items():
            if v and self.status.get(c) not in ("cleared", "empty"):
                self.status[c] = "empty"
                n += 1
        return n

    def _rim_patrol_stops(self, uncov):''',
    "helper")

io.open(p, "w", encoding="utf-8").write(s)
print("periodic certification installed")
