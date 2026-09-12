# -*- coding: utf-8 -*-
"""refresh_86.py -- §8.6 still quotes the intermediate numbers; bring it in line
with the final ones and mention the two defects found after it was written."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p3.tex")
s = io.open(p, encoding="utf-8").read()

pairs = [
    ("修正后完成率升至 $0.99$ 量级，\n搜索必须真正走完；再经参数与算法优化（抑制无法完成认证的无谓搜索站位等），\n在\\textbf{从未参与调参的独立算例池}（40 例）上，平均时间由 1476.1 s 降至\n\\textbf{1018.1 s}（$-31\\%$）、行程减少 $33\\%$、完成率 $0.9893$。",
     "修正后搜索必须真正走完，时间随之上升；此后再做四轮改进，在\\textbf{从未参与调参的独立算例池}\n（40 例）上，平均时间由 1377.6 s 降至 \\textbf{871.3 s}（$-36.7\\%$）、行程减少 $38.2\\%$，\n完成率由 $0.9981$ 升到 \\textbf{$1.0000$}（最差由 $0.9231$ 升到 $1.0000$）。"),
    ("修正后三次正式测试\\textbf{三局全部清除}（11/11、\\textbf{12/12}、11/11），\n平均时间 966.4 s、920.8 s、1204.3 s。",
     "修正后三次正式测试\\textbf{三局全部清除}（11/11、12/12、11/11），\n平均时间 1133.1 s、945.2 s、1193.4 s。"),
    ("一并记录一个被否掉的结论：首轮寻优给出的\"下降 44\\%\"在独立池上只有 1.7\\%，\n根因是算例池被复用而 \\texttt{Arena} 会就地清除 \\texttt{Source} 对象；\n脚本已改为每次评估重新生成算例并加入可复现性守卫。",
     "此外在把上述改动落地后，追踪最后一个失败算例时又发现一个更基础的缺陷：\n归航按\"最后一条观测的方位角\"从\\textbf{当前位置}前进，而该方位只在测量它的那个点上有意义\n——偏差达 $58^{\\circ}$，机器人已把源定位到 4.2 m（清除半径 20 m）却在 400 m 外来回振荡。\n改为朝估计点前进后，该算例由 $0.909$ 变为 $1.000$、时间下降 $35\\%$。\n一并记录一个被否掉的结论：首轮寻优给出的\"下降 44\\%\"在独立池上只有 1.7\\%，\n根因是算例池被复用而 \\texttt{Arena} 会就地清除 \\texttt{Source} 对象；\n脚本已改为每次评估重新生成算例并加入可复现性守卫。"),
]
hit = 0
for a, b in pairs:
    if a not in s:
        print("  -- not found:", a[:56].replace("\n", " "))
        continue
    s = s.replace(a, b, 1)
    hit += 1
io.open(p, "w", encoding="utf-8").write(s)
print("%d replacements" % hit)
