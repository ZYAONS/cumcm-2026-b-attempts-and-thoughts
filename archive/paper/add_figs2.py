# -*- coding: utf-8 -*-
"""add_figs2.py -- insert the two remaining figures and trim prose."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s:
            print("  WARN anchor missing in", fname, ":", a[:60].replace("\n", " "))
            continue
        s = s.replace(a, b, 1)
        print("  ok in", fname)
    io.open(p, "w", encoding="utf-8").write(s)


# 1) baseline chart after the comparison table of problem 2
edit("paper_p2.tex", [
    ("""\\begin{figure}[H]
\\centering
\\includegraphics[width=0.84\\textwidth]{../figures/fig_q2_montecarlo.png}""",
     """\\begin{figure}[H]
\\centering
\\includegraphics[width=0.62\\textwidth]{../figures/fig_q2_baselines.png}
\\caption{五种第二检测点规则的实际定位区域直径（均值与 95\\% 分位；为便于显示，纵轴截断于 400 m。C、D 两策略存在无界情形，真实均值分别为 2508.7 m 与 1285.0 m）}
\\label{fig:q2basefig}
\\end{figure}

\\begin{figure}[H]
\\centering
\\includegraphics[width=0.62\\textwidth]{../figures/fig_q2_montecarlo.png}"""),
])

# 2) Q3/Q4 comparison panel before the Q4 drill table
edit("paper_p3.tex", [
    ("""\\begin{table}[H]
\\centering
\\caption{问题四演练测试统计}""",
     """\\begin{figure}[H]
\\centering
\\includegraphics[width=0.70\\textwidth]{../figures/fig_q34_stats.png}
\\caption{问题三与问题四的整体对比：平均定位清除时间、虚拟时间构成与清障完成率}
\\label{fig:q34stats}
\\end{figure}

\\begin{table}[H]
\\centering
\\caption{问题四演练测试统计}"""),
])

# 3) offset the two added floats by trimming prose
edit("paper_p2.tex", [
    ("""第一层 $\\max$ 遍历 $\\mathcal G$（用 32 个对数分布的距离 $\\times$ 7 个角度离散，共 224 个点）与 $\\delta_2=\\pm\\varepsilon$ 两个端点；第二层 $\\min$ 在极坐标网格 $(b,\\varphi)$ 上进行，并以坐标下降法细化到 $0.5$ m / $0.2^{\\circ}$。""",
     """第一层 $\\max$ 遍历 $\\mathcal G$（32 个对数分布距离 $\\times$ 7 个角度 = 224 点）与 $\\delta_2=\\pm\\varepsilon$；第二层 $\\min$ 在极坐标网格 $(b,\\varphi)$ 上用坐标下降细化到 $0.5$ m / $0.2^{\\circ}$。"""),
    ("""其工程含义十分直观：\\emph{“沿与示向度约 40$^{\\circ}$ 的方向、后退到保证接收半径 1000 m 处”}。该区域对 $\\eta$ 的敏感性是“窄带型”——$b$ 的方向几乎不可偏离 1000 m（因为更快失效的是保证探测约束），而 $\\varphi$ 在 $\\pm40^{\\circ}$ 内有较大自由度，故实际执行时\\textbf{优先保证距离、其次调整角度}。""",
     """工程含义直观：\\emph{“沿与示向度约 40$^{\\circ}$ 的方向、后退到保证接收半径 1000 m 处”}。该区域是“窄带型”——$b$ 几乎不可偏离 1000 m（先失效的是保证探测约束），而 $\\varphi$ 在 $\\pm40^{\\circ}$ 内有较大自由度，故执行时\\textbf{优先保证距离、其次调整角度}。"""),
])

edit("paper_p3.tex", [
    ("""结论：策略对接收半径、测角误差与干扰源个数均保持\\textbf{完成率 100\\%}；平均时间随干扰源个数显著变化（10 个源时 414.8 s，16 个源时 272.9 s），因为搜索成本近似固定而目标数增加会分摊成本。接收半径下界降低（$R_{\\min}=950$ m）会使平均时间下降，原因是更小的“最坏接收半径”意味着实际源更容易被提前发现；这提示\\textbf{结果对 $R_{\\min}$ 的敏感性主要来自搜索覆盖的设计假设，而非算法本身}。""",
     """结论：策略对接收半径、测角误差与干扰源个数均保持\\textbf{完成率 100\\%}；平均时间随源数显著变化（10 源 414.8 s，16 源 272.9 s），因为搜索成本近似固定而被更多目标分摊。$R_{\\min}$ 降为 950 m 时平均时间下降，说明\\textbf{结果对 $R_{\\min}$ 的敏感性主要来自搜索覆盖的设计假设，而非算法本身}。"""),
])
print("done")
