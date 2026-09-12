# -*- coding: utf-8 -*-
"""trim7.py -- shave a few lines so that both PDF versions keep a 30-page body."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p3.tex")
s = io.open(p, encoding="utf-8").read()
pairs = [
    ("""  \\item \\textbf{路径规划仍是非最优的启发式}。本文用最近邻 + 2-opt，未使用 LKH 等强求解器，也未利用“清除顺序影响后续探测概率”这一耦合。可将其建模为带信息获取的动态车辆路径问题（DTRP）\\cite{bersimas1991}，用近似动态规划求解。""",
     """  \\item \\textbf{路径规划仍是启发式}。本文用最近邻 + 2-opt，未利用“清除顺序影响后续探测概率”这一耦合；可建模为带信息获取的动态车辆路径问题\\cite{bersimas1991}并用近似动态规划求解。"""),
    ("""  \\item \\textbf{未建模通信与真实时间约束的耦合}。本文假设通信可靠且往返时间可忽略；若真实系统带宽受限，应把“每次请求的真实耗时”纳入目标函数，形成虚拟时间与真实时间的双目标优化。""",
     """  \\item \\textbf{未耦合通信与真实时间}。若真实系统带宽受限，应把“每次请求的真实耗时”纳入目标函数，形成虚拟时间与真实时间的双目标优化。"""),
    ("""  \\item \\textbf{假设了误差独立同界}。工程上不同地点的误差可能存在空间相关性（同一条街道、同一建筑反射），若误差相关性较强，多次测量的信息增益会下降，需要在问题二的模型中引入相关结构。""",
     """  \\item \\textbf{假设误差独立同界}。若不同地点的误差存在空间相关性（同一建筑反射），多次测量的信息增益会下降，需在问题二模型中引入相关结构。"""),
]
for a, b in pairs:
    if a not in s:
        print("  WARN:", a[:40])
        continue
    s = s.replace(a, b, 1)
    print("  ok")
io.open(p, "w", encoding="utf-8").write(s)
print("trimmed")
