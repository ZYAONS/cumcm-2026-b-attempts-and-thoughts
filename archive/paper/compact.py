# -*- coding: utf-8 -*-
"""compact.py -- bring the body of the paper within the 30 page limit.

  * shorter, one-page abstract
  * smaller figure widths
  * tighter float separation and smaller algorithm bodies
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def fix_p1():
    p = os.path.join(HERE, "paper_p1.tex")
    s = io.open(p, encoding="utf-8").read()

    # ---- tighter float spacing + smaller algorithm bodies
    anchor = "\\lstset{"
    add = ("\\setlength{\\textfloatsep}{7pt plus 2pt minus 2pt}\n"
           "\\setlength{\\floatsep}{7pt plus 2pt minus 2pt}\n"
           "\\setlength{\\intextsep}{7pt plus 2pt minus 2pt}\n"
           "\\setlength{\\abovedisplayskip}{5pt plus 2pt minus 2pt}\n"
           "\\setlength{\\belowdisplayskip}{5pt plus 2pt minus 2pt}\n"
           "\\usepackage{etoolbox}\n"
           "\\AtBeginEnvironment{algorithmic}{\\footnotesize}\n"
           "\\AtBeginEnvironment{thebibliography}{\\small}\n\n")
    s = s.replace(anchor, add + anchor, 1)

    # ---- new, shorter abstract
    start = s.find("\\begin{abstract}")
    end = s.find("\\end{abstract}") + len("\\end{abstract}")
    new_abs = r"""\begin{abstract}
本文为搭载便携式测向机的机器狗建立“几何定位—站位优化—在线搜索规划—可证终止”的完整模型体系，并按附件 1、附件 2 复现了本地模拟环境，完成大规模演练与三次正式测试。

\textbf{问题一}：把带 $\pm1^{\circ}$ 误差的示向度解释为以检测点为顶点的角楔，定位区域即各角楔之交。证明其为凸多边形、给出 $O(n^2)$ 顶点枚举算法与基于回收锥的有界性判据，用旋转卡壳法求直径并与一阶解析式 $D\!\approx\!\sqrt{w_1^2\!+\!w_2^2\!+\!2w_1w_2\cos\gamma}/\sin\gamma$ 互证（细长区域偏差 $<0.1\%$）。对“以直径为直径的圆能否覆盖”的回答是\textbf{一般不能}：本文证明任何直径为 $D$ 的覆盖圆必与直径圆重合（提法良定义），给出 Thales 充要判据，并在 6 万组随机算例中测得不能覆盖的比例为 $1.13\%$（2 站）$\sim3.70\%$（5 站），最大超出半径仅 $0.18\%$，同时给出最小包围圆作为正确替代。

\textbf{问题二}：注意到误差“地点固定、重复检测无效”，将选点建模为\textbf{极大极小优化}：在可行源扇形上最小化最坏情形定位区域直径，并加“保证第二次能收到信号”的约束。解得 $b^{*}=1004.1$ m、$\varphi^{*}=36.8^{\circ}$（相对示向度偏转）、$J^{*}=134.0$ m，且与检测点位置无关。候选区域为以 $S_1$ 为心、半径约 1000 m、张角 $\pm40^{\circ}$ 的圆弧带。相对朴素垂直策略，平均定位区域直径由 96.6 m 降到 55.1 m；沿示向度前进则 25.7\% 的算例定位区域无界；4000 次 Monte-Carlo 无一次越界。

\textbf{问题三}：提出“普查—机会式交会—射线归航—可证终止”策略。由\textbf{七点覆盖定理}（中心加正六边形顶点，$\rho=1280$ m）保证发现全部全向源，由“无信号点集 $R_{\min}$-覆盖目标域”给出可证明的终止判据；位置估计取问题一定位区域的最小包围圆，清除采用步长几何收缩、过冲减半的射线归航与末段六边形清除图案。60 组演练完成率 \textbf{100\%}，平均定位清除时间 \textbf{331.0} s；三次正式测试清除 15/15、12/12、10/10，平均时间 268.4 s、375.2 s、399.6 s。

\textbf{问题四}：定向源造成“\textbf{半平面黑洞}”，单点无信号无法排除干扰源。本文给出\textbf{认证判据}（候选位置落在其 $R_{\min}$ 邻域内无信号点凸包内部时任何定向方向都无法隐藏）与\textbf{射线逼近引理}（沿曾收到信号的射线逼近，全程不丢信号），并把站位加密为间距 1000 m 的三角格点、给出可选区域外补测机制。60 组混合演练完成率 \textbf{95.7\%}，平均定位清除时间 \textbf{661.0} s；三次正式测试清除 11、11、11 个源，平均时间 602.6 s、654.5 s、718.8 s。

论文另给出多方法互证、残差与不确定度一致性检验、参数灵敏度分析与外部文献对照（最优交会角 $90^{\circ}$、覆盖密度 $2\pi/3\sqrt3$ 等），并讨论模型优缺点与推广。

\keywords{\textbf{交会定位} \quad \textbf{极大极小站位优化} \quad \textbf{圆覆盖} \quad \textbf{在线路径规划} \quad \textbf{可证终止判据}}
\end{abstract}"""
    s = s[:start] + new_abs + s[end:]
    io.open(p, "w", encoding="utf-8").write(s)
    print("p1 compacted")


def shrink_figures():
    for f in ("paper_p1.tex", "paper_p2.tex", "paper_p3.tex"):
        p = os.path.join(HERE, f)
        s = io.open(p, encoding="utf-8").read()
        s = s.replace("width=0.99\\textwidth", "width=0.84\\textwidth")
        s = s.replace("width=0.98\\textwidth", "width=0.84\\textwidth")
        s = s.replace("width=0.72\\textwidth", "width=0.60\\textwidth")
        s = s.replace("width=0.66\\textwidth", "width=0.56\\textwidth")
        s = s.replace("width=0.62\\textwidth", "width=0.52\\textwidth")
        io.open(p, "w", encoding="utf-8").write(s)
    print("figures shrunk")


if __name__ == "__main__":
    fix_p1()
    shrink_figures()
