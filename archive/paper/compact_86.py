# -*- coding: utf-8 -*-
"""compact_86.py -- the verification section was 5 pages and pushed the body over
the 30 page limit; rewrite it in about one and a half pages.

Also replaces the keybox environment (defined only in the technical reports, not
in the paper preamble) by a plain emphasised paragraph.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p3.tex")
s = io.open(p, encoding="utf-8").read()

start = s.index("\\subsection{模拟器验证与认证判据的修正}")
end = s.index("\\subsection{灵敏度与稳健性}")

new = r"""\subsection{模拟器验证与认证判据的修正}\label{sec:verify}

本节数字来自"本地协议一致模拟器"（原因见第 10 节），故先说明该模拟器被验证到什么程度。
本文实现了一个 \textbf{68 项检查}的验证套件，覆盖：HTTP 协议与校验流水线（18 项）、
虚拟时间记账（8 项）、物理判据（16 项）、响应与日志契约（8 项）、
\textbf{与开源实现的交叉对照}（5 项）、守恒律（4 项）、
\textbf{增量认证的等价性}（5 项）、策略级保证（4 项）。\textbf{结果为 68/68 通过}，
过程中抓出并修复 3 个真实缺陷：

\begin{enumerate}[leftmargin=1.8em]
  \item \texttt{robot\_id} 在服务启动未指定时形同虚设（HTTP 层只检查启动参数，
        不检查首次进场绑定的身份）——已改为首次成功进场时绑定；
  \item 示向度四舍五入到两位小数后可突破 $\pm1^{\circ}$ 硬上界（实测最大 $1.0024^{\circ}$）
        ——已改为舍入后向真值回收，20000 样本最大偏差 $0.99985^{\circ}$；
  \item \textbf{认证扫描的"未认证位置"列表被一个早退优化截断}：某频道在一个候选位置
        失败后，它在后续所有候选位置都被跳过，因此这些位置不进入未认证集合
        （实测真实未认证点 1253 个、返回 1 个）。终止判据本身仍正确，
        但规划器长期在残缺区域上决策。该缺陷由"增量实现必须等于暴力重算"这一检查逼出，
        修好后单局 CPU 由 41 s 降至 2.8 s。
\end{enumerate}

与开源实现的对照方面，调研发现一份\textbf{专门针对本题}的公开工程（官方模拟器驱动与离线
mock，MIT 许可）。以其为独立参照：速度、切换、检测、清除命中/未命中、\texttt{near}、
清除半径、场地半径、接收半径、源个数、两个时长上限共 \textbf{12 个常量完全一致}；
把其成本公式独立实现后，本文模拟器执行 300 步随机动作的虚拟时间增量
\textbf{逐步偏差小于 $10^{-9}$ s}。唯一实质分歧是示向度误差：该 mock 每次测量重新随机，
而附件 1 要求"同一地点重复测量结果相同"，本文按附件 1 实现。

修正对结果的影响必须如实说明。此前报告的 $0.9574$ 与 $661.0$ s 是\textbf{在残缺认证下
"提前宣布完成"得到的}：机器人看不到大部分未认证区域而过早停机，代价是漏掉约 4\% 的干扰源。
修正后完成率升至 $0.99$ 量级，但搜索必须真正走完，时间随之上升；
再经参数与算法优化（抑制无法完成认证的无谓搜索站位等），在\textbf{从未参与调参的
独立算例池}（40 例）上把时间从 1476.1 s 压回 \textbf{1018.1 s}（$-31\%$）、
行程减少 $33\%$，完成率 $0.9893$。

\begin{center}
\begin{tabular}{lcccc}
\toprule
& 完成率 & 最差完成率 & 平均时间/s & 平均行程/m \\ \midrule
修正前（错误认证，演练池） & 0.9574 & 0.8333 & 661.0 & 28476 \\
修正后（独立池） & \textbf{0.9935} & 0.9091 & 1476.1 & 73064 \\
修正 $+$ 优化（独立池） & 0.9893 & 0.8182 & \textbf{1018.1} & \textbf{49119} \\
\bottomrule
\end{tabular}
\end{center}

还需记录一个被否掉的结论：第一轮寻优曾显示"站位半径 $1280\to1250$ 使平均时间下降 44\%"，
在独立池上复算只有 1.7\%。根因是寻优脚本把算例池只生成一次并复用，
而 \texttt{Arena} 会就地清除传入的 \texttt{Source} 对象，导致第二次以后的评估都跑在
"已被清空的算例"上。该脚本现已改为每次评估从种子重新生成算例，
并加入"同一配置连算两次必须同分"的守卫。

修正后的三次正式测试\textbf{三局全部清除}（11/11、\textbf{12/12}、11/11），
平均时间 966.4 s、920.8 s、1204.3 s；此前漏掉的"贴边朝外"源在第 2 局被成功清除。

"""

s = s[:start] + new + s[end:]
io.open(p, "w", encoding="utf-8").write(s)
print("section 8.6 compacted")
