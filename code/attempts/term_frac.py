# -*- coding: utf-8 -*-
"""term_frac.py -- 把归航步长的保守系数参数化。

行程审计显示"清除"任务有 26 段腿、共 6233 m，而源只有 12.5 个——
即**每个源平均要走 2.1 段**。其中第一段是走向估计点，后续段是归航修正。
`clear_channel` 里每步只走 `0.7*d`（d 为到估计点的距离），这是为了防过冲，
但当估计已经比较准时，这个保守系数就浪费了一整段腿。

把它参数化为 `term_step_frac`，扫描 0.7 / 0.85 / 1.0。
清单段腿约可省 13 段 × 240 m = 3100 m = 620 s = 50 s/源。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()
a = 'step = max(6.0, min(0.7 * d, self.p["term_cap"])) * step_scale'
b = 'step = max(6.0, min(float(self.p.get("term_step_frac", 0.7)) * d,\n' \
    '                               self.p["term_cap"])) * step_scale'
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("term_step_frac parameterised")
