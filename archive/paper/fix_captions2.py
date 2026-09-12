# -*- coding: utf-8 -*-
"""fix_captions2.py -- the captions still describe the old inset layout."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s:
            print("  WARN anchor missing in", fname, ":", a[:40])
            continue
        s = s.replace(a, b, 1)
        print("  ok in", fname)
    io.open(p, "w", encoding="utf-8").write(s)


edit("paper_p2.tex", [
    ("""\\caption{双站交会定位的定位区域：两条实测示向度方向线（实线）及其 $\\pm1^{\\circ}$ 边界线（虚线）围成凸四边形；右下角为定位区域的局部放大，黑色实线段为直径 $D$，虚线圆为“以 $D$ 为直径的圆”，点线圆为最小包围圆}""",
     """\\caption{双站交会定位的定位区域。(a) 整体几何：两条实测示向度方向线（实线）及其 $\\pm1^{\\circ}$ 边界线（虚线）围成凸四边形；(b) 定位区域的独立放大面板（$x,y$ 轴刻度放大到米级），黑色粗实线段为直径 $AB$，黑色虚线圆为“以 $AB$ 为直径的圆”，紫色点线圆为最小包围圆}"""),
    ("""\\caption{按本文规则选择第二检测点后，三个不同真实距离下的定位区域形状（红）：真实距离越远，定位区域越大，最坏情形出现在 1500 m}""",
     """\\caption{按本文规则选择第二检测点后的定位区域。(a) 几何总览：$S_1$、最优第二检测点 $S_2^{*}$ 与三个不同距离的干扰源位置（颜色与 (b)(c)(d) 的标题对应）；(b)(c)(d) 为对应的定位区域放大面板（红色多边形），真实距离越远定位区域越大，最坏情形出现在 1500 m}"""),
])
print("captions updated")
