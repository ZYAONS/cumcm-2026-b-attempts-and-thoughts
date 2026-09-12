# -*- coding: utf-8 -*-
"""patch_ring_n.py -- 让基础覆盖环的点数可配置（默认 6 = 正六边形，即七点覆盖定理的最小配置）。

公开仓库用的是 8 点环（半径 1081 m），覆盖半径更大、初始交会几何更好，
代价是多两个站位。这里把点数参数化，便于实测比较。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

old = '''    def _make_ring_stops(self):
        """
        Six stops on a circle of radius `ring_radius` (plus the entry point) whose
        detection disks (radius R_min = 1000 m) cover the whole arena: this is
        the minimal complete-search configuration, see Kershner (1939) and the
        covering-radius computation of the paper.
        """
        r = self.p["ring_radius"]
        a0 = math.radians(self.p["ring_rotation"])
        return [(r * math.cos(a0 + k * math.pi / 3.0), r * math.sin(a0 + k * math.pi / 3.0))
                for k in range(6)]'''

new = '''    def _make_ring_stops(self):
        """
        Stops on a circle of radius `ring_radius` (plus the entry point) whose
        detection disks (radius R_min = 1000 m) cover the whole arena.  With
        `ring_n` = 6 this is the minimal complete-search configuration of the
        seven-point covering theorem (Kershner 1939); more points keep a larger
        coverage margin and give better triangulation geometry at the cost of
        extra legs.
        """
        r = self.p["ring_radius"]
        n = int(self.p.get("ring_n", 6) or 6)
        a0 = math.radians(self.p["ring_rotation"])
        return [(r * math.cos(a0 + 2.0 * math.pi * k / n),
                 r * math.sin(a0 + 2.0 * math.pi * k / n)) for k in range(n)]'''

assert old in s, "ring stop anchor missing"
s = s.replace(old, new, 1)

old2 = '    "ring_radius": 1280.0,      # radius of the 6 primary covering stops'
new2 = ('    "ring_radius": 1280.0,      # radius of the primary covering ring\n'
        '    "ring_n": 6,                # number of stops on that ring (6 = hexagon)')
assert old2 in s, "param anchor missing"
s = s.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("ring_n parameterised")
sys.exit(0)
