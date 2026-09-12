# -*- coding: utf-8 -*-
"""add_figs.py -- add the four remaining generated figures to the paper and trim
prose so that the body stays within 30 pages."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s:
            print("  WARN anchor missing in", fname, ":", a[:50].replace("\n", " "))
            continue
        s = s.replace(a, b, 1)
    io.open(p, "w", encoding="utf-8").write(s)
    print("  edited", fname)


# --- 1) virtual-time accounting figure in the analysis of problem 3
edit("paper_p1.tex", [
    ("""\\textbf{(3) 三个必须在模型中解决的子问题}。""",
     """\\begin{figure}[H]
\\centering
\\includegraphics[width=0.62\\textwidth]{../figures/fig_simulator_timing.png}
\\caption{四条指令中各动作的虚拟时间消耗（按附件 1 的算例：移动 500 m 用 100 s，检测 5 s，切换频道 1 s，清除未命中 3 s、命中 5 s）}
\\label{fig:timing}
\\end{figure}

\\textbf{(3) 三个必须在模型中解决的子问题}。"""),
])

# --- 2) baseline bar chart next to the comparison table of problem 2
edit("paper_p2.tex", [
    ("""\\begin{figure}[H]
\\centering
\\includegraphics[width=0.62\\textwidth]{../figures/fig_q2_montecarlo.png}""",
     """\\begin{figure}[H]
\\centering
\\includegraphics[width=0.62\\textwidth]{../figures/fig_q2_baselines.png}
\\caption{五种第二检测点规则的实际定位区域直径（均值与 95\\% 分位，为便于显示纵轴截断于 400 m；C、D 两策略存在无界情形，其真实均值分别为 2508.7 m 与 1285.0 m）}
\\label{fig:q2base}
\\end{figure}

\\begin{figure}[H]
\\centering
\\includegraphics[width=0.62\\textwidth]{../figures/fig_q2_montecarlo.png}"""),
])

# --- 3) Q3/Q4 statistic panel in the results of problem 4
edit("paper_p3.tex", [
    ("""\\begin{figure}[H]
\\centering
\\includegraphics[width=0.62\\textwidth]{../figures/fig_q4_case_map.png}""",
     """\\begin{figure}[H]
\\centering
\\includegraphics[width=0.70\\textwidth]{../figures/fig_q34_stats.png}
\\caption{问题三与问题四的整体对比：平均定位清除时间、虚拟时间构成与清障完成率}
\\label{fig:q34stats}
\\end{figure}

\\begin{figure}[H]
\\centering
\\includegraphics[width=0.62\\textwidth]{../figures/fig_q4_case_map.png}"""),
])

# --- 4) convergence / measurement-location figure in the verification chapter
edit("paper_p3.tex", [
    ("""\\subsection{残差结构分析}""",
     """\\begin{figure}[H]
\\centering
\\includegraphics[width=0.70\\textwidth]{../figures/fig_convergence.png}
\\caption{一次完整测试中的检测行为：左为各次检测的位置到出发点距离随虚拟时刻的变化（可见“由内向外”的搜索波前与回访），右为检测结果统计}
\\label{fig:conv}
\\end{figure}

\\subsection{残差结构分析}"""),
])

# --- 5) trim prose to compensate for the four added floats
edit("paper_p1.tex", [
    ("""工程上，干扰源定位分为初步监测、区域性排查与精准定位三个阶段；前两阶段由固定监测站、移动监测车或无人机完成，而受环境遮挡与低功率干扰源制约，最终的精确定位仍需技术人员携带便携式测向机徒步排查，效率低、风险高。""",
     """工程上干扰源定位分为初步监测、区域性排查与精准定位三阶段，前两阶段可由固定站、监测车或无人机完成，而受遮挡与低功率源制约，最终精确定位仍需技术人员携便携测向机徒步排查，效率低、风险高。"""),
    ("""\\textbf{(1) 信息来源的全部刻画}。已知信号在 $S_1$ 被收到，故干扰源距 $S_1$ 不超过其有效接收半径，而接收半径 $\\le1500$ m，因此 $G$ 位于以 $S_1$ 为心、半径 1500 m 的圆内；又因收到的是“direction”而非“near”，距离大于 5 m；再加上 $G$ 位于目标圆域内与方位角 $\\pm1^{\\circ}$ 的约束，可行源集合 $\\mathcal{G}$ 是一段长 1500 m、宽约 $\\pm1^{\\circ}$ 的扇形（图 \\ref{fig:q2geo}）。""",
     """\\textbf{(1) 信息来源的全部刻画}。信号在 $S_1$ 被收到 $\\Rightarrow$ 距离不超过有效接收半径 $\\le1500$ m；收到的是 direction 而非 near $\\Rightarrow$ 距离 $>5$ m；再加 $G$ 在目标域内与方位角 $\\pm1^{\\circ}$ 约束，可行源集合 $\\mathcal{G}$ 是一段长 1500 m、宽 $\\pm1^{\\circ}$ 的扇形（图 \\ref{fig:q2geo}）。"""),
])

edit("paper_p3.tex", [
    ("""\\textbf{机理解释}：(i) 约束 $\\Omega$ 中的“最坏情形”由离 $S_2$ 最远与最近的可行源共同决定；当 $b\\gtrsim1000$ m 时，近端源（$r\\approx5$ m）到 $S_2$ 的距离约等于 $b$，约束 $b\\le R_{\\min}$ 恰好取等号，故 $b^{*}\\approx R_{\\min}=1000$ m；(ii) 偏转角 $\\varphi$ 的作用是调节交会角——$\\varphi=0$ 时两条方位视线近似共线（$D$ 极大甚至无界），$\\varphi=90^{\\circ}$ 时虽然交会角好但 $S_2$ 离远端源过远、约束不可行；$\\varphi^{*}\\approx37^{\\circ}$ 是在“交会角接近 $90^{\\circ}$ 且落在 $R_{\\min}$ 约束边界上”这一折中下的最优值。""",
     """\\textbf{机理解释}：(i) 最坏情形由离 $S_2$ 最远与最近的可行源共同决定；$b>1000$ m 时近端源（$r\\approx5$ m）到 $S_2$ 的距离约等于 $b$，约束 $b\\le R_{\\min}$ 取等号，故 $b^{*}\\approx R_{\\min}$；(ii) $\\varphi=0$ 时两条方位视线近似共线（$D$ 极大甚至无界），$\\varphi=90^{\\circ}$ 时 $S_2$ 离远端源过远而使约束不可行，$\\varphi^{*}\\approx37^{\\circ}$ 是二者的折中。"""),
])
print("figures added, prose trimmed")
