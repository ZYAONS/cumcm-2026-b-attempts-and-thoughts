# -*- coding: utf-8 -*-
"""fix_stops_cache.py -- 把普查站位改成"一次计算、永久缓存"。

两次踩同一个坑：
  1. 贴边环只写进局部变量 -> 第二次调用丢失（25 站变 13 站）；
  2. 写回 self.survey_stops 后，ring 模式下 base 仍由 _make_ring_stops() 重新生成，
     基础环把贴边环"盖掉"（ring1155 rim0 与 rim12 结果逐位相同）。

根因是同一个：普查站位集合被"按需重新计算"，而追加/排序都是**一次性**操作。
改为：首次调用时算好完整集合（基础形状 + 贴边环 + 最远点排序）并缓存，
之后直接返回缓存，不再重算。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

start = s.index("        if self.p.get(\"survey_mode\") == \"adaptive\":")
end = s.index("    def _pending_stops(self):")
new = '''        cached = getattr(self, "_primary_cache", None)
        if cached is not None:
            return list(cached)
        if self.p.get("survey_mode") == "adaptive":
            # 自适应：不预置任何站位，全部由认证扫描按需给出
            base = []
        elif self.p.get("survey_mode", "ring") == "lattice":
            base = list(self.survey_stops)
        else:
            base = self._make_ring_stops()
        # 贴边环在**任何模式**下都生效：它是"贴边朝外定向源"的唯一发现手段，
        # 与普查用什么形状无关。
        base = base + self._rim_ring_stops()
        if self.p.get("spread_stops", True) and base:
            # 最远点采样排序：截断时保留均匀覆盖，而不是砍掉外圈
            base = self._spread_order(base)
        self._primary_cache = list(base)
        self.survey_stops = list(base)
        return list(base)

'''
s = s[:start] + new + s[end:]
io.open(p, "w", encoding="utf-8").write(s)
print("survey stops are now computed once and cached")
