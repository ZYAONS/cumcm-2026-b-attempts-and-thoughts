# -*- coding: utf-8 -*-
"""fix_q3_rest2.py -- 剩余几处（摘要与表格）的最终替换。"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ok = total = 0


def edit(fname, pairs):
    global ok, total
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b, tag in pairs:
        total += 1
        if a not in s:
            print("  !! 锚点未找到 [%s] %s" % (tag, fname))
            continue
        s = s.replace(a, b, 1)
        ok += 1
        print("  ok [%s]" % tag)
    io.open(p, "w", encoding="utf-8").write(s)


edit("paper_p1.tex", [
    ("60 组演练完成率 \\textbf{100\\%}，平均定位清除时间 \\textbf{313.3} s（中位 308.3 s，标准差 48.1 s）；"
     "三次正式测试清除 12/12、16/16、11/11，平均时间 350.6 s、239.4 s、344.5 s。",
     "60 组演练完成率 \\textbf{100\\%}，平均定位清除时间 \\textbf{307.7} s（中位 296.8 s，标准差 49.3 s）；"
     "三次正式测试清除 14/14、12/12、10/10，平均时间 280.5 s、337.0 s、369.1 s。",
     "abstract-q3-final"),
])

edit("paper_p3.tex", [
    ("规划式（覆盖站位 + 2-opt 滚动重规划，本文） & 三 & \\textbf{1.000} & 313.3 & 12803\\\\",
     "规划式（覆盖站位 + 2-opt 滚动重规划，本文） & 三 & \\textbf{1.000} & 307.7 & 12928\\\\",
     "policy-q3"),
    ("问题三为 313.3 s 对 324.1 s", "问题三为 307.7 s 对 324.1 s", "policy-text"),
    ("平均定位清除时间分别为 350.6 s、239.4 s、344.5 s",
     "平均定位清除时间分别为 280.5 s、337.0 s、369.1 s", "formal-text"),
    ("（均值 311.5 s）", "（均值 328.9 s）", "formal-mean"),
])

print("更新 %d/%d" % (ok, total))
sys.exit(0 if ok == total else 1)
