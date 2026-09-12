# -*- coding: utf-8 -*-
"""skip_useless_stops.py -- 如果某个普查站位附近已被完全认证，就不必去了。

上一实验暴露的缺口：途中测量确实积累了信息（检测 452→618），
但 `_pending_stops` 仍然把预规划的全部站位排进任务表，于是**白跑**。

判定是严格的（不是启发式）：
    对某个待访站位 p，若在其认证半径 R 之内的**每一个候选网格点**，
    对**每一个尚未认证的频道**都已被排除，那么：
      * 那里不可能藏有源 -> 去 p 做"发现"没有意义；
      * 认证也不再需要 p 的读数。
    因此 p 可以直接跳过。

这正是"发现"与"认证"合一的判据——此前的 skip_certified 只在**频道**层面判断，
几乎不触发；换成**站位**层面判断，只有整个邻域都认证完了才会跳过，
触发条件合理得多。
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


rep('    "leg_probe_step": 0.0,      # 长距离移动的分段长度（m）；>0 时途中顺带测量',
    '    "skip_useless_stops": True,  # 邻域已被完全认证的普查站位直接跳过\n'
    '    "leg_probe_step": 0.0,      # 长距离移动的分段长度（m）；>0 时途中顺带测量',
    "parameter")

rep("    def _pending_stops(self):",
    '''    def _stop_is_useless(self, p):
        """
        True when p no longer needs a visit: every certification candidate within
        the certification radius of p is already ruled out for every channel that
        has not been certified yet.

        Then no source can hide there (so the visit would discover nothing) and the
        certificate does not need p's readings either.
        """
        if not self.p.get("skip_useless_stops", True):
            return False
        ruled_map = getattr(self, "_cert_ruled", None)
        if not ruled_map:
            return False
        open_ch = [c for c in self.channels
                   if self.status.get(c) not in ("cleared", "empty")
                   and not self.obs.get(c)]
        if not open_ch:
            return True
        R = self.p["verify_r"] - self.p["verify_grid"] * 0.7072
        R2 = R * R
        grid = self._verify_grid()
        for gi, q in enumerate(grid):
            dx, dy = q[0] - p[0], q[1] - p[1]
            if dx * dx + dy * dy > R2:
                continue
            for c in open_ch:
                if gi not in ruled_map.get(c, ()):
                    return False
        return True

    def _pending_stops(self):''',
    "helper")

rep("""        out = []
        for p in self._primary_stops():""",
    """        out = []
        for p in self._primary_stops():
            if self._stop_is_useless(p):
                continue""",
    "skip in pending")

io.open(p, "w", encoding="utf-8").write(s)
print("useless-stop skipping installed")
