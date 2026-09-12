# -*- coding: utf-8 -*-
"""trace_clear.py -- 把一次"定位+清除"的每一次检测/清除动作逐条打出来，
看清 10 次检测/源 到底花在哪。

用法: python trace_clear.py [seed]
"""
import os
import random
import sys

import robot_core as rc
import simulator as sim
from make_data import P3, P4

MODE = os.environ.get("MODE", "q3")


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P3 if MODE == "q3" else P4)
    srcs = sim.make_case(random.Random(seed),
                         kind_mix=(0.0 if MODE == "q3" else 0.5))
    arena = sim.Arena(srcs, seed=seed)
    cl = rc.LocalClient(arena)
    brain = rc.Brain(cl, params=p, seed=seed)
    log = []
    om, oc = brain.move_measure, brain.move_clear

    def m2(x, y, c):
        r = om(x, y, c)
        log.append(("M", brain._cur_task, c, round(x), round(y),
                    r.get("measure_result"), brain.status[c],
                    None if brain.est[c] is None else round(brain.est[c][2])))
        return r

    def c2(x, y, c):
        r = oc(x, y, c)
        log.append(("C", brain._cur_task, c, round(x), round(y),
                    r.get("clear_result"), brain.status[c], None))
        return r
    brain.move_measure, brain.move_clear = m2, c2
    st = brain.run()
    st.update(arena.stats())
    arena.close()

    # per-channel statistics for the CLEAR task
    per = {}
    for e in log:
        if e[1] != "clear":
            continue
        per.setdefault(e[2], []).append(e)
    by_ch = dict((s.channel, s) for s in srcs)
    print("完成率 %.3f  平均 %.1f s/源  检测 %d 次  清除 %d 次"
          % (st["clear_ratio"], st["mean_time"], st["n_measure"], st["n_clear"]))
    print("%-5s %-6s %-6s %-8s %s" % ("ch", "类型", "距离", "检测数", "清除数"))
    tot_m = tot_c = 0
    for c, ev in sorted(per.items()):
        nm = sum(1 for e in ev if e[0] == "M")
        nc = sum(1 for e in ev if e[0] == "C")
        kind = by_ch[c].kind if c in by_ch else "?"
        tot_m += nm
        tot_c += nc
        print("%-5d %-6s %-6s %-8d %d" % (c, kind, "已清除" if c in by_ch and by_ch[c].cleared else "未清除", nm, nc))
    print("清除任务内：检测 %d 次（%.0f s）、清除 %d 次（%.0f s）"
          % (tot_m, tot_m * 6.0, tot_c, tot_c * 4.0))

    # 打印一条最长的清除过程
    worst = max(per.items(), key=lambda kv: len(kv[1])) if per else None
    if worst:
        print("\n最长的一条（频道 %d，真值 %s，共 %d 个动作）："
              % (worst[0], (round(by_ch[worst[0]].x), round(by_ch[worst[0]].y))
                 if worst[0] in by_ch else "?", len(worst[1])))
        for e in worst[1]:
            print("   %s ch%-3d pos=(%6d,%6d)  %-16s status=%-8s sigma=%s"
                  % (e[0], e[2], e[3], e[4], e[5], e[6], e[7]))


if __name__ == "__main__":
    main()
