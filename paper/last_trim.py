# -*- coding: utf-8 -*-
"""last_trim.py -- 最后压一页：把新增命题的证明压成一句话。"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p2.tex")
s = io.open(p, encoding="utf-8").read()
start = s.find(r"\begin{pf}" + "\n" + r"正 $n$ 边形的直径")
end = s.find(r"\end{pf}", start) + len(r"\end{pf}")
if start < 0 or end <= start:
    print("!! 锚点未找到")
    sys.exit(1)
new = (r"\emph{证明}：正 $n$ 边形的直径是对角线 "
       r"$D=2R_c\sin(\pi\lfloor n/2\rfloor/n)$，最小包围圆半径 $R_{\mathrm{MEC}}=R_c$，"
       r"相除即得 \eqref{eq:ngon}；$\sin(\pi\lfloor n/2\rfloor/n)=1$ 当且仅当 "
       r"$\lfloor n/2\rfloor/n=1/2$，即 $n$ 为偶数。$\blacksquare$")
s = s[:start] + new + s[end:]
io.open(p, "w", encoding="utf-8").write(s)
print("证明已压成一句")
