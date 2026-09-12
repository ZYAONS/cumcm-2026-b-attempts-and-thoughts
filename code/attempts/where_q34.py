# -*- coding: utf-8 -*-
"""where_q4.py -- 用当前最优配置跑问题四，打印行程/检测/清除的精确分解。

用法: python where_q4.py [n_cases] [seed0]
"""
import json
import os
import random
import statistics
import sys

import robot_core as rc

MODE = os.environ.get('MODE', 'q4')
import simulator as sim
from make_data import P3, P4

HERE = os.path.dirname(os.path.abspath(__file__))


def run_case(seed, params):
    srcs = sim.make_case(random.Random(seed), kind_mix=(0.0 if MODE == 'q3' else 0.5))
    arena = sim.Arena(srcs, seed=seed)
    cl = rc.LocalClient(arena)
    brain = rc.Brain(cl, params=params, seed=seed)
    # 记录每个任务的起止点，便于算 2-opt 下界
    legs = []
    orig_m, orig_c = brain.move_measure, brain.move_clear
    last = [brain.pos]

    def m2(x, y, c):
        r = orig_m(x, y, c)
        legs.append((brain._cur_task, last[0], (x, y)))
        last[0] = (x, y)
        return r

    def c2(x, y, c):
        r = orig_c(x, y, c)
        legs.append(("clear", last[0], (x, y)))
        last[0] = (x, y)
        return r
    brain.move_measure, brain.move_clear = m2, c2
    st = brain.run()
    st.update(arena.stats())
    st["legs"] = legs
    st["task_travel"] = dict(brain._task_travel)
    st["task_count"] = dict(brain._task_count)
    st["n_stops"] = len(brain.visited_stops)
    # 访问过的"计划点"集合（覆盖站位 + 清除目标）
    pts = set()
    for kind, a, b in legs:
        pts.add((round(b[0], 1), round(b[1], 1)))
    st["n_pts"] = len(pts)
    st["src_pos"] = [(round(s.x, 1), round(s.y, 1)) for s in srcs]
    arena.close()
    return st


def two_opt_len(points):
    """开放巡回（从原点出发）的最近邻 + 2-opt 长度，作为该点集的行程下界参考"""
    pts = list(points)
    if not pts:
        return 0.0
    import math
    cur = (0.0, 0.0)
    order = []
    rem = set(range(len(pts)))
    while rem:
        i = min(rem, key=lambda j: math.dist(cur, pts[j]))
        order.append(i)
        rem.discard(i)
        cur = pts[i]
    pos = [pts[i] for i in order]
    def L(o):
        d = math.dist((0.0, 0.0), o[0])
        for a, b in zip(o, o[1:]):
            d += math.dist(a, b)
        return d
    improved = True
    guard = 0
    while improved and guard < 8:
        improved = False
        guard += 1
        for i in range(len(pos) - 1):
            for j in range(i + 1, len(pos)):
                a = (0.0, 0.0) if i == 0 else pos[i - 1]
                b, c = pos[i], pos[j]
                d = pos[j + 1] if j + 1 < len(pos) else None
                old = math.dist(a, b) + (math.dist(c, d) if d else 0)
                new = math.dist(a, c) + (math.dist(b, d) if d else 0)
                if new < old - 1e-9:
                    pos[i:j + 1] = pos[i:j + 1][::-1]
                    improved = True
    return L(pos)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P3 if MODE == 'q3' else P4)
    rows = []
    for k in range(n):
        st = run_case(seed0 + k, p)
        rows.append(st)
    tt = {}
    for k in ("clear", "localise", "probe", "census"):
        tt[k] = statistics.mean(r["task_travel"].get(k, 0.0) for r in rows)
    cnt = {}
    for k in ("clear", "localise", "probe", "census"):
        cnt[k] = statistics.mean(r["task_count"].get(k, 0.0) for r in rows)
    nsrc = statistics.mean(r["n_sources"] for r in rows)
    print("cases=%d  sources/case=%.1f" % (n, nsrc))
    print("完成率 %.4f   平均时间 %.1f s/源   总虚拟时间 %.0f s"
          % (statistics.mean(r["clear_ratio"] for r in rows),
             statistics.mean(r["mean_time"] if r["n_cleared"] else 9000.0 for r in rows),
             statistics.mean(r["virtual_time"] for r in rows)))
    print("行程合计 %.0f m = %.0f s" % (sum(tt.values()), sum(tt.values()) / 5.0))
    for k in ("census", "probe", "localise", "clear"):
        print("   %-9s 任务数 %5.1f  行程 %7.0f m (%5.0f s)"
              % (k, cnt[k], tt[k], tt[k] / 5.0))
    print("检测次数 %.1f  (%.0f s, 含切换约 %.0f s)"
          % (statistics.mean(r["n_measure"] for r in rows),
             statistics.mean(r["n_measure"] for r in rows) * 5.0,
             statistics.mean(r["n_measure"] for r in rows) * 6.0))
    print("清除动作 %.1f 次" % statistics.mean(r["n_clear"] for r in rows))
    print("覆盖站位实际访问 %.1f 个；不同落点 %.1f 个"
          % (statistics.mean(r["n_stops"] for r in rows),
             statistics.mean(r["n_pts"] for r in rows)))
    # 点集下界参考
    bnd = []
    for r in rows:
        pts = set()
        for kind, a, b in r["legs"]:
            pts.add((round(b[0], 1), round(b[1], 1)))
        bnd.append(two_opt_len(list(pts)))
    print("同点集 2-opt 巡回下界 %.0f m（实测 %.0f m，余量 %.1f%%）"
          % (statistics.mean(bnd), sum(tt.values()),
             100.0 * (sum(tt.values()) / statistics.mean(bnd) - 1.0)))
    src_bnd = []
    for r in rows:
        pts = list(r["src_pos"]) + [(0.0, 0.0)]
        src_bnd.append(two_opt_len(pts))
    tot = statistics.mean([r["n_sources"] for r in rows])
    print("只访问干扰源+原点的 2-opt 巡回 %.0f m = %.0f s（%.0f s/源）"
          % (statistics.mean(src_bnd), statistics.mean(src_bnd) / 5.0,
             statistics.mean(src_bnd) / 5.0 / tot))
    json.dump([{k: v for k, v in r.items() if k != "legs"} for r in rows],
              open(os.path.join(HERE, "..", "data", "where_%s.json" % MODE), "w",
                   encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
