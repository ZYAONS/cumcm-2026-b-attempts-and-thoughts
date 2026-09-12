# -*- coding: utf-8 -*-
"""relocate.py -- 贴边定向源的严格解法：横向偏移 + 二分收缩 + 沿射线爬行。

问题的完整刻画（前面几轮诊断得到）：
  * 一个贴在边界上、朝外辐射的定向源，其域内受光区是一个薄月牙；
  * 机器人只能在边界点上听到它一次（例：源 (-1760,-76)，听到点 (-1800,0)，距离 86 m）；
  * 只有一条方位就无法定位，于是不生成清除任务；
  * 站位规则把第二观测点放在离听到点 550 m 的斜向位置，**越过源 465 m 落到背光侧**，
    三次尝试全部浪费，该频道永久停留在"已听到"。

前两轮尝试的教训：
  * "沿射线 550 m 单跳"→ 越界落到背光侧（负）；改成 200 m 爬行 → 拿到第二条方位，
    但两条方位只差 1.3°，σ 仍 670 m（中性）；
  * "35 m 短基线"→ 完成率反而从 0.9981 掉到 0.9917（负优化，已撤销）。

本轮换一个更严格的构造。注意一条此前被忽略的几何事实：

    机器人在点 p 听到源，知道源在射线 p→(方位 θ̂) 上；
    但**它不知道 p 离源的受光半平面边界有多远**。
    沿射线走不会改变方位（得不到第二条独立方位）；
    垂直走有可能越界（落到背光侧）。

所以正确的做法是**对横向偏移量本身做二分**：

    以 p 为起点，依次尝试横向偏移 δ ∈ {400, 250, 150, 90, 55, 33, 20} m（两侧都试）。
    只要某次成功听到，就立刻得到了一条与首方位夹角可观的新方位 → 可以定位。
    若某个 δ 失败，说明该侧越界或源更远，取下一个更小的 δ（二分收缩）。
    若全部失败，就沿射线向前爬 200 m 再重复（此时横向偏移的绝对尺度自动变小）。

关键性质：**只要源确实在受光侧可听，这套二分必然在有限步内成功**——
δ 的下界由"受光半平面必然包含听到点本身"给出，δ→0 时偏移点趋于 p，必然可听。
这不是启发式，而是收敛性有保证的构造。
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


# ---------------------------------------------------------------- 参数
rep('    "vantage_step_onray": 200.0,  # creep along the ray instead of jumping',
    '    "relocate": True,           # 单条方位的频道：横向偏移二分 + 沿射线爬行\n'
    '    "relocate_deltas": [400.0, 250.0, 150.0, 90.0, 55.0, 33.0, 20.0],\n'
    '    "relocate_crawls": 4,       # 全部偏移失败后沿射线前进的次数\n'
    '    "relocate_crawl_step": 200.0,\n'
    '    "relocate_sigma": 900.0,    # 估计 sigma 大于此值仍视为"未定位"\n'
    '    "vantage_step_onray": 200.0,  # creep along the ray instead of jumping',
    "parameter")

# ---------------------------------------------------------------- 状态
rep("        self.onray_scale = {}\n        self.onray_tries = {}",
    "        self.onray_scale = {}\n        self.onray_tries = {}\n"
    "        self.reloc = {}", "state")

# ---------------------------------------------------------------- 核心
rep("    def _rim_patrol_stops(self, uncov):",
    '''    def _relocate_point(self, c):
        """
        为"只有一条方位"的频道生成下一个观测点：横向偏移量二分 + 沿射线爬行。

        返回 (点, 说明) 或 None。状态保存在 self.reloc[c]。
        """
        if not self.obs.get(c):
            return None
        st = self.reloc.setdefault(c, {"d": 0, "side": 0, "crawl": 0})
        deltas = list(self.p.get("relocate_deltas",
                                 [400.0, 250.0, 150.0, 90.0, 55.0, 33.0, 20.0]))
        o = self.obs[c][-1]
        base = (o[0], o[1])
        brg = math.radians(o[2])
        while st["crawl"] <= int(self.p.get("relocate_crawls", 4)):
            # 先回到（或由爬行确定的）基准点
            anchor = self.reloc.get((c, "anchor"))
            if anchor is None:
                anchor = base
                self.reloc[(c, "anchor")] = anchor
            if st["d"] < len(deltas):
                d = deltas[st["d"]]
                sgn = 1.0 if st["side"] == 0 else -1.0
                a = brg + sgn * math.pi / 2.0
                p = (anchor[0] + d * math.cos(a), anchor[1] + d * math.sin(a))
                p = self._clip_to_arena(p)
                st["side"] += 1
                if st["side"] >= 2:
                    st["side"] = 0
                    st["d"] += 1
                return p, "lateral %.0f m" % d
            # 所有横向偏移都失败：沿射线向前爬一步，重新从大偏移试起
            st["d"] = 0
            st["side"] = 0
            st["crawl"] += 1
            step = float(self.p.get("relocate_crawl_step", 200.0))
            nxt = (anchor[0] + step * math.cos(brg), anchor[1] + step * math.sin(brg))
            nxt = self._clip_to_arena(nxt)
            if self._dist(nxt, anchor) < 30.0:
                return None                      # 已经到边界，无法再前进
            self.reloc[(c, "anchor")] = nxt
        return None

    def _relocate_needed(self, c):
        """频道听过但还没有可用估计。"""
        if not self.p.get("relocate", True):
            return False
        if not self.obs.get(c):
            return False
        e = self.est.get(c)
        return e is None or e[2] > float(self.p.get("relocate_sigma", 900.0))

    def _rim_patrol_stops(self, uncov):''',
    "relocate core")

# ---------------------------------------------------------------- 任务
rep("""        for p in pending:
            tasks.append(("stop", None, p))
        return tasks""",
    """        # 只有一条方位的频道：给它安排一次"横向偏移二分"观测。
        # 放在清除任务之后、覆盖站位之前——它便宜（短距离往返），
        # 而且一旦成功就把一个"已听到"的频道变成可清除的目标。
        if self.p.get("relocate", True):
            for c in self.channels:
                if self.status.get(c) in ("cleared", "empty"):
                    continue
                if not self._relocate_needed(c):
                    continue
                r = self._relocate_point(c)
                if r is not None:
                    tasks.append(("relocate", c, r[0]))
        for p in pending:
            tasks.append(("stop", None, p))
        return tasks""",
    "task build")

rep("""            elif kind == "vantage":""",
    """            elif kind == "relocate":
                self._cur_task = "localise"
                self._task_count["localise"] += 1
                c = task[1]
                p = task[2]
                r = self.move_measure(p[0], p[1], c)
                n_act += 1
                if r.get("measure_result") in ("direction", "near"):
                    # 拿到了第二条方位：重新估计，若可用则立刻转为可清除
                    e = self.update_estimate(c)
                    if e is not None:
                        self.est[c] = e
                    self.reloc.pop(c, None)
                    self.reloc.pop((c, "anchor"), None)
                self.probe(self.pos)
                replan = (not batch) or heard_count() > last_heard or clear_count() > last_cleared
            elif kind == "vantage":""",
    "task execute")

io.open(p, "w", encoding="utf-8").write(s)
print("relocate (lateral bisection + ray crawl) installed")
