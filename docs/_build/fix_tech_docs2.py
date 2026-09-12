# -*- coding: utf-8 -*-
"""fix_tech_docs2.py -- the last three overfull boxes of the Q3 report."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "tech_q3.tex")
s = io.open(p, encoding="utf-8").read()

pairs = [
    # (1) long inline maths inside a list item
    ("""  \\item \\textbf{LOCALISE}$(c)$：对只有一条方位的频道，按问题二规则设置专门观测点
        （$b=\\min(1000,\\,0.6r_{\\rm hi})$，$\\varphi=\\pm55^{\\circ}$ 就近取侧），获取第二条方位；""",
     """  \\item \\textbf{LOCALISE}$(c)$：对只有一条方位的频道，按问题二规则设置专门观测点，
        取 $b=\\min(1000,\\,0.6r_{\\rm hi})$、$\\varphi=\\pm55^{\\circ}$（就近取侧），以获得第二条方位；"""),
    # (2) unbreakable URL: insert break opportunities without adding hyphens
    ("""官方模拟器只通过百度网盘分发（\\texttt{pan.baidu.com/s/1P1yfVjY0RufU93XOdzhOLw?pwd=2026}），
且首次运行需联网、用参赛队号/队员姓名/手机号注册登录并与竞赛服务器校验时间；正式测试额度
绑定在该账号上。""",
     """官方模拟器只通过百度网盘分发（链接形如
\\texttt{pan.baidu.com/s/\\hspace{0pt}1P1yfVjY0RufU93XOdzhOLw}，
提取码 \\texttt{2026}），且首次运行需联网，用参赛队号/队员姓名/手机号注册登录并与竞赛
服务器校验时间；正式测试额度绑定在该账号上。"""),
    # (3) comparison table with a long first column
    ("""\\begin{tabular}{lccc}
\\toprule
策略 & 完成率 & 平均定位清除时间/s & 平均移动/m \\\\ \\midrule
规划式（本文，覆盖站位 $+$ 2-opt 滚动重规划） & \\textbf{1.000} & 331.0 & 14715 \\\\
纯贪心（就近选择任务，无路径规划） & 0.998 & 331.1 & 15055 \\\\
\\bottomrule
\\end{tabular}""",
     """\\small
\\begin{tabular}{p{5.6cm}ccc}
\\toprule
策略 & 完成率 & 平均定位清除时间/s & 平均移动/m \\\\ \\midrule
规划式（覆盖站位 $+$ 2-opt 滚动重规划，本文） & \\textbf{1.000} & 331.0 & 14715 \\\\
纯贪心（就近选择任务，无路径规划） & 0.998 & 331.1 & 15055 \\\\
\\bottomrule
\\end{tabular}"""),
]
for a, b in pairs:
    if a not in s:
        print("  !! missing:", a[:50].replace("\n", " "))
        continue
    s = s.replace(a, b, 1)
    print("  ok:", a[:50].replace("\n", " "))
io.open(p, "w", encoding="utf-8").write(s)
print("done")
