# -*- coding: utf-8 -*-
"""trim5.py -- shorten the last paragraphs so that the body ends on page 31."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p3.tex")
s = io.open(p, encoding="utf-8").read()

pairs = [
    ("""本文框架可直接推广到：(i) \\textbf{多机器人协同}——按 Voronoi 划分覆盖站位集并行搜索，终止判据变为“全体无信号点之并集覆盖目标域”；(ii) \\textbf{移动干扰源}——位置估计改为带运动模型的滤波，覆盖判据改为时空覆盖；(iii) \\textbf{TDOA/AOA 混合定位}——角度楔替换为双曲线带，问题一的半平面枚举推广为二次约束可行域枚举；(iv) \\textbf{应急搜救}——把“接收半径/频道”替换为“探测半径/目标类型”后，“覆盖保证+可证终止+在线路径”同样适用。""",
     """本文框架可直接推广到：(i) \\textbf{多机器人协同}——按 Voronoi 划分站位并行搜索，终止判据变为“全体无信号点之并集覆盖目标域”；(ii) \\textbf{移动干扰源}——估计改为带运动模型的滤波，覆盖判据改为时空覆盖；(iii) \\textbf{TDOA/AOA 混合定位}——角度楔换成双曲线带，问题一算法推广为二次约束可行域枚举；(iv) \\textbf{应急搜救}——替换“接收半径/频道”为“探测半径/目标类型”后三件套同样适用。"""),
    ("""本文的模型框架可直接推广到以下场景：""", """本文框架可直接推广到以下场景："""),
]
for a, b in pairs:
    if a in s:
        s = s.replace(a, b, 1)
        print("  ok")
    else:
        print("  WARN:", a[:40])
io.open(p, "w", encoding="utf-8").write(s)
print("trimmed")
