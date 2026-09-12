# -*- coding: utf-8 -*-
"""trim1.py -- remove one page worth of redundancy from the body."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s:
            print("  WARN anchor not found in", fname, ":", a[:40])
            continue
        s = s.replace(a, b, 1)
    io.open(p, "w", encoding="utf-8").write(s)
    print("  edited", fname)


# 1) compress the long itemised restatement of the device rules
edit("paper_p1.tex", [
    ("""  \\item 测向机频道切换耗时 1 s；一次检测（停下、切换、调整天线并读取稳定示向度）耗时 5 s；机器狗沿直线以 5 m/s 移动。
  \\item 光学探测仪仅在距干扰源不超过 20 m 时可精确定位并启动激光枪清除，精确定位 3 s、清除 2 s；若 20 m 内没有该频道干扰源则只耗 3 s（返回“未发现”）。
  \\item 检测点与干扰源距离不超过 5 m 且位于其覆盖角内时，因信号过强无法给出示向度（返回“near”），此时可直接光学精确定位并清除。""",
     """  \\item \\textbf{时间与清除}：频道切换 1 s；一次检测（停下、切换、调天线、读稳定示向度）5 s；机器狗沿直线以 5 m/s 移动。光学探测仪仅在距干扰源 $\\le20$ m 时可精确定位并启动激光枪清除（定位 3 s、清除 2 s）；20 m 内无该频道源时只耗 3 s（返回“未发现”）。检测点距源 $\\le5$ m 且在其覆盖角内时信号过强而无法给出示向度（返回“near”），可直接清除。"""),
])

# 2) compress the symbol table rows a little
edit("paper_p1.tex", [
    ("$T,\\bar T$ & 定位清除总时间与平均定位清除时间\\\\",
     "$T,\\bar T$ & 定位清除总时间、平均定位清除时间\\\\"),
])

# 3) shorten the promotion section and one analysis paragraph
edit("paper_p3.tex", [
    ("""本文的模型框架可直接推广到以下场景：(i) \\textbf{多机器人协同}——把覆盖站位集按 Voronoi 划分后并行搜索，终止判据变为“全体无信号点的并集覆盖目标域”；(ii) \\textbf{移动干扰源}——把位置估计换成带运动模型的滤波，覆盖判据改为“时空覆盖”；(iii) \\textbf{TDOA/AOA 混合定位}——把角度楔替换为双曲线带，问题一的半平面枚举算法可原样推广为二次约束的可行域枚举；(iv) \\textbf{应急搜救}——以“接收半径 $\\to$ 探测半径、频道 $\\to$ 目标类型”作替换后，本文的“覆盖保证 + 可证终止 + 在线路径”三件套同样适用。""",
     """本文框架可直接推广到：(i) \\textbf{多机器人协同}——按 Voronoi 划分覆盖站位集并行搜索，终止判据变为“全体无信号点之并集覆盖目标域”；(ii) \\textbf{移动干扰源}——位置估计改为带运动模型的滤波，覆盖判据改为时空覆盖；(iii) \\textbf{TDOA/AOA 混合定位}——角度楔替换为双曲线带，问题一的半平面枚举推广为二次约束可行域枚举；(iv) \\textbf{应急搜救}——把“接收半径/频道”替换为“探测半径/目标类型”后，“覆盖保证+可证终止+在线路径”同样适用。"""),
])

# 4) shrink the remaining wide figures slightly
for f in ("paper_p1.tex", "paper_p2.tex", "paper_p3.tex"):
    p = os.path.join(HERE, f)
    s = io.open(p, encoding="utf-8").read()
    s = s.replace("width=0.74\\textwidth", "width=0.70\\textwidth")
    io.open(p, "w", encoding="utf-8").write(s)
print("done")
