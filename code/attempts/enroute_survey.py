# -*- coding: utf-8 -*-
"""enroute_survey.py -- 把长距离移动分段，途中顺带测量。

新发现的实现事实
----------------
`move_measure` 是**一步跳到目标**：机器人从 A 直接"瞬移"到 B，
只测量终点。也就是说**路过的整片区域从未被采样**。
于是所有信息只能来自"普查站位"，而普查占了 212 s/源（行程审计）。

新机制
------
在走向目标的途中，按 `leg_probe_step`（例如 350 m）插入若干中间测点，
只测**从未听到过的频道**（认证正需要这些读数）。
关键性质：**这段路本来就要走，中间测点不增加任何行程**，
所以它们是"免费的采样点"，可以用来替代昂贵的普查站位。

代价只有测量时间：每个中间测点测 k 个频道 = k*(5s+切换)。
而省下的是整个普查行程——如果普查站位因此可以取消，就能省 212 s/源。

实现上要避免递归：中间点的移动距离 <= step，不会再触发分段。
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


rep('    "enroute_clear": False,     # MEASURED NEGATIVE (24 cases): 1.0000 -> 0.9946',
    '    "leg_probe_step": 0.0,      # 长距离移动的分段长度（m）；>0 时途中顺带测量\n'
    '    "leg_probe_max_channels": 8,  # 每个中间测点最多测几个频道\n'
    '    "enroute_clear": False,     # MEASURED NEGATIVE (24 cases): 1.0000 -> 0.9946',
    "parameters")

rep("    def move_measure(self, x, y, channel):",
    '''    def _enroute_survey(self, x, y):
        """
        On the way to (x, y), stop every `leg_probe_step` metres and measure the
        channels that have never been heard.

        Those intermediate points cost no extra travel -- the leg is walked
        anyway -- so they are free sampling positions, and the certificate is
        exactly what needs readings for the never-heard channels.  This is what
        lets the dedicated survey stops be dropped.
        """
        step = float(self.p.get("leg_probe_step", 0.0) or 0.0)
        if step <= 0.0:
            return 0
        x0, y0 = self.pos
        d = math.hypot(x - x0, y - y0)
        if d <= 1.5 * step:
            return 0
        todo_all = [c for c in self.channels
                    if not self.obs.get(c)
                    and self.status.get(c) not in ("cleared", "empty")]
        if not todo_all:
            return 0
        k_max = int(self.p.get("leg_probe_max_channels", 8))
        n = int(d // step)
        done = 0
        for k in range(1, n + 1):
            t = k * step / d
            if t >= 0.92 or self.vtime > self.p.get("max_virtual_guard", 1e18):
                break
            px, py = x0 + (x - x0) * t, y0 + (y - y0) * t
            todo = [c for c in self.channels
                    if not self.obs.get(c)
                    and self.status.get(c) not in ("cleared", "empty")][:k_max]
            todo.sort()
            for c in todo:
                self.move_measure(px, py, c)      # d <= step: no recursion
                done += 1
        return done

    def move_measure(self, x, y, channel):''',
    "helper")

rep("""        d = self._dist(self.pos, (x, y))
        sw = 1.0 if channel != self.cur_channel else 0.0
        self.vtime += d / SPEED + sw + 5.0""",
    """        if self.p.get("leg_probe_step", 0.0):
            self._enroute_survey(x, y)
        d = self._dist(self.pos, (x, y))
        sw = 1.0 if channel != self.cur_channel else 0.0
        self.vtime += d / SPEED + sw + 5.0""",
    "hook in move_measure")

io.open(p, "w", encoding="utf-8").write(s)
print("en-route segmented survey installed")
