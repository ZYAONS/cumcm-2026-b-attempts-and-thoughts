# -*- coding: utf-8 -*-
"""trim_86_more.py -- final compression of the verification section: keep the
findings and the numbers, drop the duplicated detail (it lives in the technical
report) so that the body returns to 30 pages."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p3.tex")
s = io.open(p, encoding="utf-8").read()

start = s.index("\\subsection{模拟器验证与认证判据的修正}")
end = s.index("\\subsection{灵敏度与稳健性}")

new = r"""\subsection{模拟器验证与认证判据的修正}\label{sec:verify}

本节数字来自"本地协议一致模拟器"（原因见第 10 节），故先说明其可信度。
本文实现了 \textbf{68 项检查}的验证套件（协议 18、时间记账 8、物理 16、响应契约 8、
与开源实现交叉对照 5、守恒律 4、增量认证等价性 5、策略级保证 4），
\textbf{68/68 通过}，并抓出修复三个真实缺陷：\texttt{robot\_id} 在服务未指定时形同虚设；
示向度四舍五入到两位小数后可突破 $\pm1^{\circ}$ 上界（实测 $1.0024^{\circ}$）；
以及\textbf{认证扫描的"未认证位置"列表被一个早退优化截断}（真实 1253 个点、返回 1 个，
规划器长期在残缺区域上决策）。第三条由"增量实现必须等于暴力重算"这一检查逼出，
修好后单局 CPU 由 41 s 降到 2.8 s。

交叉对照方面，调研发现一份专门针对本题的公开工程（官方模拟器驱动与离线 mock，MIT 许可）。
以它为独立参照：12 个物理/时间常量完全一致；把其成本公式独立实现后，
本文模拟器 300 步随机动作的虚拟时间增量\textbf{逐步偏差小于 $10^{-9}$ s}。
唯一实质分歧是误差模型——该 mock 每次测量重新随机，而附件 1 要求同一地点重复测量结果相同，
本文按附件 1 实现。

修正对结果的影响必须如实说明：此前报告的 $0.9574$ 与 $661.0$ s 是\textbf{在残缺认证下
提前宣布完成}得到的，代价是漏掉约 4\% 的干扰源。修正后完成率升至 $0.99$ 量级，
搜索必须真正走完；再经参数与算法优化（抑制无法完成认证的无谓搜索站位等），
在\textbf{从未参与调参的独立算例池}（40 例）上，平均时间由 1476.1 s 降至
\textbf{1018.1 s}（$-31\%$）、行程减少 $33\%$、完成率 $0.9893$。
一并记录一个被否掉的结论：首轮寻优给出的"下降 44\%"在独立池上只有 1.7\%，
根因是算例池被复用而 \texttt{Arena} 会就地清除 \texttt{Source} 对象；
脚本已改为每次评估重新生成算例并加入可复现性守卫。
修正后三次正式测试\textbf{三局全部清除}（11/11、\textbf{12/12}、11/11），
平均时间 966.4 s、920.8 s、1204.3 s。

"""

s = s[:start] + new + s[end:]
io.open(p, "w", encoding="utf-8").write(s)
print("section 8.6 compressed to narrative form")
