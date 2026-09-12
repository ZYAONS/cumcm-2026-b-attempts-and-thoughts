# -*- coding: utf-8 -*-
"""fix_stale_all.py -- 清掉论文里所有过期数字与一处 LaTeX 拼写错误。"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EDITS = [
    # 1) LaTeX 错误：制表符 + extbf
    ("问题四\textbf{在全部扰动下都恒为 1.000}", "问题四在全部扰动下仍保持 0.988 以上", "tab-typo"),
    ("问题三、问题四\textbf{在全部扰动下都恒为 1.000}",
     "问题三在所有扰动下恒为 1.000，问题四保持在 0.988 以上", "tab-typo2"),
    # 2) 问题三正式测试描述
    ("平均定位清除时间分别为 257.5 s、392.0 s、389.1 s（均值 346.2 s）",
     "平均定位清除时间分别为 280.5 s、337.0 s、369.1 s（均值 328.9 s）", "q3-formal"),
    ("对应的行为日志为 \\texttt{logs/formal/formal\\_seed810001.log} 等三个文件",
     "对应的行为日志为 \\texttt{logs/formal/formal\\_seed990001.log} 等三个文件", "q3-log"),
    # 3) 问题四正式测试描述
    ("三次正式测试共清除 34 个干扰源中的 34 个（三局完成率均为 100\\%），"
     "平均定位清除时间 966.4 s、920.8 s、1204.3 s（均值 1030.5 s），程序运行时间均小于 5 s。",
     "三次正式测试共清除 35 个干扰源中的 35 个（三局完成率均为 100\\%），"
     "平均定位清除时间 612.9 s、692.5 s、622.5 s（均值 642.6 s），程序运行时间均小于 4.2 s。",
     "q4-formal"),
    ("平均时间 1133.1 s、945.2 s、1193.4 s。", "平均时间 612.9 s、692.5 s、622.5 s。",
     "q4-formal2"),
    # 4) 贪心对照
    ("问题四中纯贪心策略的完成率骤降到 48.4\\%",
     "问题四中纯贪心策略的完成率骤降到 55.7\\%", "greedy"),
    # 5) 策略对照表：移动距离
    ("\\textbf{1.000} & 307.7 & 12803\\\\", "\\textbf{1.000} & 307.7 & 12928\\\\",
     "policy-travel"),
]
ok = total = 0
for fname in ("paper_p1.tex", "paper_p3.tex"):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b, tag in EDITS:
        if a not in s:
            continue
        s = s.replace(a, b, 1)
        ok += 1
        print("  ok [%s] (%s)" % (tag, fname))
    io.open(p, "w", encoding="utf-8").write(s)
    total = len(EDITS)
print("更新 %d 处" % ok)
# 报告未命中的锚点
s_all = "".join(io.open(os.path.join(HERE, f), encoding="utf-8").read()
                for f in ("paper_p1.tex", "paper_p3.tex"))
missing = [t for a, b, t in EDITS if b not in s_all]
print("未生效：", missing if missing else "无")
sys.exit(0)
