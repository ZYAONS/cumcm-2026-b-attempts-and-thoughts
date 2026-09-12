# -*- coding: utf-8 -*-
"""spread_stops.py -- 截断扫描站位时，取"分布最均匀的 N 个"而不是"最靠内的 N 个"。

max_survey_stops 目前按 `_make_survey_stops` 的排序（由内向外）截断，
于是限制到 15 个就等于放弃最外圈——而最外圈正是边界附近源的唯一机会。

改为**最远点采样**（farthest point sampling）排序：先取最靠近中心的一个，
然后每次取"离已选集合最远"的那个点。这样前 N 个点在整个目标域上均匀铺开，
截断到 15 个也能保持覆盖。
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


rep('    "max_survey_stops": 0,      # cap on the number of primary survey stops',
    '    "spread_stops": True,       # order the survey stops by farthest-point\n'
    '                                # sampling, so a cap keeps the arena covered\n'
    '    "max_survey_stops": 0,      # cap on the number of primary survey stops',
    "parameter")

# apply the reordering where the survey stops are first built
rep("""        if self.p.get("survey_mode", "ring") == "lattice":
            return list(self.survey_stops)""",
    """        if self.p.get("survey_mode", "ring") == "lattice":
            if self.p.get("spread_stops", True) and not getattr(
                    self, "_spread_done", False):
                self.survey_stops = self._spread_order(self.survey_stops)
                self._spread_done = True
            return list(self.survey_stops)""",
    "primary stops")

rep("    def _all_search_stops(self):",
    '''    def _spread_order(self, pts):
        """
        Farthest-point ordering: start at the point nearest the origin, then
        repeatedly append the point farthest from everything chosen so far.

        Truncating this list to N stops therefore keeps the arena evenly covered,
        whereas truncating the radius-sorted list would drop the outer ring -- the
        only chance of finding a source near the rim.
        """
        rest = [tuple(q) for q in pts]
        if not rest:
            return []
        first = min(rest, key=lambda q: q[0] * q[0] + q[1] * q[1])
        order = [first]
        rest.remove(first)
        while rest:
            nxt = max(rest, key=lambda q: min(
                (q[0] - a[0]) ** 2 + (q[1] - a[1]) ** 2 for a in order))
            order.append(nxt)
            rest.remove(nxt)
        return order

    def _all_search_stops(self):''',
    "spread helper")

io.open(p, "w", encoding="utf-8").write(s)
print("farthest-point ordering installed")
