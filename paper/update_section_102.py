# -*- coding: utf-8 -*-
"""update_section_102.py -- §10.2 items 1 and 2 have now been addressed
experimentally; items 3 and 4 were assessed and found not to need modelling.
Rewrite the subsection accordingly and point to the new report."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p3.tex")
s = io.open(p, encoding="utf-8").read()

start = s.index("\\subsection{模型缺点与改进方向}")
end = s.index("\\subsection{推广}")

new = r"""\subsection{模型缺点与改进方向}

针对上一版列出的四个方向，本轮把它们逐一做成\textbf{可开关的实现}并在同一算例池上实测
（完整记录见支撑材料 \texttt{docs/optional\_changes.pdf}：11 项尝试中 3 项有效、
6 项为负优化、2 项无效）。结论如下。

\textbf{(1) 完成率损失——已解决。} 该损失此前被归因于"贴边且朝外的定向源在域内不可认证"，
但诊断显示真实原因在更上游：\\
(i) 末段三次观测点\textbf{近乎共线}（归航沿直线走），共线的方位测量无法约束距离，
最小包围圆半径因此停在 77 m，而末段清除图案的半径取 $0.55\sigma\approx42$ m，
图案点没有一个落进 20 m 清除半径；\\
(ii) 图案扫完后机器人停在\textbf{最后一个外圈点}上，该点可能位于定向源的\textbf{背光侧}，
随后的原地复测必然无声，循环空转直至预算耗尽。\\
两处修复分别是：\textbf{垂向截断测量}（图案失败时从垂直于视线的方向补一次观测，
$\sigma$ 由 77 m 降到 \textbf{1 m}）与\textbf{自适应沿射线站位}（第二站位偏移角随失败次数收缩，
最终回到射线上——由射线逼近引理保证必定受光）。在\textbf{从未参与调参的独立算例池}
（40 例）上，完成率由 $0.9945$ 升到 $\mathbf{1.0000}$（最差由 $0.8462$ 升到 $1.0000$），
平均时间同时下降 \textbf{38.2\%}。\textbf{真正的解不是域外采样，而是把定位做准、把站位放对。}

\textbf{(2) 路径规划的耦合——部分有效。} 把"清除顺序影响后续探测"具体化为两个可实现的耦合：
顺路清除（巡访站位时清除近旁的已知源）与自适应补测间隔（未解算频道多时缩短补测间隔）。
24 例对照：前者 $881.3\to882.2$ s（\textbf{无效}，说明任务排序中的优先权偏置已隐含实现了该耦合），
后者 $881.3\to\mathbf{852.1}$ s（$-3.3\%$，已默认启用）。因此本文的路径规划仍属启发式，
但"耦合未被利用"这一自评偏保守。

\textbf{(3) 误差独立同界——经检验无需建模。} 把示向度误差换成\textbf{空间相关}的平滑随机场
（波长 $1200\sim3000$ m，相关比例取 $0/50/80/100\%$）后，完成率与时间的差异落在运行波动范围内
（$a=100\%$ 时反而最好）。原因是结构性的：本文把每条读数当作\textbf{硬约束}
（真实方位落在 $\hat\theta\pm1^{\circ}$ 内），定位区域取全部约束之交、不确定度取最小包围圆半径，
该结论对\textbf{任意}满足逐条界的误差实现都成立，\textbf{与是否相关无关}。
相关性只影响"重测取平均"的收益，而本文重测的价值来自\textbf{交会角改善}而非误差平均。
（若改用卡尔曼滤波一类\textbf{统计}估计器，则必须先建模相关性。）

\textbf{(4) 真实时间耦合——本地环境判定无需建模，但在官方环境需复测。}
实测一次正式测试（问题四，799 次 HTTP 请求）的真实耗时为 5.18 s，
平均每请求 \textbf{6.48 ms}，相对 1200 s 上限有 \textbf{232 倍}余量；
即使计入仿真环境内部开销 19.63 s，余量仍有 61 倍。
但本结论只对本地模拟器成立：官方模拟器是 Windows 图形程序，其响应受界面刷新影响，
可能慢得多。本队无法获取官方模拟器（见第 10.1 节），故\textbf{无法实测}，
只能给出定量说法——官方每请求需比本地慢 230 倍以上才会触限。

"""
s = s[:start] + new + s[end:]
io.open(p, "w", encoding="utf-8").write(s)
print("section 10.2 rewritten")
