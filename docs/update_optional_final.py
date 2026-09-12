# -*- coding: utf-8 -*-
"""update_optional_final.py -- add the stale-bearing fix (the largest single win
of this round) and refresh the summary numbers."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "optional_changes.tex")
s = io.open(p, encoding="utf-8").read()

# ---- 1. new subsection: the stale bearing walk ---------------------------
anchor = "\\subsection{第 1 条的最终实测}"
new = r"""\subsection{有效改动 4：沿估计方向归航（本节最大的单项收益）}

在把前两项改动落地后，正式测试里仍有一个算例失败。追踪它时发现了\textbf{一个更基础的缺陷}：

\begin{lstlisting}[caption={案例 seed 910001、频道 18 的归航轨迹（修复前）}]
target channel 18 at (-1291.0, -445.1)  directional  dir=311 deg  R_eff=1448 m
>>> clear_channel(18) call #1  pos=(-1639.5,-178.0)  dist to TRUE source = 439.1 m
    estimate (-1287.4, -443.0) sigma=111.1  est error = 4.2 m      <-- 已定位到 4.2 m!
   [it1] walk 420 m -> (-818,  -43)     <-- 朝反方向走
   [it2] walk 420 m -> (-1140,-313)     <-- 走回来
   [it3] walk 189 m -> (-963, -164)     <-- 又走开
   ...
RESULT ratio=0.909   mean=1732.9 s   travel=65854 m
\end{lstlisting}

\textbf{机器人已经把一个源定位到 4.2 m（清除半径是 20 m），却在离它 400 多米的地方来回振荡。}

根因在归航步的方向计算上。原实现取\textbf{最后一条观测的方位角}，再从这个方位角
\textbf{从当前位置}前进——但方位角只在\textbf{测量它的那个点}上有意义。
本例中最后一条方位是在很远的位置测的，两者方向的夹角达 $58^{\circ}$，
于是每一步都把机器人送得更远；步长又按"过冲"规则逐步减半，
形成"走远—回退—再走远"的极限环，直到尝试预算耗尽。

\begin{keybox}[title=改动]
归航步改为\textbf{朝估计点前进}：$b=\operatorname{atan2}(\hat q_y-p_y,\ \hat q_x-p_x)$。
当机器人确实站在最后观测点附近时，两个方向本来就重合，因此没有任何损失；
当它不在时，朝估计点前进是唯一有意义的方向。
\end{keybox}

修复后同一算例：\textbf{ratio 0.909 $\to$ 1.000，平均时间 1732.9 s $\to$ 1133.1 s（$-35\%$）}，
归航稳定收敛（估计误差 4.0 m、$\sigma$ 由 18.9 降到 12，最终在 9.9 m 处清除）。

\begin{warnbox}[title=这条缺陷为什么值得单独记下来]
它不是被"更强的算法"修好的，而是被\textbf{把每一步的位置和目标打印出来}发现的。
三种改动（垂向截断、沿射线站位、朝估计点前进）里，最后这一条实现最简单、收益最大，
却最不容易靠读代码发现——因为"用最后一条方位前进"在\textbf{正常情况下}是对的
（机器人总是先走到观测点再前进），只有在异常路径上才暴露。
\textbf{任何迭代式控制都必须把"当前状态与判据"打出来看。}
\end{warnbox}

"""
assert anchor in s, "anchor missing"
s = s.replace(anchor, new + anchor, 1)

# ---- 2. refresh the final numbers ---------------------------------------
old_tbl = r"""\begin{center}
\begin{tabular}{lcccc}
\toprule
& 完成率 & 最差完成率 & 平均时间/s & 平均行程/m \\ \midrule
问题三 优化前 & 1.0000 & 1.0000 & 325.9 & 13456 \\
问题三 优化后 & 1.0000 & 1.0000 & 324.6 & 13414 \\
问题四 优化前 & 0.9940 & 0.9091 & 1382.9 & 68925 \\
问题四 优化后 & \textbf{1.0000} & \textbf{1.0000} & \textbf{901.0} & \textbf{45125} \\
\bottomrule
\end{tabular}
\end{center}"""
new_tbl = r"""\begin{center}
\begin{tabular}{lcccc}
\toprule
& 完成率 & 最差完成率 & 平均时间/s & 平均行程/m \\ \midrule
问题三 优化前 & 1.0000 & 1.0000 & 326.3 & 13490 \\
问题三 优化后 & 1.0000 & 1.0000 & 325.8 & 13448 \\
问题四 优化前 & 0.9981 & 0.9231 & 1377.6 & 67501 \\
问题四 优化后 & \textbf{1.0000} & \textbf{1.0000} & \textbf{871.3} & \textbf{41714} \\
\bottomrule
\end{tabular}
\end{center}

在演练池（问题三/四各 60 例）与正式测试上的最终结果：

\begin{center}
\begin{tabular}{lccc}
\toprule
& 完成率 & 平均时间/s & 说明 \\ \midrule
问题三 演练 60 例 & \textbf{1.0000} & 326.8 & 搜索成本被更多目标分摊 \\
问题三 正式测试 3 次 & 15/15、12/12、10/10 & 257.5 / 392.0 / 389.1 & 均值 346.2 s \\
问题四 演练 60 例（混合） & \textbf{1.0000} & 888.3 & 此前为 0.9574 / 661.0 s（错误认证） \\
问题四 演练 30 例（全定向） & \textbf{1.0000} & 983.4 & 此前为 0.9164 / 835.2 s \\
问题四 演练 30 例（全全向） & 1.0000 & 860.6 & --- \\
问题四 正式测试 3 次 & \textbf{11/11、12/12、11/11} & 1133.1 / 945.2 / 1193.4 & 三局全部清除 \\
问题四 灵敏度（8 组扰动） & \textbf{全部 1.000} & 711$\sim$1125 & 不依赖单一参数取值 \\
贪心对照（问题四，30 例） & 0.5654 & --- & 无认证判据时大幅下降 \\
\bottomrule
\end{tabular}
\end{center}"""
assert old_tbl in s, "summary table anchor missing"
s = s.replace(old_tbl, new_tbl, 1)

s = s.replace("\\textbf{3 项有效}（垂向截断测量、自适应沿射线站位、\n自适应补测间隔）",
              "\\textbf{4 项有效}（朝估计点归航、垂向截断测量、自适应沿射线站位、自适应补测间隔）")
s = s.replace("共尝试 11 项改动", "共尝试 12 项改动")
s = s.replace("\\textbf{6 项为负优化}（边境外补测、提高清除预算的三组参数、\n更大的末段半径、更密的格点），\\textbf{2 项无效}（顺路清除耦合、progress\\_ratio）。",
              "\\textbf{6 项为负优化}（边境外补测、提高清除预算的三组参数、更大的末段半径、更密的格点），"
              "\\textbf{2 项无效}（顺路清除耦合、progress\\_ratio）。")
s = s.replace("两项合起来使问题四在\\textbf{独立算例池}上的完成率由 $0.9940$ 升到\n\\textbf{$1.0000$}（最差由 $0.9091$ 升到 $1.0000$），同时平均时间下降 \\textbf{$34.8\\%$}。",
              "连同\\textbf{朝估计点归航}的修正，问题四在\\textbf{独立算例池}上的完成率由 $0.9981$ 升到 "
              "\\textbf{$1.0000$}（最差由 $0.9231$ 升到 $1.0000$），同时平均时间下降 \\textbf{$36.7\\%$}。")
io.open(p, "w", encoding="utf-8").write(s)
print("optional-changes report updated")
