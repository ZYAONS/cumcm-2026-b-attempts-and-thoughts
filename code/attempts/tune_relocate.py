# -*- coding: utf-8 -*-
"""tune_relocate.py -- 撤销顺路清除；把 relocate 的偏移量改成"由小到大"。

一、顺路清除实测为负优化（24 例）：
      关闭            完成率 1.0000（0 例失败）/ 540.3 s / 行程 22343 m
      开启 r=520      完成率 0.9946（2 例失败）/ 573.3 s / 行程 24935 m
      开启 r=350      完成率 0.9972（1 例失败）/ 544.4 s / 行程 22741 m
      开启 r=750      完成率 0.9946（2 例失败）/ 599.3 s / 行程 27091 m
   原因：机会式清除会打断扫描，而 clear_channel 自身的归航与末段图案带来的
   额外移动**超过了它省下的那趟绕行**；同时推迟了扫描的发现进度。撤销。

二、relocate 的成本值得优化：localise 任务 6.8 次/例、行程 2487 m、时间 921 s，
   占总时间 13.6%。偏移序列原本是"由大到小"（400→20 m），
   但几何上**受光半平面必然包含听到点本身**，所以偏移越小越可能受光、
   而且往返越便宜。改为**由小到大**。
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


rep('    "enroute_clear": True,      # 顺路清除：已定位的源若就在附近，立刻清掉',
    '    "enroute_clear": False,     # MEASURED NEGATIVE (24 cases): 1.0000 -> 0.9946\n'
    '                                # and 540.3 -> 573.3 s; the opportunistic clear\n'
    '                                # interrupts the sweep and its own homing costs\n'
    '                                # more than the detour it saves',
    "enroute off")

rep('    "relocate_deltas": [400.0, 250.0, 150.0, 90.0, 55.0, 33.0, 20.0],',
    '    "relocate_deltas": [20.0, 33.0, 55.0, 90.0, 150.0, 250.0, 400.0],',
    "deltas small first")

rep('        deltas = list(self.p.get("relocate_deltas",\n'
    '                                 [400.0, 250.0, 150.0, 90.0, 55.0, 33.0, 20.0]))\n'
    '        if st["d"] >= len(deltas):',
    '        deltas = list(self.p.get("relocate_deltas",\n'
    '                                 [20.0, 33.0, 55.0, 90.0, 150.0, 250.0, 400.0]))\n'
    '        if st["d"] >= len(deltas):',
    "query default")

rep('        deltas = list(self.p.get("relocate_deltas",\n'
    '                                 [400.0, 250.0, 150.0, 90.0, 55.0, 33.0, 20.0]))\n'
    '        if st["side"] == 0:',
    '        deltas = list(self.p.get("relocate_deltas",\n'
    '                                 [20.0, 33.0, 55.0, 90.0, 150.0, 250.0, 400.0]))\n'
    '        if st["side"] == 0:',
    "advance default")

io.open(p, "w", encoding="utf-8").write(s)
print("done")
