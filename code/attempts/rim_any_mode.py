# -*- coding: utf-8 -*-
"""rim_any_mode.py -- 让贴边环在任何 survey_mode 下都生效。

发现：`_rim_ring_stops()` 只被加在 `survey_mode == "lattice"` 的分支里，
于是 ring 模式下 rim_ring_n 完全无效（实测 ring1155 rim0 与 rim12 的结果逐位相同）。
贴边环是"边界源发现"的通用机制，与格点模式无关，应当无条件生效。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

a = '''        if self.p.get("survey_mode") == "adaptive":
            # 自适应：不预置任何站位，全部由认证扫描按需给出
            return []
        if self.p.get("survey_mode", "ring") == "lattice":
            if not getattr(self, "_rim_done", False):
                self.survey_stops = list(self.survey_stops) + self._rim_ring_stops()
                self._rim_done = True
            if self.p.get("spread_stops", True) and not getattr(
                    self, "_spread_done", False):
                self.survey_stops = self._spread_order(self.survey_stops)
                self._spread_done = True
            return list(self.survey_stops)
        return self._make_ring_stops()'''

b = '''        if self.p.get("survey_mode") == "adaptive":
            # 自适应：不预置任何站位，全部由认证扫描按需给出
            base = []
        elif self.p.get("survey_mode", "ring") == "lattice":
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

assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("rim ring now applies in every survey mode")
