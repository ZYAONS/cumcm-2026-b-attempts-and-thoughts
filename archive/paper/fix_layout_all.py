# -*- coding: utf-8 -*-
"""fix_layout_all.py -- remove every overfull box and make the wide tables fit.

Overfull boxes reported by the compiler (line numbers refer to the merged
paper.tex; the offsets are paper_p1 = 1..245, paper_p2 = 246..590,
paper_p3 = 591..1099):

  164   long inline minimax formula            -> display equation
  643   long LOCALISE bullet                   -> shorter wording + explicit break
  746   policy comparison table too wide       -> p{} first column + \small
  768   Q3 formal-test table too wide          -> breakable code column
  835   theorem statement                     -> shorter wording
  935   Q4 formal-test table too wide          -> breakable code column
  986   verification table                     -> \small
  1034  reference-comparison bullet            -> shorter sentence
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s:
            print("  !! anchor missing in %s: %s" % (fname, a[:52].replace("\n", " ")))
            continue
        s = s.replace(a, b, 1)
        print("  ok  %s : %s" % (fname, a[:52].replace("\n", " ")))
    io.open(p, "w", encoding="utf-8").write(s)


# ---------------------------------------------------------------- p1 ------
edit("paper_p1.tex", [
    ("""\\textbf{(3) 设计准则}。由于 $G$ 在 $\\mathcal{G}$ 中未知，取\\textbf{极大极小准则}：$S_2^{*}=\\arg\\min_{S_2}\\max_{G\\in\\mathcal{G},\\ |\\delta_2|\\le1^{\\circ}}D(S_1,S_2,G,\\delta_2)$。同时必须保证第二次检测确实能收到信号，否则策略失效：约束 $|S_2-G|\\le R_{\\min}=1000$ m 对一切 $G\\in\\mathcal{G}$ 成立（用最坏接收半径，故为\\textbf{保证}探测）。""",
     """\\textbf{(3) 设计准则}。由于 $G$ 在 $\\mathcal{G}$ 中未知，取\\textbf{极大极小（minimax）准则}：
\\begin{equation}
S_2^{*}=\\arg\\min_{S_2}\\ \\max_{G\\in\\mathcal{G}}\\ \\max_{|\\delta_2|\\le1^{\\circ}}\\ D\\bigl(S_1,S_2,G,\\delta_2\\bigr).
\\label{eq:q2minimax}
\\end{equation}
同时必须保证第二次检测确实能收到信号，否则策略失效，故施加约束：对一切 $G\\in\\mathcal{G}$ 有 $|S_2-G|\\le R_{\\min}=1000$ m（取最坏接收半径，故为\\textbf{保证}探测）。"""),
])

# ---------------------------------------------------------------- p3 ------
edit("paper_p3.tex", [
    # 643 : LOCALISE bullet
    ("""  \\item \\textbf{LOCALISE}$(c)$：对只有一条方位的频道，按问题二规则设置专门观测点（$b=\\min(1000,0.6r_{\\rm hi})$，$\\varphi=\\pm55^{\\circ}$ 就近取侧），获取第二条方位；""",
     """  \\item \\textbf{LOCALISE}$(c)$：对只有一条方位的频道，按问题二规则设置专门观测点，取 $b=\\min(1000,\\,0.6r_{\\rm hi})$、$\\varphi=\\pm55^{\\circ}$（就近取侧），以获得第二条方位；"""),
    # 746 : policy comparison table
    ("""\\begin{tabular}{lcccc}
\\toprule
策略 & 问题 & 完成率 & 平均定位清除时间/s & 平均移动/m\\\\""",
     """\\small
\\begin{tabular}{p{4.6cm}cccc}
\\toprule
策略 & 问题 & 完成率 & 平均定位清除时间/s & 平均移动/m\\\\"""),
    ("""规划式（本文，覆盖站位 + 2-opt 滚动重规划） & 三 & \\textbf{1.000} & 331.0 & 14715\\\\""",
     """规划式（覆盖站位 + 2-opt 滚动重规划，本文） & 三 & \\textbf{1.000} & 331.0 & 14715\\\\"""),
    # 768 : Q3 formal test table -- breakable code column
    ("""\\begin{tabular}{cccc}
\\toprule
测试案例编码 & 清除干扰源个数 & 平均定位清除时间/s & 程序运行时间/s\\\\
\\midrule
Q3-810001-020304050708101112131415171819 & 15（15） & 268.4 & 1.7\\\\
Q3-810002-010203070809101215171819 & 12（12） & 375.2 & 1.3\\\\
Q3-810003-01020405061013141516 & 10（10） & 399.6 & 1.5\\\\
\\bottomrule
\\end{tabular}""",
     """\\small
\\begin{tabular}{p{5.6cm}ccc}
\\toprule
测试案例编码 & 清除干扰源\\newline 个数 & 平均定位清除\\newline 时间/s & 程序运行\\newline 时间/s\\\\
\\midrule
\\ttfamily Q3-810001-\\hspace{0pt}0203040507\\hspace{0pt}0810111213\\hspace{0pt}1415171819 & 15（15） & 268.4 & 1.7\\\\
\\ttfamily Q3-810002-\\hspace{0pt}0102030708\\hspace{0pt}0910121517\\hspace{0pt}1819 & 12（12） & 375.2 & 1.3\\\\
\\ttfamily Q3-810003-\\hspace{0pt}0102040506\\hspace{0pt}1013141516 & 10（10） & 399.6 & 1.5\\\\
\\bottomrule
\\end{tabular}"""),
    # 835 : theorem statement
    ("""设候选位置 $q$ 的 $R_{\\min}$ 邻域内已有一组返回 no\\_signal 的检测点 $\\{p_1,\\dots,p_k\\}$（即 $|p_j-q|\\le R_{\\min}$）。则“存在某个定向方向 $u$ 使该干扰源躲过全部这些检测”当且仅当存在半平面包含全部向量 $\\{p_j-q\\}$；等价地，\\textbf{可以排除该干扰源}当且仅当""",
     """设候选位置 $q$ 的 $R_{\\min}$ 邻域内已有一组返回 no\\_signal 的检测点 $\\{p_1,\\dots,p_k\\}$，即 $|p_j-q|\\le R_{\\min}$。则“存在某个定向方向 $u$，使该源躲过全部这些检测”等价于“存在一个半平面包含全部向量 $p_j-q$”。因此\\textbf{可以排除该干扰源}当且仅当"""),
    # 935 : Q4 formal test table
    ("""\\begin{tabular}{cccc}
\\toprule
测试案例编码 & 清除干扰源个数 & 平均定位清除时间/s & 程序运行时间/s\\\\
\\midrule
Q4-910001-0104050607081013171820 & 11（11） & 602.6 & 2.0\\\\
Q4-910002-030405060809111215161920 & 11（12） & 654.5 & 2.3\\\\
Q4-910003-0102030711131415171819 & 11（11） & 718.8 & 2.3\\\\
\\bottomrule
\\end{tabular}""",
     """\\small
\\begin{tabular}{p{5.6cm}ccc}
\\toprule
测试案例编码 & 清除干扰源\\newline 个数 & 平均定位清除\\newline 时间/s & 程序运行\\newline 时间/s\\\\
\\midrule
\\ttfamily Q4-910001-\\hspace{0pt}0104050607\\hspace{0pt}0810131718\\hspace{0pt}20 & 11（11） & 602.6 & 2.0\\\\
\\ttfamily Q4-910002-\\hspace{0pt}0304050608\\hspace{0pt}0911121516\\hspace{0pt}1920 & 11（12） & 654.5 & 2.3\\\\
\\ttfamily Q4-910003-\\hspace{0pt}0102030711\\hspace{0pt}1314151718\\hspace{0pt}19 & 11（11） & 718.8 & 2.3\\\\
\\bottomrule
\\end{tabular}"""),
    # 986 : verification table
    ("""\\begin{tabular}{p{3.1cm}p{4.1cm}p{4.1cm}p{3.2cm}}""",
     """\\small
\\begin{tabular}{p{3.0cm}p{4.0cm}p{4.0cm}p{3.2cm}}"""),
    # 1034 : reference-comparison bullet
    ("""  \\item 交会角的最优性：文献\\cite{xiu2005}以圆概率误差（CEP）最小为准则推出最优交会角为 $90^{\\circ}$，文献\\cite{sheng2016}进一步指出存在系统误差时最优交会角会偏离 $90^{\\circ}$。本文问题二的最优解 $\\varphi^{*}=36.8^{\\circ}$ 对应的实际交会角为 $89.5^{\\circ}\\sim91.2^{\\circ}$（随源距离变化），与之\\textbf{完全一致}；偏离的存在正对应本文“两侧读数误差同号”的最坏情形设定。""",
     """  \\item 交会角的最优性：文献\\cite{xiu2005}以圆概率误差（CEP）最小为准则推出最优交会角为 $90^{\\circ}$；文献\\cite{sheng2016}进一步指出存在系统误差时最优交会角会偏离 $90^{\\circ}$。本文问题二的最优解 $\\varphi^{*}=36.8^{\\circ}$ 对应的实际交会角为 $89.5^{\\circ}\\sim91.2^{\\circ}$（随源距离变化），与之\\textbf{完全一致}；其偏离正对应本文“两侧读数误差同号”的最坏情形设定。"""),
])
print("layout fixes applied")
