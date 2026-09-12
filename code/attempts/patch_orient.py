# -*- coding: utf-8 -*-
"""patch_orient.py -- 独立设计的改进：定向源朝向可行集（orientation feasible set）。

与公开实现的差别：对方用"朝向的贝叶斯信念"，这里用**硬约束可行集**，与本文
"定位区域 = 硬约束交集"的建模口径一致，不引入概率假设。

原理
----
设频道 c 的源位置估计为 p、朝向为 u（单位向量，指向辐射方向）。
在检测点 q 处收到 no_signal，且 |q - p| <= R_min = 1000 时，唯一可能的解释是
"q 落在源的背向半平面"，即

        (q - p) . u < 0                                        (1)

于是 no_signal 不是"没有信息"，而是对朝向的一个半平面约束。把所有这类约束累积起来，
得到朝向的可行角区间 F_c。当末段归航因为在背向侧丢失信号时，不必盲目退回上一个听到
信号的点，而是可以**主动走到源的前向侧** p + L*u_hat（u_hat 取 F_c 的代表方向），
在那里源一定处于受光半平面内。

实现
----
* F_c 用 24 个 15 度分箱表示，初值全可行；
* 每得到一条满足 (1) 前条件的 no_signal，就删掉与 (q-p) 夹角 < 90 度的分箱；
* `_front_point(c)` 返回 p + L*u_hat（u_hat 为幸存分箱的角平分线方向，取离当前
  位置最近的一侧），只在末段 lost 时作为**首选**回退点。
参数 `orient_belief`（默认 False）控制开关，便于两池对照后才决定是否采纳。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

# ---- 1) 参数 -------------------------------------------------------------
anchor = '    "sweep_center_first": True,  # try the estimate centre before the ring'
if anchor not in s:
    print("!! 参数锚点未找到")
    sys.exit(1)
s = s.replace(anchor, anchor + '\n'
              '    "orient_belief": False,    # 定向源朝向硬约束可行集（自主设计的改进）\n'
              '    "orient_bins": 24,         # 朝向分箱数（24 = 每箱 15 度）\n'
              '    "orient_len": 350.0,       # 前向侧取数点的距离', 1)

# ---- 2) 状态初始化 -------------------------------------------------------
anchor2 = "        self.meas_cache = {}"
if anchor2 not in s:
    print("!! 状态锚点未找到")
    sys.exit(1)
s = s.replace(anchor2, anchor2 + "\n"
              "        nb = int(self.p.get(\"orient_bins\", 24) or 24)\n"
              "        # 朝向可行集：每个频道一组仍可行的朝向分箱\n"
              "        self.orient_ok = dict((c, set(range(nb))) for c in self.channels)",
              1)

# ---- 3) 方法：约束更新 + 前向侧取数点 -------------------------------------
anchor3 = "    def _retreat(self, c):"
if anchor3 not in s:
    print("!! _retreat 锚点未找到")
    sys.exit(1)
new_methods = '''    # ---------------------------------------------------- orientation belief
    def _orient_update(self, c, q):
        """
        把一次 no_signal 转成对朝向的半平面约束 (q-p).u < 0，更新可行分箱。
        仅当估计位置与检测点距离不超过 R_min 时该约束才成立（否则可能只是超距）。
        """
        if not self.p.get("orient_belief", False):
            return
        est = self.est.get(c)
        if est is None:
            return
        dx, dy = q[0] - est[0], q[1] - est[1]
        d = math.hypot(dx, dy)
        if d < 1e-6 or d > float(self.p["verify_r"]):
            return
        nb = int(self.p.get("orient_bins", 24) or 24)
        ok = self.orient_ok.get(c)
        if not ok:
            return
        # 可行朝向必须指向背离 q 的一侧，即与 (q-p) 的夹角 > 90 度
        keep = set()
        for b in ok:
            ang = 2.0 * math.pi * (b + 0.5) / nb
            if math.cos(ang) * dx + math.sin(ang) * dy < 0.0:
                keep.add(b)
        self.orient_ok[c] = keep

    def _orient_front(self, c):
        """
        返回"源的前向侧"取数点：p + L*u_hat。u_hat 取所有幸存分箱中最靠近当前
        位置的方向（这样移动距离最短）。可行集为空时退回 None。
        """
        est = self.est.get(c)
        ok = self.orient_ok.get(c)
        if est is None or not ok:
            return None
        nb = int(self.p.get("orient_bins", 24) or 24)
        L = float(self.p.get("orient_len", 350.0))
        best = None
        for b in ok:
            ang = 2.0 * math.pi * (b + 0.5) / nb
            pt = (est[0] + L * math.cos(ang), est[1] + L * math.sin(ang))
            d = self._dist(self.pos, pt)
            if best is None or d < best[0]:
                best = (d, pt)
        if best is None:
            return None
        return self._clip_to_arena(best[1])

'''
s = s.replace(anchor3, new_methods + anchor3, 1)

# ---- 4) no_signal 时更新朝向约束 ------------------------------------------
old_ns = """                if res.get("measure_result") == "no_signal":
                    if not self._retreat(c):
                        return False
                    continue"""
if old_ns not in s:
    print("!! no_signal 锚点未找到（clear_channel 内）")
    sys.exit(1)
s = s.replace(old_ns, """                if res.get("measure_result") == "no_signal":
                    self._orient_update(c, self.pos)
                    if not self._retreat(c):
                        return False
                    continue""", 1)

# 行走后收到 no_signal 的分支同样更新
old_ns2 = """            else:
                step_scale *= 0.45
                if self.p.get("bracket_clear", True) and self._bracket_clear(c, self.last_seen[c], tgt):
                    return True"""
if old_ns2 not in s:
    print("!! 行走分支锚点未找到")
    sys.exit(1)
s = s.replace(old_ns2, """            else:
                self._orient_update(c, tgt)
                step_scale *= 0.45
                if self.p.get("bracket_clear", True) and self._bracket_clear(c, self.last_seen[c], tgt):
                    return True""", 1)

# ---- 5) _retreat 优先走前向侧 ---------------------------------------------
old_ret = """        seen = self.last_seen.get(c)
        if seen is None:
            return False"""
if old_ret not in s:
    print("!! retreat 内部锚点未找到")
    sys.exit(1)
s = s.replace(old_ret, """        seen = self.last_seen.get(c)
        if self.p.get("orient_belief", False):
            # 自主设计的改法：背向丢失时主动绕到源的前向侧，而不是退回去
            front = self._orient_front(c)
            if front is not None and self._dist(self.pos, front) > 2.0:
                r = self.hear(c, front)
                if r.get("measure_result") in ("direction", "near"):
                    return True
        if seen is None:
            return False""", 1)

io.open(p, "w", encoding="utf-8").write(s)
print("orient_belief 已植入 robot_core.py")
