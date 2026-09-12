# -*- coding: utf-8 -*-
"""update_paper_fast2.py -- bring the paper tables in line with the regenerated data."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    hit = 0
    for a, b in pairs:
        if a not in s:
            print("  -- not found: %s" % a[:58].replace("\n", " "))
            continue
        s = s.replace(a, b, 1)
        hit += 1
    io.open(p, "w", encoding="utf-8").write(s)
    print("  %s : %d replaced" % (fname, hit))


edit("paper_p3.tex", [
    ("全部为定向源 & 30 & \\textbf{1.0000} & 652.0\\\\",
     "全部为定向源 & 30 & \\textbf{1.0000} & 645.2\\\\"),
    ("全部为全向源 & 30 & 1.0000 & 583.0\\\\",
     "全部为全向源 & 30 & 1.0000 & 547.2\\\\"),
    # q4 sensitivity block
    ("基准 & 1.000 & 967.7\\\\", "基准 & 1.000 & 606.0\\\\"),
    ("有效接收半径下界 $1000\\to950$ m & 1.000 & 898.9\\\\",
     "有效接收半径下界 $1000\\to950$ m & 1.000 & 582.0\\\\"),
    ("有效接收半径下界 $1000\\to1050$ m & 1.000 & 876.2\\\\",
     "有效接收半径下界 $1000\\to1050$ m & 0.994 & 575.9\\\\"),
    ("有效接收半径上界 $1500\\to1400$ m & 1.000 & 880.4\\\\",
     "有效接收半径上界 $1500\\to1400$ m & 1.000 & 603.4\\\\"),
    ("测角误差 $1^{\\circ}\\to0.8^{\\circ}$ & 1.000 & 855.8\\\\",
     "测角误差 $1^{\\circ}\\to0.8^{\\circ}$ & 0.994 & 645.3\\\\"),
    ("干扰源个数固定为 10 & 1.000 & 1125.1\\\\",
     "干扰源个数固定为 10 & 1.000 & 746.9\\\\"),
    ("干扰源个数固定为 16 & 1.000 & 711.6\\\\",
     "干扰源个数固定为 16 & 1.000 & 507.1\\\\"),
    ("可见问题四的完成率在全部八组扰动下\\textbf{都保持 1.000}，说明该策略不依赖任何单一参数的精确取值；此前观察到的完成率损失已由末段定位的两项改进消除。",
     "可见问题四的完成率对模型参数不敏感（六组扰动为 1.000，两组为 0.994），"
     "说明该策略不依赖任何单一参数的精确取值。"),
])
print("done")
