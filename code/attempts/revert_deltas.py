# -*- coding: utf-8 -*-
"""revert_deltas.py -- 恢复"偏移由大到小"的次序。

实测（24 例）：由大到小 完成率 1.0000 / 540.3 s；
              由小到大 完成率 0.9965（1 例失败）/ 541.2 s
虽然后者把 localise 行程从 2529 m 砍到 1191 m，但总行程反而从 22343 m 升到
22979 m，且完成率下降——大偏移先试能更早拿到"方向差够大"的第二条方位，
对定位于事有补。恢复原次序。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()
old = "[20.0, 33.0, 55.0, 90.0, 150.0, 250.0, 400.0]"
new = "[400.0, 250.0, 150.0, 90.0, 55.0, 33.0, 20.0]"
n = s.count(old)
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8").write(s)
print("restored big->small in %d places" % n)
