# -*- coding: utf-8 -*-
"""fix_relocate_state.py -- 状态机必须在"任务被执行"时推进，而不是在"任务被生成"时。

诊断（seed 100006 / ch2）：
    最终观测仍只有两条、且是旧的"沿射线爬行"那一对（相距 36 m、方位只差 1.3°），
    两楔之交**无界**（bounded=False），因此 estimate 不可用，永远不生成清除任务。
    而 relocate 生成的 6 个候选点里有 3 个是"受光且距源 40~90 m"的优质观测点，
    却**一个都没有被访问**。

原因：`_relocate_point()` 在**构建任务列表**时就执行 `st["d"] += 1`，
而 `_build_tasks()` 在每次重规划（即每个动作之后）都会被调用。
于是状态机在没有访问任何点的情况下就推进完了，任务列表里每次看到的都是"下一个"候选，
而机器人每次只执行第一个任务 → 候选点被不断丢弃。

修法：
  * `_relocate_point()` 改为**纯查询**：只返回当前状态对应的候选点，不改变状态；
  * 状态在**任务执行完**之后推进（横向偏移：先换边、再放大 δ；都试完则沿射线爬行一步）；
  * 同时让 `vantage` 路径**避让**这些频道（relocate 才是为它们设计的机制）。
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


start = s.index("    def _relocate_point(self, c):")
end = s.index("    def _relocate_needed(self, c):")
new = '''    def _relocate_point(self, c):
        """
        为"只有一条方位"的频道给出**当前**候选观测点（纯查询，不改变状态）。

        状态机：按位于 self.reloc[c] 的 (d, side, crawl) 给出候选点；
        推进由 `_relocate_advance()` 在任务执行之后完成。
        """
        if not self.obs.get(c):
            return None
        st = self.reloc.setdefault(c, {"d": 0, "side": 0, "crawl": 0})
        deltas = list(self.p.get("relocate_deltas",
                                 [400.0, 250.0, 150.0, 90.0, 55.0, 33.0, 20.0]))
        if st["d"] >= len(deltas):
            return None
        o = self.obs[c][-1]
        anchor = self.reloc.get((c, "anchor"), (o[0], o[1]))
        brg = math.radians(o[2])
        d = deltas[st["d"]]
        sgn = 1.0 if st["side"] == 0 else -1.0
        a = brg + sgn * math.pi / 2.0
        q = self._clip_to_arena((anchor[0] + d * math.cos(a),
                                 anchor[1] + d * math.sin(a)))
        return q, "lateral %.0f m" % d

    def _relocate_advance(self, c):
        """任务执行之后推进状态：先换边，再放大 δ；都试完则沿射线爬行一步。"""
        st = self.reloc.setdefault(c, {"d": 0, "side": 0, "crawl": 0})
        deltas = list(self.p.get("relocate_deltas",
                                 [400.0, 250.0, 150.0, 90.0, 55.0, 33.0, 20.0]))
        if st["side"] == 0:
            st["side"] = 1
            return
        st["side"] = 0
        st["d"] += 1
        if st["d"] < len(deltas):
            return
        # 所有横向偏移都失败：沿射线前进，重新从最大偏移试起
        st["d"] = 0
        st["crawl"] += 1
        if st["crawl"] > int(self.p.get("relocate_crawls", 4)):
            return
        o = self.obs[c][-1]
        anchor = self.reloc.get((c, "anchor"), (o[0], o[1]))
        step = float(self.p.get("relocate_crawl_step", 200.0))
        brg = math.radians(o[2])
        nxt = self._clip_to_arena((anchor[0] + step * math.cos(brg),
                                   anchor[1] + step * math.sin(brg)))
        if self._dist(nxt, anchor) > 30.0:
            self.reloc[(c, "anchor")] = nxt

'''
s = s[:start] + new + s[end:]
print("  ok: relocate core rewritten")

# 执行器：测量之后推进状态
rep("""                if r.get("measure_result") in ("direction", "near"):
                    # 拿到了第二条方位：重新估计，若可用则立刻转为可清除
                    e = self.update_estimate(c)
                    if e is not None:
                        self.est[c] = e
                    self.reloc.pop(c, None)
                    self.reloc.pop((c, "anchor"), None)""",
    """                if r.get("measure_result") in ("direction", "near"):
                    # 拿到了第二条方位：重新估计，若可用则立刻转为可清除
                    e = self.update_estimate(c)
                    if e is not None:
                        self.est[c] = e
                    self.reloc.pop(c, None)
                    self.reloc.pop((c, "anchor"), None)
                else:
                    self._relocate_advance(c)""",
    "executor advance")

# vantage 避让 relocate 频道
rep("""                if len(self.obs[c]) < 1:
                    continue
                if (self.vantage_tries.get(c, 0) >= self.p["vantage_max_tries"]""",
    """                if len(self.obs[c]) < 1:
                    continue
                if self._relocate_needed(c):
                    continue          # 由 relocate 机制负责，不用旧的斜向站位
                if (self.vantage_tries.get(c, 0) >= self.p["vantage_max_tries"]""",
    "vantage avoidance")

io.open(p, "w", encoding="utf-8").write(s)
print("relocate state machine fixed")
