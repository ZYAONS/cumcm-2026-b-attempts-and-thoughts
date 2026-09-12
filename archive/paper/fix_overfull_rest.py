# -*- coding: utf-8 -*-
"""fix_overfull_rest.py -- eliminate the last overfull boxes:
  * a global emergencystretch so that CJK paragraphs with long inline maths can
    still be broken without visible gaps
  * narrower boxes and gaps in the framework diagram
  * two sentences rephrased
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s:
            print("  !! anchor missing in %s: %s" % (fname, a[:50].replace("\n", " ")))
            continue
        s = s.replace(a, b, 1)
        print("  ok  %s" % a[:50].replace("\n", " "))
    io.open(p, "w", encoding="utf-8").write(s)


edit("paper_p1.tex", [
    # global stretch for CJK paragraphs
    ("\\setlength{\\textfloatsep}{7pt plus 2pt minus 2pt}",
     "\\setlength{\\emergencystretch}{2.5em}\n"
     "\\setlength{\\textfloatsep}{7pt plus 2pt minus 2pt}"),
    # narrower diagram
    ("              minimum height=1.55cm, minimum width=3.05cm, fill=blue!6,",
     "              minimum height=1.50cm, minimum width=2.72cm, fill=blue!6,"),
    ("\\node[box, right=1.55cm of q1] (q2)", "\\node[box, right=1.20cm of q1] (q2)"),
    ("\\node[box, right=1.55cm of q2] (q3)", "\\node[box, right=1.20cm of q2] (q3)"),
    ("\\node[box, right=1.55cm of q3] (q4)", "\\node[box, right=1.20cm of q3] (q4)"),
    ("\\node[core, below=1.35cm of q2, xshift=1.55cm, minimum width=11.4cm] (core)",
     "\\node[core, below=1.30cm of q2, xshift=1.20cm, minimum width=10.4cm] (core)"),
    ("     {\\textbf{统一内核}：角度楔交会 $\\Rightarrow$ 定位区域（凸多边形）$\\Rightarrow$ 最小包围圆作位置不确定度 $\\sigma$};",
     "     {\\textbf{统一内核}：角度楔交会 $\\Rightarrow$ 定位区域（凸多边形）$\\Rightarrow$ 最小包围圆半径作不确定度 $\\sigma$};"),
])

edit("paper_p3.tex", [
    ("""设候选位置 $q$ 的 $R_{\\min}$ 邻域内已有一组返回 no\\_signal 的检测点 $\\{p_1,\\dots,p_k\\}$，即 $|p_j-q|\\le R_{\\min}$。则“存在某个定向方向 $u$，使该源躲过全部这些检测”等价于“存在一个半平面包含全部向量 $p_j-q$”。因此\\textbf{可以排除该干扰源}当且仅当""",
     """设候选位置 $q$ 的 $R_{\\min}$ 邻域内已有一组返回 no\\_signal 的检测点 $\\{p_1,\\dots,p_k\\}$，即 $|p_j-q|\\le R_{\\min}$。于是“存在某个定向方向 $u$，使该源躲过全部检测”等价于“存在一个半平面，包含全部向量 $p_j-q$”。因此\\textbf{可以排除该干扰源}当且仅当"""),
    ("""  \\item 覆盖数：Kershner\\cite{kershner1939}给出用等半径圆覆盖圆盘的经典结果与渐近覆盖密度 $3\\sqrt3/(2\\pi)\\approx1.2092$。用面积下界估计覆盖 1800 m 圆域所需 $R_{\\min}=1000$ m 的圆数：$1.2092\\times(1800/1000)^2=3.9$，而真正\\emph{保证}覆盖需要 7 个（定理 \\ref{thm:cover}）；这一差距正是“渐近密度”与“有限规模精确覆盖”的差别，本文采用后者以保证正确性。""",
     """  \\item 覆盖数：Kershner\\cite{kershner1939}给出用等半径圆覆盖圆盘的经典结果与渐近覆盖密度 $3\\sqrt3/(2\\pi)\\approx1.2092$。以面积比作下界估计，覆盖 1800 m 圆域大约需要 3.9 个 $R_{\\min}=1000$ m 的圆，而真正\\emph{保证}覆盖需要 7 个（定理 \\ref{thm:cover}）。这一差距正是“渐近密度”与“有限规模精确覆盖”的差别，本文采用后者以保证正确性。"""),
])
print("done")
