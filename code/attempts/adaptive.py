# -*- coding: utf-8 -*-
"""adaptive.py -- 结构性改动：取消固定格点，让认证驱动采样。

现状与问题
----------
当前流程是"先按固定格点扫 18.6 个站位，再清除"，其中：
    探测行程 11884 m（2377 s）   <- 固定格点造成的"必走"
    清除行程  9060 m（1812 s）   <- 走到 13 个源，**这部分无论如何都要走**

而清除巡回本身就把机器人带到了目标域各处（13 个源分布在全域），
**这条路必须走，却没有被用来做测量覆盖**。

新结构：自适应采样
------------------
取消固定格点（survey_mode = "adaptive"），改为：
  1. 入场普查（原点，20 次检测）——找出所有"朝向中心"的源；
  2. 机器人走向清除目标，**沿途按 probe_spacing 持续测量**，
     这些读数既服务于发现，也服务于认证；
  3. 当没有可清除的目标时，由**认证扫描**指出"证书最弱的候选点"，
     在那里补一个站位——即"哪里还不确定就去哪里"；
  4. 采样与清除交替进行，直到全部清完且全部认证。

与旧结构的本质差别：旧结构"先盲目扫完再干活"，
新结构**每一步都由信息缺口驱动**，且把"必须走的清除行程"
转化为测量覆盖。站位不再是固定的 18.6 个，而是"认证需要多少就补多少"。

配套改动：next_search_batch 一次给出若干个候选站位，
让巡回规划（2-opt）能在它们之间排序，而不是一个一个地贪心跳。
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


# ---- 参数 ----------------------------------------------------------------
rep('    "rim_ring_n": 0,            # 贴边环：在 r=rim_ring_r 上补 n 个站位，',
    '    "adaptive_batch": 4,        # 自适应采样一次取几个候选站位交给巡回规划\n'
    '    "rim_ring_n": 0,            # 贴边环：在 r=rim_ring_r 上补 n 个站位，',
    "parameter")

# ---- 无固定格点 ----------------------------------------------------------
rep('        if self.p.get("survey_mode", "ring") == "lattice":\n'
    '            if not getattr(self, "_rim_done", False):',
    '        if self.p.get("survey_mode") == "adaptive":\n'
    '            # 自适应：不预置任何站位，全部由认证扫描按需给出\n'
    '            return []\n'
    '        if self.p.get("survey_mode", "ring") == "lattice":\n'
    '            if not getattr(self, "_rim_done", False):',
    "no lattice")

# ---- 一次给出多个候选站位 ------------------------------------------------
rep("    def _rim_patrol_stops(self, uncov):",
    '''    def next_search_batch(self, unresolved, k):
        """
        一次给出至多 k 个"认证最需要"的站位。

        单个站位交给巡回规划没有意义（只有一个点时无所谓顺序）；
        一批站位才能让 2-opt 在它们之间排出好路线。
        贪心地反复调用 next_search_stop，并把已选中的点临时视作已访问，
        以免一批里出现重复位置。
        """
        out = []
        for _ in range(max(int(k), 1)):
            stop, flags = self.next_search_stop(unresolved)
            if stop is None:
                break
            key = (round(stop[0], 1), round(stop[1], 1))
            if key in self.visited_stops:
                break
            self.visited_stops.add(key)          # 临时占位，避免重复
            out.append(stop)
        return out

    def _rim_patrol_stops(self, uncov):''',
    "batch helper")

# ---- 在 _run_planned 里使用批量 ------------------------------------------
rep("""                stop, flags = self.next_search_stop(unresolved)""",
    """                if self.p.get("survey_mode") == "adaptive":
                    stops = self.next_search_batch(
                        unresolved, int(self.p.get("adaptive_batch", 4)))
                    stop = stops[0] if stops else None
                    if stops:
                        tour = [("stop", None, q) for q in stops[1:]]
                else:
                    stop, flags = self.next_search_stop(unresolved)""",
    "batch in loop")

io.open(p, "w", encoding="utf-8").write(s)
print("adaptive sampling installed")
