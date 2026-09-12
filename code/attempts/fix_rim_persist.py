# -*- coding: utf-8 -*-
"""fix_rim_persist.py -- 贴边环必须写回 self.survey_stops，否则第二次调用就丢了。

上一版的回归：`_primary_stops()` 第一次返回 25 个站位，第二次只返回 13 个。
原因是我把"格点 + 贴边环"写进了局部变量 base，而 `_rim_done` 守卫已经置位，
于是第二次调用不再追加贴边环。原实现是写回 `self.survey_stops` 的，
那样才能持久。修正：写回实例属性。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

a = '''        elif self.p.get("survey_mode", "ring") == "lattice":
            base = list(self.survey_stops)
        else:
            base = self._make_ring_stops()
        # 贴边环在**任何模式**下都生效：它是"贴边朝外定向源"的唯一发现手段，
        # 与普查用什么形状无关
        if not getattr(self, "_rim_done", False):
            base = base + self._rim_ring_stops()
            self._rim_done = True
        if self.p.get("spread_stops", True) and not getattr(
                self, "_spread_done", False):
            base = self._spread_order(base)
            self._spread_done = True
        return base'''

b = '''        elif self.p.get("survey_mode", "ring") == "lattice":
            base = list(self.survey_stops)
        else:
            base = self._make_ring_stops()
            self.survey_stops = list(base)
        # 贴边环在**任何模式**下都生效：它是"贴边朝外定向源"的唯一发现手段，
        # 与普查用什么形状无关。注意必须写回实例属性——否则 _rim_done 置位后
        # 第二次调用就会丢掉这批点（曾因此把 25 个站位变成 13 个）。
        if not getattr(self, "_rim_done", False):
            base = base + self._rim_ring_stops()
            self._rim_done = True
        if self.p.get("spread_stops", True) and not getattr(
                self, "_spread_done", False):
            base = self._spread_order(base)
            self._spread_done = True
        self.survey_stops = list(base)
        return list(base)'''

assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("rim ring now persists")
