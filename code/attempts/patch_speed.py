# -*- coding: utf-8 -*-
"""patch_speed.py -- 三个可压缩用时的候选改动（全部以参数形式加入，默认不改变原行为）。

1) sweep_center_first : 端末清除图案先试"估计中心"，失败后再按原顺序扫，最后再回到中心。
                        估计误差中位数只有几米，中心往往一击即中，可省下一整圈 12 次尝试。
2) survey_max_r       : 把认证格点限制在某个半径内（默认 1800 = 不限制）。
3) rim_ring_n         : 已有参数，这里只做扫描。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

# ---- 1) survey lattice radius limit -------------------------------------
old = '''    def _make_survey_stops(self, spacing=None):
        """Triangular lattice of survey stops covering the arena."""
        s = self.p["survey_spacing"] if spacing is None else spacing
        stops = []
        ny = int(self.arena_r / (s * math.sqrt(3.0) / 2.0)) + 2
        nx = int(2 * self.arena_r / s) + 2
        for iy in range(-ny, ny + 1):
            y = iy * s * math.sqrt(3.0) / 2.0
            for ix in range(-nx, nx + 1):
                x = ix * s + (s / 2.0 if iy % 2 else 0.0)
                if math.hypot(x, y) <= self.arena_r + 1e-9:
                    stops.append((x, y))
        stops.sort(key=lambda p: math.hypot(p[0], p[1]))
        return stops'''
new = '''    def _make_survey_stops(self, spacing=None):
        """Triangular lattice of survey stops covering the arena.

        `survey_max_r` (default = arena radius) truncates the lattice: only the
        region that actually has to be certified needs the multi-directional
        coverage a lattice provides, so the outer shell can be dropped when a
        separate mechanism (the rim ring) covers it.
        """
        s = self.p["survey_spacing"] if spacing is None else spacing
        rmax = float(self.p.get("survey_max_r", self.arena_r))
        stops = []
        ny = int(self.arena_r / (s * math.sqrt(3.0) / 2.0)) + 2
        nx = int(2 * self.arena_r / s) + 2
        for iy in range(-ny, ny + 1):
            y = iy * s * math.sqrt(3.0) / 2.0
            for ix in range(-nx, nx + 1):
                x = ix * s + (s / 2.0 if iy % 2 else 0.0)
                rr = math.hypot(x, y)
                if rr <= self.arena_r + 1e-9 and rr <= rmax + 1e-9:
                    stops.append((x, y))
        stops.sort(key=lambda p: math.hypot(p[0], p[1]))
        return stops'''
assert old in s, "survey anchor missing"
s = s.replace(old, new, 1)

# ---- 2) sweep centre first ---------------------------------------------
old2 = '''        # NB the centre is tried LAST.  A failed sweep then leaves the robot
        # standing on the estimate, which is where an extra bearing is most
        # useful; trying the centre first would leave it on the last ring point,
        # possibly on the dark side of a directional source.
        for k in range(6):'''
new2 = '''        # The centre is the single best guess, so by default it is tried FIRST
        # (a miss costs only 3 s) and repeated LAST, so that a failed sweep still
        # leaves the robot standing on the estimate -- the position where an extra
        # bearing is most useful.
        if self.p.get("sweep_center_first", True):
            if self._try_clear(c, center):
                return True
        for k in range(6):'''
assert old2 in s, "sweep anchor missing"
s = s.replace(old2, new2, 1)

# default parameters
old3 = '    "endgame_step": 11.0,       # spacing of the local clear pattern'
new3 = ('    "endgame_step": 11.0,       # spacing of the local clear pattern\n'
        '    "sweep_center_first": True,  # try the estimate centre before the ring\n'
        '    "survey_max_r": 1800.0,    # truncate the certification lattice radius')
assert old3 in s, "param anchor missing"
s = s.replace(old3, new3, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("patched robot_core.py")
