# -*- coding: utf-8 -*-
"""better_oropt.py -- 用 O(1) 增量的 Or-opt 优化**整条**巡回。

诊断
----
实测：站位数 24.4 -> 14.9（rim0），行程几乎不变（23323 -> 23498 m）。
也就是说**行程不是站位数造成的**。而
    13 个源的 TSP             8635 m
    12.9 个格点站位的 TSP     ~6000 m
    合并成一条巡回            ~11000 m
实际却走了 23000 m —— **是合并 TSP 的两倍**。

原因：`_plan_tour` 在每个任务执行后重建序列，用"最近邻 + 带优先偏置的距离"，
最近邻本身比 2-opt 差 10~20%，再加上 clear_bonus=500 对距离的扭曲，
合并巡回的质量进一步下降。

原有的 Or-opt 只作用于序列**前 12 个任务**（`oropt_limit`），
因为每次重规划都要调用它。本补丁把 Or-opt 改成 **O(1) 增量的整序列版本**：
段（长度 1~3）的移除增益与插入代价都只需常数次距离计算，
因此即使作用在全部 37 个任务上，单次重规划仍是毫秒级。

段移除增益： d(prev,first) + d(last,next) - d(prev,next)
插入代价：   d(order[k],first) + d(last,order[k+1]) - d(order[k],order[k+1])
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

start = s.index("        # Or-opt: relocate segments of one to three tasks.")
end = s.index("        return [tasks[i] for i in order]")
new = '''        # Or-opt over the WHOLE tour, with O(1) move evaluation.
        #
        # The plan is rebuilt after every executed task, so this has to stay
        # cheap; the constant-time delta below is what makes a full-tour Or-opt
        # affordable (the previous version only improved the first few tasks).
        def seg_delta(seq, i, j, k):
            """delta of moving seq[i:j+1] to just after position k"""
            n = len(seq)
            prev = start if i == 0 else pos[seq[i - 1]]
            first = pos[seq[i]]
            last = pos[seq[j]]
            nxt = pos[seq[j + 1]] if j + 1 < n else None
            gain = self._dist(prev, first)
            if nxt is not None:
                gain += self._dist(last, nxt) - self._dist(prev, nxt)
            else:
                gain += 0.0                       # open tour: nothing after
            if k < 0:
                a = start
                b = pos[seq[0]]
            else:
                a = pos[seq[k]]
                b = pos[seq[k + 1]] if k + 1 < n else None
            cost = self._dist(a, first)
            if b is not None:
                cost += self._dist(last, b) - self._dist(a, b)
            return cost - gain

        limit = int(self.p.get("oropt_limit_batch", 60))
        if self.p.get("replan_mode") == "each":
            limit = int(self.p.get("oropt_limit_full", 60))
        rounds = 0
        improved = True
        while improved and rounds < 12 and len(order) > 4:
            improved = False
            rounds += 1
            n = len(order)
            for L in (3, 2, 1):
                for i in range(n - L + 1):
                    if i >= limit:
                        break
                    j = i + L - 1
                    for k in range(-1, n - L):
                        if i <= k + 1 <= j:
                            continue
                        if seg_delta(order, i, j, k) < -1e-9:
                            seg = order[i:j + 1]
                            rest = order[:i] + order[j + 1:]
                            at = k + 1 if k < i else k + 1 - L
                            order = rest[:at] + seg + rest[at:]
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
'''
s = s[:start] + new + s[end:]
io.open(p, "w", encoding="utf-8").write(s)
print("full-tour O(1) Or-opt installed")
