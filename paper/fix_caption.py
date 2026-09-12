# -*- coding: utf-8 -*-
"""fix_caption.py -- the baseline chart now uses a log axis and shows the true
values, so the caption must not claim a 400 m truncation."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p2.tex")
s = io.open(p, encoding="utf-8").read()
old = ("\\caption{五种第二检测点规则的实际定位区域直径（均值与 95\\% 分位；为便于显示，纵轴截断于 "
       "400 m。C、D 两策略存在无界情形，真实均值分别为 2508.7 m 与 1285.0 m）}")
new = ("\\caption{五种第二检测点规则的实际定位区域直径（纵轴取对数坐标；C、D 两策略在部分算例中定位区域"
       "无界，其 95\\% 分位为 $\\infty$，故仅给出均值）}")
assert old in s, "caption anchor missing"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("caption fixed")
