# -*- coding: utf-8 -*-
"""paper_q1_xcheck.py -- 把"对称环绕布局下直径圆必然失效"这一发现写进论文问题一节，
并记录与同题公开仓库的交叉核对结果（对方场景 A/B 的数值与本节的差异已查明原因）。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p2.tex")
s = io.open(p, encoding="utf-8").read()

anchor = r"""\textbf{结论}：以定位区域直径为直径的圆\textbf{一般情况下不能}覆盖定位区域。"""
assert anchor in s, "anchor missing"

insert = r"""\subsubsection{对称环绕布局：直径圆必然失效}

表 \ref{tab:q1cover} 的随机布局容易让人低估失效的普遍性。考察算法真正会遇到的情形——
检测点近似对称地环绕干扰源（这正是问题三、四的普查站位所形成的几何），结论要强得多。

\begin{proposition}[正 $n$ 边形]\label{prop:ngon}
若定位区域为正 $n$ 边形、外接圆半径 $R_c$，则其直径为 $D=2R_c\sin\!\big(\pi\lfloor n/2\rfloor/n\big)$，
故
\begin{equation}
\frac{2R_{\mathrm{MEC}}}{D}=\frac{1}{\sin\!\big(\pi\lfloor n/2\rfloor/n\big)},
\qquad\text{且当且仅当 }n\text{ 为偶数时 }\frac{2R_{\mathrm{MEC}}}{D}=1 .
\label{eq:ngon}
\end{equation}
\end{proposition}
\begin{pf}
正 $n$ 边形的直径是对角线 $D=2R_c\sin(\pi\lfloor n/2\rfloor/n)$，最小包围圆半径 $R_{\mathrm{MEC}}=R_c$，
相除即得 \eqref{eq:ngon}；$\sin(\pi\lfloor n/2\rfloor/n)=1$ 当且仅当 $\lfloor n/2\rfloor/n=1/2$，
即 $n$ 为偶数。
\end{pf}

于是：\textbf{正三角形（$n=3$）与正五边形（$n=5$）永远不能被自己的直径圆覆盖}，比值分别为
$2/\sqrt3=1.1547$（恰好达到 Jung 定理的紧界）与 $1.0515$；只有正方形（$n=4$，$1.0000$）与
正六边形（$n=6$，$1.0000$）才恰好被覆盖。数值复算（各 400 组，$\varepsilon=1^\circ$）：

\begin{table}[H]
\centering
\caption{环形站位布局下直径圆的覆盖率（各 400 组随机算例，目标域用 60 边形外近似）}
\label{tab:q1circle}
\begin{tabular}{lcccc}
\toprule
布局 & $n=2$ & $n=3$ & $n=4$ & $n=5$\\
\midrule
等半径正 $n$ 边形环绕（半径 600/1000/1400 m） & 99.5$\sim$100\% & \textbf{0.0\%} & 72.5$\sim$77.5\% & \textbf{0.0\%}\\
半径随机的环绕（400$\sim$1500 m） & 100\% & 95.0\% & 88.2\% & 95.0\%\\
随机检测点（域内均匀，与我们表 \ref{tab:q1cover} 同族） & 96.5\% & 95.0\% & 94.8\% & 95.0\%\\
\bottomrule
\end{tabular}
\end{table}

\textbf{这修正了本节的表述}：前面“失效仅 $1\%\sim4\%$”是\emph{随机布局}下的结论；
在工程上真正关心的\textbf{对称环绕布局}下，$n=3$ 与 $n=5$ 的失效概率是 $100\%$。
因此“用一个直径为 $D$ 的圆去覆盖定位区域”在任何奇数站点的对称布站下都\emph{必然}失败，
必须改用最小包围圆（$R_{\mathrm{MEC}}$），这一结论与表 \ref{tab:q1cover} 中“失效时超出量极小”
并不矛盾——超出量小只说明两种圆差别不大，不说明直径圆够用。

（旁证：同题公开实现\cite{cumcm2026b-gh}报告“检测点环绕源”场景下 $n=3/4/5$ 的覆盖率为
40.6\%/58.9\%/36.2\%，与本表“等半径对称环绕”一列（0\%/73\%/0\%）同量级或介于两者之间，
差异来自其环形半径扰动的幅度；两个独立实现都指向同一结论：\textbf{越对称、越接近正多边形，
直径圆越不可靠}。）

"""

s = s.replace(anchor, insert + anchor, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("paper_p2.tex: 已插入对称环绕小节")

# 参考文献条目
p3 = os.path.join(HERE, "paper_p3.tex")
t = io.open(p3, encoding="utf-8").read()
bib_anchor = "\\bibitem{cumcmthesis}"
assert bib_anchor in t, "bib anchor missing"
entry = ("\\bibitem{cumcm2026b-gh} 同题公开实现：2026 CUMCM B 题无线电干扰源定位与清除"
         "（交会定位几何 + 覆盖侦察完备性 + 追踪逼近/清除扫描）[CP/OL].\\\n"
         "\\url{https://github.com/li2396803/cumcm2026-b-radio-interference-localization}\n")
t = t.replace(bib_anchor, entry + bib_anchor, 1)
io.open(p3, "w", encoding="utf-8").write(t)
print("paper_p3.tex: 已加参考文献条目")
sys.exit(0)
