# -*- coding: utf-8 -*-
"""rim_ring.py -- 混合策略的最后一环：给扫描加一圈贴边站位。

四池汇总（各 30 例）揭示了真正的权衡：
    配置              最差完成率   平均时间   失败算例
    P4（论文，24 站）    0.9978     880.7 s    1/120
    s1000 纯扫描（13 站） 0.9833     533.8 s   14/120
    s900  纯扫描（18 站） 0.9751     554.5 s   17/120

为什么 P4 更稳？因为它的 24 个站位里约 17 个是**认证搜索**补出来的，
而认证搜索把站位放到"证书最弱"的地方——那恰恰就是**定向源可能藏身**的地方。
换句话说，**认证搜索兼任了定向源发现器**，这是它真正的价值，不是认证本身。

而贴边朝外的定向源，其域内受光区是一条**贴着边界的薄月牙**。
任何朝外方向的月牙都会与半径 1750 m 的圆环相交，所以：

    **在扫描里加一圈贴边站位，就能以很低的代价覆盖所有"朝外"的定向源。**

这一圈站位是**直接服务于发现**的（而不是认证），因此与"边距剔除边界候选点"
的改动不冲突：边距只影响认证网格，不影响扫描站位。
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


rep('    "spread_stops": True,       # order the survey stops by farthest-point',
    '    "rim_ring_n": 0,            # 贴边环：在 r=rim_ring_r 上补 n 个站位，\n'
    '                                # 专门发现"朝外辐射"的贴边定向源\n'
    '    "rim_ring_r": 1750.0,\n'
    '    "spread_stops": True,       # order the survey stops by farthest-point',
    "parameter")

rep("    def _primary_stops(self):",
    '''    def _rim_ring_stops(self):
        """
        贴边环：在半径 rim_ring_r 上均匀放 n 个站位。

        贴边且朝外辐射的定向源，其域内受光区是一条贴着边界的薄月牙；
        任何方向的月牙都会与这圈站位相交，因此在环上均匀取样就能发现它。
        这些站位只服务于**发现**，与认证边距（verify_margin）无关。
        """
        n = int(self.p.get("rim_ring_n", 0) or 0)
        if n <= 0:
            return []
        r = float(self.p.get("rim_ring_r", 1750.0))
        rot = math.radians(float(self.p.get("ring_rotation", 0.0)))
        return [(r * math.cos(rot + 2.0 * math.pi * k / n),
                 r * math.sin(rot + 2.0 * math.pi * k / n)) for k in range(n)]

    def _primary_stops(self):''',
    "helper")

rep("""        if self.p.get("survey_mode", "ring") == "lattice":
            if self.p.get("spread_stops", True) and not getattr(
                    self, "_spread_done", False):
                self.survey_stops = self._spread_order(self.survey_stops)
                self._spread_done = True
            return list(self.survey_stops)""",
    """        if self.p.get("survey_mode", "ring") == "lattice":
            if not getattr(self, "_rim_done", False):
                self.survey_stops = list(self.survey_stops) + self._rim_ring_stops()
                self._rim_done = True
            if self.p.get("spread_stops", True) and not getattr(
                    self, "_spread_done", False):
                self.survey_stops = self._spread_order(self.survey_stops)
                self._spread_done = True
            return list(self.survey_stops)""",
    "primary stops")

io.open(p, "w", encoding="utf-8").write(s)
print("rim ring installed")
