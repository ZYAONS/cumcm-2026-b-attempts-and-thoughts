# -*- coding: utf-8 -*-
"""skip_certified.py -- 减少每站检测频道数：站位附近已全部认证的频道不再测。

逻辑（可证明的，不是启发式）：
    对一个"从未听到过"的频道 c，在某站位 p 处测一次的全部价值，
    在于为 p 附近尚未认证的候选点提供一条读数。
    如果 p 的认证半径 R 之内的**每一个候选点都已经被判定排除**，
    那么在该处测量 c 就不会改变任何结论——不测。

判定用认证扫描已经维护好的增量结构 `_cert_ruled[c]`（已排除的网格点索引集合），
只需检查"p 的 R 邻域内是否还有未排除的网格点"。这件事是 O(邻域点数)，
而邻域点数约为 πR²/verify_grid² ≈ 800，相对于一次 6 s 的检测可以忽略。

注意这不是"猜"：认证扫描本身是精确的（原点在读数凸包内部），
所以"附近全部已认证"意味着那里确实不可能有源，测了也没有信息量。
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


rep('    "exhaustive_clear": True,   # 末段兜底：σ 圆盘上栅格穷举清除',
    '    "skip_certified": True,     # 站位附近已全部认证的频道不再测量\n'
    '    "exhaustive_clear": True,   # 末段兜底：σ 圆盘上栅格穷举清除',
    "parameter")

rep("    def _exhaustive_clear(self, c, center, sigma):",
    '''    def _cert_open_near(self, c, pos):
        """
        pos 的认证半径邻域内是否还有"尚未被排除"的候选点。

        返回 False 表示该处对频道 c 已无信息量（测了也不会改变任何结论）。
        """
        ruled = self._cert_ruled.get(c) if getattr(self, "_cert_ruled", None) else None
        if ruled is None:
            return True                      # 认证结构尚未建立：保守地测
        R = self.p["verify_r"] - self.p["verify_grid"] * 0.7072
        R2 = R * R
        for gi, q in enumerate(self._verify_grid()):
            dx, dy = q[0] - pos[0], q[1] - pos[1]
            if dx * dx + dy * dy > R2:
                continue
            if gi not in ruled:
                return True
        return False

    def _exhaustive_clear(self, c, center, sigma):''',
    "helper")

rep("""        if self.status[c] == "unknown":
            return True""",
    """        if self.status[c] == "unknown":
            if (self.p.get("skip_certified", True)
                    and not self._cert_open_near(c, pos)):
                # 该站位附近已被完全认证：此处不可能有源，测了没有信息量
                return False
            return True""",
    "skip rule")

io.open(p, "w", encoding="utf-8").write(s)
print("skip-certified rule installed")
