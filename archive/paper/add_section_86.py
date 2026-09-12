# -*- coding: utf-8 -*-
"""add_section_86.py -- add section 8.6 documenting the verification round and
the corrected certification, right before the sensitivity comparison section."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p3.tex")
s = io.open(p, encoding="utf-8").read()

anchor = "\\subsection{灵敏度与稳健性}"
assert anchor in s, "anchor missing"

new = r"""\subsection{模拟器验证与认证判据的修正}\label{sec:verify}

本节的数字全部来自"本地协议一致模拟器"（原因见第 10 节），因此在给出结论之前，
必须先说明该模拟器本身被验证到什么程度。

\subsubsection{验证范围}

本文实现了一个 68 项检查的验证套件，覆盖七类：

\begin{center}
\begin{tabular}{clcp{6.4cm}}
\toprule
组 & 覆盖范围 & 项数 & 代表检查 \\ \midrule
A & HTTP 协议 & 18 & 路由、\texttt{Content-Type}/\texttt{Encoding} 校验、
请求体上限、字段白名单、身份绑定、坐标与频道取值域、\textbf{幂等重放}、
未进场/重复进场/退出后调用 \\
B & 虚拟时间记账 & 8 & 移动 $=d/5$、切换 $1$ s（同频道 $0$）、检测固定 $5$ s、
清除命中 $5$/未命中 $3$ s、清除不改频道、时钟单调 \\
C & 物理判据 & 16 & 源个数、频道互异、$R_{\rm eff}\in[1000,1500]$、面积均匀采样、
超距静默、$5$ m 内 \texttt{near}、\textbf{误差上界与同点重测一致}、
清除半径 $20$ m 边界、定向半平面含边界、反侧静默、清除与角度无关 \\
D & 响应与日志契约 & 8 & 三个时限回传、三态/两态取值、日志字段与成本分解 \\
E & \textbf{与开源实现交叉对照} & 5 & 12 个常量逐项相等、300 步随机动作\textbf{逐步}成本相等 \\
F & 守恒律 & 4 & 日志分量之和 $=$ 最终虚拟时钟、行程守恒 \\
G & \textbf{增量认证等价性} & 5 & 每次扫描与"从零重算"逐次比对（60 次调用） \\
H & 策略级保证 & 4 & 保证发现（格点覆盖半径）、七点覆盖闭式条件、
贴边点域内不可认证、凸包判据与叉积法一致 \\
\bottomrule
\end{tabular}
\end{center}

\textbf{结果：68/68 通过。} 过程中抓出并修复了 3 个真实缺陷：

\begin{enumerate}[leftmargin=1.8em]
  \item \texttt{robot\_id} 在服务启动未指定时形同虚设——HTTP 层只检查启动参数，
        不检查首次 \texttt{/enter} 绑定的身份。已改为在首次成功进场时绑定；
  \item 示向度四舍五入到两位小数后可突破 $\pm1^{\circ}$ 硬上界（最大 $1.0024^{\circ}$）。
        已改为舍入后再向真值回收，20000 个样本最大偏差 $0.99985^{\circ}$；
  \item \textbf{认证扫描的"未认证位置"列表被一个早退优化截断}——
        某频道在某个候选位置失败后，它在后续所有候选位置都被跳过，
        因此这些位置不进入未认证集合。实测一次调用中真实未认证点 1253 个，
        而返回的只有 \textbf{1} 个。终止判据（"是否还有未认证点"）本身仍正确，
        但\textbf{规划器长期在残缺的未认证区域上决策}。
\end{enumerate}

第 3 条由"增量实现必须等于暴力重算"这一检查逼出（第一次运行即报
\texttt{brute 1 vs incremental 1253}）；修好后不仅纠正了完整性，
还把单局 CPU 由 41 s 降到 2.8 s。

\subsubsection{与开源实现的交叉对照}

调研发现一份\textbf{专门针对本题}的开源工程（官方模拟器的驱动与离线 mock，
MIT 许可，作者为双盲评审做了脱敏）。把它当作独立参照，逐项对照：

\begin{center}
\begin{tabular}{lcc}
\toprule
量 & 参考实现 & 本文模拟器 \\ \midrule
速度 / 切换 / 检测 / 清除命中 / 未命中 & $5$ m/s / $1$ s / $5$ s / $5$ s / $3$ s & 完全相同 \\
\texttt{near} / 清除半径 / 场地半径 & $5$ m / $20$ m / $1800$ m & 完全相同 \\
接收半径 / 源个数 / 两个时长上限 & $[1000,1500]$ / $[10,16]$ / $360000,1200$ & 完全相同 \\
\textbf{成本模型} & 逐式实现为参照 & \textbf{300 步随机动作逐步偏差 $<10^{-9}$ s} \\
示向度误差 & 每次调用\textbf{重新随机} & \textbf{地点函数}（附件 1 要求同点一致） \\
\bottomrule
\end{tabular}
\end{center}

唯一的实质分歧是误差模型：该 mock 每次测量重新随机，因此"在同一点重测取平均"
会虚假地降低误差；附件 1 明确"同一地点重复测量结果相同"，本文按其实现。
这一点会改变策略选择，故如实记录。

\subsubsection{修正对结果的影响}

修正后重新调参（坐标下降，并在\textbf{从未参与调参的独立算例池}上验收）：

\begin{center}
\begin{tabular}{lcccc}
\toprule
& 完成率 & 最差完成率 & 平均时间/s & 平均行程/m \\ \midrule
问题四 修正前（错误认证） & 0.9574 & 0.8333 & 661.0 & 28476 \\
问题四 修正后（独立池 40 例） & \textbf{0.9935} & 0.9091 & 1476.1 & 73064 \\
问题四 修正 $+$ 调参（独立池 40 例） & 0.9893 & 0.8182 & \textbf{1018.1} & \textbf{49119} \\
\bottomrule
\end{tabular}
\end{center}

必须如实说明：\textbf{"修正前"的 661.0 s 是在残缺认证下"提前宣布完成"得到的}——
机器人因为看不到大部分未认证区域而过早停机，代价是漏掉约 4\% 的干扰源。
修正后完成率提升到 $0.99$ 量级，但搜索必须真正走完，时间随之上升；
在此基础上再做参数与算法优化（抑制无谓搜索站位等），
把时间从 1476 s 压回 1018 s（$-31\%$）、行程减少 $33\%$。

\begin{keybox}[title=训练池上出现的"44\% 提升"是如何被否掉的]
第一轮寻优显示"站位半径 $1280\to1250$ 使平均时间下降 44\%"。在独立算例池上复算只有
1.7\%。根因是寻优脚本把算例池只生成一次并复用，而 \texttt{Arena} 会\textbf{就地清除}
传入的 \texttt{Source} 对象，于是第二次以后的每次评估都跑在"已被清空的算例"上
（完成率恒为 1.0、时间虚低）。该脚本现已改为每次评估都从种子重新生成算例，
并加入"同一配置连算两次必须同分"的守卫；否则脚本直接以返回码 2 退出。
\end{keybox}

\subsubsection{三次正式测试（修正后）}

\begin{center}
\begin{tabular}{lcc}
\toprule
测试案例编码 & 清除干扰源个数 & 平均定位清除时间/s \\ \midrule
Q4-910001-0104050607081013171820 & 11（11） & 966.4 \\
Q4-910002-030405060809111215161920 & \textbf{12（12）} & 920.8 \\
Q4-910003-0102030711131415171819 & 11（11） & 1204.3 \\
\bottomrule
\end{tabular}
\end{center}

三局\textbf{全部清除}，此前漏掉的"贴边朝外"源在第 2 局被成功清除。

"""

s = s.replace(anchor, new + anchor, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("section 8.6 added")
