# -*- coding: utf-8 -*-
"""update_verify_doc.py -- add the final, independent-pool numbers and the rim
patrol decision to the verification report."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "simulator_verification.tex")
s = io.open(p, encoding="utf-8").read()

a = """结论：\\textbf{问题三的性能是结构性的}——8 个参数在 313$\\sim$348 s 的窄带内几乎无差异，
说明瓶颈是"覆盖 $+$ 认证"的固有行程，不是参数没调好；
\\textbf{问题四的收益是真实的}——完成率从不稳定（最差 0.9375）提升到恒为 1.0000，
平均时间下降约 20\\%，主要来自"不再为无法完成认证的边界候选点白跑"。"""

b = r"""结论：\textbf{问题三的性能是结构性的}——8 个参数在 313$\sim$348 s 的窄带内几乎无差异，
说明瓶颈是"覆盖 $+$ 认证"的固有行程，不是参数没调好；
\textbf{问题四的收益是真实的}，而且必须分两步看。

\textbf{第一步：修正的代价。} 修正认证扫描后，"提前宣布完成"不再发生，
机器人必须真正走完搜索，因此时间上升：

\begin{center}
\begin{tabular}{lcccc}
\toprule
 & 完成率 & 最差完成率 & 平均时间/s & 平均行程/m \\ \midrule
修正前（错误认证） & 0.9574 & 0.8333 & 661.0 & 28476 \\
修正后 & \textbf{0.9935} & 0.9091 & 1476.1 & 73064 \\
\bottomrule
\end{tabular}
\end{center}

\textbf{第二步：在正确的前提下重新优化。} 把搜索成本按任务类别拆开后发现：
\textbf{89\% 的时间与行程都花在"搜索站位"上}（65 次搜索任务对 12 次清除任务），
而其中相当一部分站位是"域内永远无法完成认证"的边界候选点。

据此做了两项改动并逐项验收：

\begin{center}
\begin{tabular}{lccc}
\toprule
改动 & 完成率 & 平均时间/s & 平均行程/m \\ \midrule
（基线：修正后） & 0.9944 & 1176.5 & 58944 \\
抑制无法完成认证的搜索站位 & 0.9944 & 955.0 & 47923 \\
再调参（格点间距 1100 m 等） & 0.9935 & \textbf{945} & 47000 \\
\bottomrule
\end{tabular}
\end{center}

\textbf{关键否证}：一度实现的"边界外定向补测"（rim patrol）看似必要
（定理 2 说边界点在域内不可认证），但在\textbf{演练池 30 例}上逐项对照后发现：
开启与关闭的\textbf{完成率完全相同（0.9944，最差也相同 0.9000）}，
而关闭后时间与行程各降 \textbf{18.8\%}。逐个检查失败算例也显示，
漏掉的源半径多在 1158$\sim$1673 m（\textbf{并非贴边}），补测机制对它们毫无帮助。
因此该机制\textbf{默认关闭}，只在需要时作为可选项保留。

\begin{keybox}[title=最终验收（独立算例池，从未参与调参）]
问题四：平均时间 1476.1 s $\to$ \textbf{1018.1 s}（$-31.0\%$），
行程 $-32.8\%$，完成率 0.9935 $\to$ 0.9893（相当）。
问题三：平均时间 333.4 s $\to$ \textbf{323.0 s}（$-3.1\%$），行程 $-9.3\%$，完成率恒为 1.0000。\par
正式测试（HTTP）：问题四由"11/11、11/12、11/11"变为 \textbf{11/11、12/12、11/11}，
此前漏掉的贴边朝外源被成功清除；问题三保持 15/15、12/12、10/10。
\end{keybox}

\textbf{唯一未能消除的失败模式}：贴边且定向方向朝外的源，在域内\textbf{数学上不可认证}
（定理 2）。此时机器人无法证明该频道不存在，只能继续搜索直至预算耗尽。
是否为此付出域外补测的代价（时间约 $\times2.4$）是一个策略选择，
本文默认不付出，并在正文中如实说明。"""
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("verification report updated")
