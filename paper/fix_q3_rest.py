# -*- coding: utf-8 -*-
"""fix_q3_rest.py -- 收尾：修掉表格残句 + 更新灵敏度表与正式测试描述。"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p3.tex")
s = io.open(p, encoding="utf-8").read()
ok = 0
total = 0


def rep(a, b, tag):
    global s, ok, total
    total += 1
    if a not in s:
        print("  !! 锚点未找到 [%s]" % tag)
        return
    s = s.replace(a, b, 1)
    ok += 1
    print("  ok [%s]" % tag)


# 1) 修掉切片残留的孤立反斜杠
rep("1718 & 10（10） & 369.1 & 1.2\\\\\n\\\n\\bottomrule",
    "1718 & 10（10） & 369.1 & 1.2\\\\\n\\bottomrule",
    "stray-backslash")

# 2) 灵敏度表（data/q3_sensitivity.csv 的实测值）
rep(r"""基准 & 1.000 & 310.6\\
有效接收半径下界 $R_{\min}:1000\to950$ m & 1.000 & 309.0\\
有效接收半径下界 $R_{\min}:1000\to1050$ m & 1.000 & 320.4\\
有效接收半径上界 $R_{\max}:1500\to1400$ m & 1.000 & 314.0\\
测角误差 $1^{\circ}\to0.8^{\circ}$ & 1.000 & 335.5\\
干扰源个数固定为 10 & 1.000 & 380.7\\
干扰源个数固定为 16 & 1.000 & 251.4\\""",
    r"""基准 & 1.000 & 285.8\\
有效接收半径下界 $R_{\min}:1000\to950$ m & 1.000 & 341.5\\
有效接收半径下界 $R_{\min}:1000\to1050$ m & 1.000 & 289.7\\
有效接收半径上界 $R_{\max}:1500\to1400$ m & 1.000 & 296.5\\
测角误差 $1^{\circ}\to0.8^{\circ}$ & 1.000 & 304.5\\
干扰源个数固定为 10 & 1.000 & 375.4\\
干扰源个数固定为 16 & 1.000 & 249.3\\""",
    "tab-q3sens")

# 3) 灵敏度段落的正文数字
rep("时间随源数显著变化（10 源 380.7 s，16 源 251.4 s）",
    "时间随源数显著变化（10 源 375.4 s，16 源 249.3 s）",
    "sens-text")

# 4) 正式测试描述
rep(r"""三次正式测试均\textbf{清除了全部干扰源}（完成率 100\%），平均定位清除时间分别为 350.6 s、239.4 s、344.5 s（均值 311.5 s），程序运行时间均小于 2 s，远低于 20 min 上限。""",
    r"""三次正式测试均\textbf{清除了全部干扰源}（完成率 100\%），平均定位清除时间分别为 280.5 s、337.0 s、369.1 s（均值 328.9 s），程序运行时间均小于 2.1 s，远低于 20 min 上限。""",
    "formal-text")

# 5) 摘要里的正式测试数字
rep("平均时间 350.6 s、239.4 s、344.5 s。",
    "平均时间 280.5 s、337.0 s、369.1 s。", "abstract-formal")

# 6) 策略对照表里的问题三行（agg 已重算）
rep(r"规划式（覆盖站位 + 2-opt 滚动重规划，本文） & 三 & \textbf{1.000} & 313.3 & 12803\\",
    r"规划式（覆盖站位 + 2-opt 滚动重规划，本文） & 三 & \textbf{1.000} & 307.7 & 12928\\",
    "policy-q3")

# 7) 核对段落
rep("问题三为 313.3 s 对 324.1 s", "问题三为 307.7 s 对 324.1 s", "policy-text")

io.open(p, "w", encoding="utf-8").write(s)
print("更新 %d/%d" % (ok, total))
sys.exit(0 if ok == total else 1)
