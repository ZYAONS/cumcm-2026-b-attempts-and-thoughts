# -*- coding: utf-8 -*-
"""cap_lattice_only.py -- 站位上限只作用于格点，贴边环永远保留。

发现：`_pending_stops` 的 cap 一旦达到就把**全部**待访站位清空，
而贴边环排在格点之后，于是"限制格点数"变成了"连贴边环一起砍掉"。
这解释了此前所有 cap 实验的异常：cap8 时总站位只有 12.6 个（8 格点 + 少量自适应），
贴边环 12 个点一个都没去——难怪完成率掉、行程反而升。

修正：把贴边环单独记录，cap 只作用于非贴边环的部分。
这样才能真正测试"**少布格点 + 保留贴边环**"这个组合。
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


rep("""        # 贴边环在**任何模式**下都生效：它是"贴边朝外定向源"的唯一发现手段，
        # 与普查用什么形状无关。
        base = base + self._rim_ring_stops()""",
    """        # 贴边环在**任何模式**下都生效：它是"贴边朝外定向源"的唯一发现手段，
        # 与普查用什么形状无关。单独记下来，好让站位上限只作用于格点部分。
        self._rim_only = list(self._rim_ring_stops())
        base = base + self._rim_only""",
    "remember rim")

rep('''    def _pending_stops(self):
        """Covering stops that still have to be visited."""
        cap = int(self.p.get("max_survey_stops", 0) or 0)
        if cap > 0 and len(self.visited_stops) >= cap:
            return []
        out = []
        for p in self._primary_stops():
            if self._stop_is_useless(p):
                continue
            key = (round(p[0], 1), round(p[1], 1))
            if key not in self.visited_stops:
                out.append(p)
        return out''',
    '''    def _pending_stops(self):
        """
        Covering stops that still have to be visited.

        `max_survey_stops` caps only the LATTICE part.  The rim ring is always
        kept: it is the only way to discover sources that radiate outward from the
        rim, and capping the combined list silently dropped it entirely (which is
        why the earlier cap experiments looked so bad).
        """
        cap = int(self.p.get("max_survey_stops", 0) or 0)
        rim = set((round(q[0], 1), round(q[1], 1))
                  for q in getattr(self, "_rim_only", ()))
        out = []
        n_base = 0
        visited_base = sum(1 for k in self.visited_stops if k not in rim)
        for p in self._primary_stops():
            key = (round(p[0], 1), round(p[1], 1))
            if key in self.visited_stops:
                continue
            if self._stop_is_useless(p):
                continue
            if key not in rim:
                if cap > 0 and visited_base + n_base >= cap:
                    continue
                n_base += 1
            out.append(p)
        return out''',
    "cap lattice only")

io.open(p, "w", encoding="utf-8").write(s)
print("cap now applies to the lattice only")
