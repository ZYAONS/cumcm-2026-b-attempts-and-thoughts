# -*- coding: utf-8 -*-
"""fix_optional_overfull.py -- the new summary table is 131 pt too wide and the
negative list rows are a few points over."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "optional_changes.tex")
s = io.open(p, encoding="utf-8").read()

# the new wide summary table -> shrink to \small and give fixed columns
a = r"""\begin{center}
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
b = r"""\begin{center}
\small
\begin{tabular}{p{4.6cm}p{3.4cm}p{3.0cm}p{4.4cm}}
\toprule
 & 完成率 & 平均时间/s & 说明 \\ \midrule
问题三 演练 60 例 & \textbf{1.0000} & 326.8 & 搜索成本被更多目标分摊 \\
问题三 正式测试 3 次 & 15/15、12/12、10/10 & 257.5 / 392.0 / 389.1 & 均值 346.2 s \\
问题四 演练 60 例（混合） & \textbf{1.0000} & 888.3 & 此前 0.9574 / 661.0 s（错误认证） \\
问题四 演练 30 例（全定向） & \textbf{1.0000} & 983.4 & 此前 0.9164 / 835.2 s \\
问题四 演练 30 例（全全向） & 1.0000 & 860.6 & --- \\
问题四 正式测试 3 次 & \textbf{11/11、12/12、11/11} & 1133.1 / 945.2 / 1193.4 & 三局全部清除 \\
问题四 灵敏度（8 组扰动） & \textbf{全部 1.000} & 711$\sim$1125 & 不依赖单一参数取值 \\
贪心对照（问题四，30 例） & 0.5654 & --- & 无认证判据时大幅下降 \\
\bottomrule
\end{tabular}
\end{center}"""
if a in s:
    s = s.replace(a, b, 1)
    print("summary table resized")
else:
    print("!! summary table anchor missing")

# widen the negative-list longtable slightly
s = s.replace(r"\begin{longtable}{p{0.5cm}p{3.7cm}p{3.4cm}p{3.2cm}p{2.6cm}}",
              r"\begin{longtable}{p{0.6cm}p{3.6cm}p{3.3cm}p{3.2cm}p{2.6cm}}")
io.open(p, "w", encoding="utf-8").write(s)
print("done")
