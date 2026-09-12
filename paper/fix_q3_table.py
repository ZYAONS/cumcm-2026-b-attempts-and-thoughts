# -*- coding: utf-8 -*-
"""fix_q3_table.py -- 用 data/q3_agg.json 的实测值重写问题三演练统计表。"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
d = json.load(io.open(os.path.join(ROOT, "data", "q3_agg.json"), encoding="utf-8"))
travel_s = d["mean_travel"] / 5.0
vt = d["mean_vtime"]
meas_s = d["mean_measure"] * 6.0
rows = {
    "ratio": d["mean_ratio"],
    "time": d["mean_time"],
    "sd": d["sd_time"],
    "vtime": d["mean_vtime"],
    "travel": d["mean_travel"],
    "travel_pct": 100.0 * travel_s / vt,
    "measure": d["mean_measure"],
    "measure_pct": 100.0 * meas_s / vt,
    "clears": d["mean_clear_actions"],
}
print(rows)

p = os.path.join(HERE, "paper_p3.tex")
s = io.open(p, encoding="utf-8").read()
old = r"""被清除干扰源个数的比例 & \textbf{1.0000} & 最小值 1.0000\\
平均定位清除时间 $\bar T$ & \textbf{307.7 s} & 标准差 51.4 s\\
单局定位清除总时间 $T$ & 3996 s & --\\
平均移动距离 & 12928 m & 占总时间 64.1\%\\
平均检测次数 & 215.4 次 & 占 34.2\%\\
平均清除动作次数 & 21.3 次 & 含未命中\\"""
new = (r"被清除干扰源个数的比例 & \textbf{1.0000} & 最小值 1.0000\\" + "\n"
       r"平均定位清除时间 $\bar T$ & \textbf{%.1f s} & 标准差 %.1f s\\" % (rows["time"], rows["sd"]) + "\n"
       r"单局定位清除总时间 $T$ & %.0f s & --\\" % rows["vtime"] + "\n"
       r"平均移动距离 & %.0f m & 占总时间 %.1f\%%\\" % (rows["travel"], rows["travel_pct"]) + "\n"
       r"平均检测次数 & %.1f 次 & 占 %.1f\%%\\" % (rows["measure"], rows["measure_pct"]) + "\n"
       r"平均清除动作次数 & %.1f 次 & 含未命中\\" % rows["clears"])
assert old in s, "q3drill anchor missing"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("tab:q3drill 已按实测重写")
sys.exit(0)
