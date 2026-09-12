# -*- coding: utf-8 -*-
"""exhaustive_clear.py -- 末段最后手段：在 σ 圆盘上做栅格穷举清除。

诊断（pool C / seed 12010 / ch12）：
    源在 r=1799（紧贴边界）、定向、朝向 165°；
    机器人已经把它**定位到 σ=42 m**（obs=38），但 attempts=2、total=14，
    **用尽了 hard_attempt_cap=14**，于是再也不会生成清除任务，源被漏掉。

为什么 14 次都没清掉？末段图案的半径取 0.55σ ≈ 23 m，两圈分别是 23 m 与 46 m，
而清除半径是 20 m——图案点之间的空隙可能整片落在 20 m 之外。

修法：加一个**有保证的兜底**——当估计已经足够好（σ 不超过定位门槛）而常规
末段图案连续失败 k 次时，在 σ 圆盘上做间距不超过 15 m 的**栅格穷举清除**。
间距 15 m 时任何半径 42 m 的圆盘内任一点都在某个栅格点 11 m 以内
（15/√2 ≈ 10.6 m < 20 m），因此**只要 σ 确实覆盖真值，就一定能清掉**。
代价：最坏 ~25 点 × 3 s = 75 s，只在最后手段触发。
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


rep('    "relocate": True,           # 单条方位的频道：横向偏移二分 + 沿射线爬行',
    '    "exhaustive_clear": True,   # 末段兜底：σ 圆盘上栅格穷举清除\n'
    '    "exhaustive_grid": 15.0,    # 栅格间距（m）；15/√2 = 10.6 < 20 m 保证覆盖\n'
    '    "exhaustive_after": 2,      # 常规末段连续失败几次后启用\n'
    '    "exhaustive_cap": 80,       # 单次穷举的清除动作上限\n'
    '    "relocate": True,           # 单条方位的频道：横向偏移二分 + 沿射线爬行',
    "parameter")

rep("    def _bracket_clear(self, c, p_from, p_to):",
    '''    def _exhaustive_clear(self, c, center, sigma):
        """
        在 σ 圆盘上按 <=15 m 间距穷举清除。

        这是"有保证"的兜底：间距 g 的方形栅格中，圆盘内任一点到最近栅格点
        不超过 g/sqrt(2)。取 g=15 m 得 10.6 m < 20 m 的清除半径，
        因此只要真值落在 σ 圆盘内（由问题一的定位区域保证），必定命中。
        """
        g = float(self.p.get("exhaustive_grid", 15.0))
        cap = int(self.p.get("exhaustive_cap", 80))
        rad = max(sigma, 20.0)
        n = int(rad / g) + 1
        tried = 0
        pts = []
        for iy in range(-n, n + 1):
            for ix in range(-n, n + 1):
                dx, dy = ix * g, iy * g
                if dx * dx + dy * dy > rad * rad:
                    continue
                pts.append((dx * dx + dy * dy, center[0] + dx, center[1] + dy))
        pts.sort()                      # 从中心向外，先试最可能的
        for _, q in pts:
            if tried >= cap:
                break
            tried += 1
            if self._try_clear(c, q):
                return True
        return False

    def _bracket_clear(self, c, p_from, p_to):''',
    "helper")

# 在末段图案失败后、且常规尝试已失败若干次时启用
rep("""            if d <= self.p["endgame_radius"]:
                if self._local_clear_sweep(c, est[:2], sigma=est[2]):
                    return True""",
    """            if d <= self.p["endgame_radius"]:
                if self._local_clear_sweep(c, est[:2], sigma=est[2]):
                    return True
                # 兜底：常规图案连续失败后，在 σ 圆盘上做有保证的栅格穷举
                if (self.p.get("exhaustive_clear", True)
                        and self.attempts.get(c, 0) >= int(
                            self.p.get("exhaustive_after", 2))
                        and self._exhaustive_clear(c, est[:2], est[2])):
                    return True""",
    "endgame hook")

# 不再因为 hard cap 而彻底放弃一个已定位的源：把 cap 提高，交由穷举兜底保证收敛
rep('    "hard_attempt_cap": 14,     # absolute cap of clear attempts per channel',
    '    "hard_attempt_cap": 24,     # absolute cap of clear attempts per channel\n'
    '                                # (raised: the exhaustive fallback now\n'
    '                                #  guarantees convergence on located sources)',
    "hard cap")

io.open(p, "w", encoding="utf-8").write(s)
print("exhaustive terminal clear installed")
