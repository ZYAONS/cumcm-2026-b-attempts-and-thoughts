# -*- coding: utf-8 -*-
"""final_tidy.py -- 收尾：删掉残留旧值 + 把新增的 Q1 小节压缩到不超过 30 页正文。"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ok = 0

# 1) 残留的 48.4
for f in ("paper_p1.tex", "paper_p3.tex"):
    p = os.path.join(HERE, f)
    s = io.open(p, encoding="utf-8").read()
    for a, b in (("48.4\\%", "55.7\\%"), ("0.484", "0.557"), ("48.4%", "55.7%")):
        if a in s:
            s = s.replace(a, b)
            ok += 1
            print("  ok 48.4->55.7 in", f)
    io.open(p, "w", encoding="utf-8").write(s)

# 2) 压缩新插入的 Q1 小节：把表格改成行内叙述
p = os.path.join(HERE, "paper_p2.tex")
s = io.open(p, encoding="utf-8").read()
start = s.find(r"\begin{table}[H]" + "\n" + r"\centering" + "\n"
               + r"\caption{环形站位布局下直径圆的覆盖率")
end = s.find(r"\end{table}", start) + len(r"\end{table}")
if start > 0 and end > start:
    new = (r"数值复算（各 400 组，$\varepsilon=1^\circ$，目标域用 60 边形外近似）给出："
           r"等半径正 $n$ 边形环绕（半径 600/1000/1400 m）时覆盖率分别为 "
           r"$n=2$：$99.5\%\sim100\%$、$n=3$：\textbf{$0.0\%$}、$n=4$：$72.5\%\sim77.5\%$、"
           r"$n=5$：\textbf{$0.0\%$}；半径随机的环绕为 $100\%/95.0\%/88.2\%/95.0\%$；"
           r"而我们表 \ref{tab:q1cover} 的随机布局为 $96.5\%/95.0\%/94.8\%/95.0\%$。")
    s = s[:start] + new + s[end:]
    io.open(p, "w", encoding="utf-8").write(s)
    ok += 1
    print("  ok Q1 表格改为行内叙述")
else:
    print("  !! Q1 表格锚点未找到")

# 3) 再压一点点：两张宽图缩 8%
for f in ("paper_p2.tex", "paper_p3.tex"):
    p = os.path.join(HERE, f)
    s = io.open(p, encoding="utf-8").read()
    s = s.replace("width=0.78\\textwidth", "width=0.72\\textwidth")
    s = s.replace("width=0.76\\textwidth", "width=0.70\\textwidth")
    io.open(p, "w", encoding="utf-8").write(s)
print("完成 %d 项" % ok)
sys.exit(0)
