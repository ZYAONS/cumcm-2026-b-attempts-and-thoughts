# -*- coding: utf-8 -*-
"""enroute.py -- 顺路清除（本轮的第二个方向），与巡回规划混合。

时间构成（完美配置，16 例，6795 s/例 = 543 s/源）：
    probe    18.6 站   行程 11884 m（53.7%）  时间 3430 s（50.5%）
    clear    12.7 次   行程  9060 m（40.9%）  时间 2585 s（38.0%）
    localise  6.8 次   行程  2487 m（11.2%）  时间  921 s（13.6%）

清除行程已成为**最大的单项**：12.7 个源、平均每个 713 m。但清除必须走到离源
20 m 以内，所以这 9060 m 里的"必须走"部分是省不掉的——能省的是**往返的绕行**。

顺路清除的做法：扫描站位每测完一处，就检查有没有"已定位但未清除"的源落在
当前位置的 `enroute_radius` 之内；有就立刻清掉。这样源是被"顺路"处理的，
而不是等扫描结束后再专门跑一趟——省掉的正是那一趟的往返。

与巡回规划的关系（混合策略）：
  * 顺路清除处理"近在咫尺"的源（半径内，边际成本低）；
  * 巡回规划处理其余的源（按 2-opt 顺序统一安排）；
  * 两者不冲突：顺路清除只清掉那些"反正要路过"的，不会打乱远端的顺序。
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


rep('    "skip_certified": True,     # 站位附近已全部认证的频道不再测量',
    '    "enroute_clear": True,      # 顺路清除：已定位的源若就在附近，立刻清掉\n'
    '    "enroute_radius": 520.0,    # "附近"的半径（m）\n'
    '    "skip_certified": True,     # 站位附近已全部认证的频道不再测量',
    "parameter")

rep("    def _cert_open_near(self, c, pos):",
    '''    def _enroute_clear(self, radius):
        """
        顺路清除：把"已定位且就在附近"的源当场清掉。

        必须走到离源 20 m 以内才能清除，所以"接近行程"本身省不掉；
        省掉的是"从扫描路线专门拐出去再拐回来"的往返。
        radius 取得比典型站距小（默认 520 m），保证只处理真正顺路的那些，
        不会为了顺路而打乱远处源的最优顺序。
        """
        if not self.p.get("enroute_clear", True):
            return 0
        done = 0
        thresh = float(self.p.get("locate_sigma", 320.0)) * 1.732
        for c in list(self.channels):
            if self.status.get(c) in ("cleared", "empty"):
                continue
            e = self.est.get(c)
            if e is None or e[2] > thresh:
                continue
            if self._dist(self.pos, (e[0], e[1])) > radius:
                continue
            if self.clear_channel(c):
                done += 1
                # 刚清完一个，状态可能变化，重新读取位置
        return done

    def _cert_open_near(self, c, pos):''',
    "helper")

rep("""                self._commit_estimates()
                if self.p.get("periodic_cert", True):""",
    """                self._commit_estimates()
                self._enroute_clear(float(self.p.get("enroute_radius", 520.0)))
                if self.p.get("periodic_cert", True):""",
    "hook")

io.open(p, "w", encoding="utf-8").write(s)
print("en-route clearing installed")
