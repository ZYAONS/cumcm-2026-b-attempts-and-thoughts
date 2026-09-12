# -*- coding: utf-8 -*-
"""fix_pie_text.py -- 让正文与饼图的占比一致（饼图：移动 61.9%、检测+切换 33.1%）。"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p3.tex")
s = io.open(p, encoding="utf-8").read()
pairs = [
    (r"\caption{问题三虚拟时间的构成：移动占主导（约 64\%），检测与频道切换约 34\%}",
     r"\caption{问题三虚拟时间的构成：移动占主导（约 62\%），检测与频道切换合计约 33\%}"),
    (r"图 \ref{fig:q3pie} 揭示了一个重要的工程结论：\textbf{移动时间占虚拟时间的约 64\%}，"
     r"而检测与频道切换合计约 34\%。",
     r"图 \ref{fig:q3pie} 揭示了一个重要的工程结论：\textbf{移动时间占虚拟时间的约 62\%}，"
     r"而检测与频道切换合计约 33\%。"),
]
ok = 0
for a, b in pairs:
    if a in s:
        s = s.replace(a, b, 1)
        ok += 1
    else:
        print("  !! 锚点未找到:", a[:60])
io.open(p, "w", encoding="utf-8").write(s)
print("更新 %d/%d" % (ok, len(pairs)))
sys.exit(0 if ok == len(pairs) else 1)
