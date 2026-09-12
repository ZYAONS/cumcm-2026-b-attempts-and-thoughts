# -*- coding: utf-8 -*-
"""move_figs_to_appendix.py -- 方案 A：把 3 张诊断图从正文移到附录。

正文页数已被浮动体支配，缩小图只会让 LaTeX 用空白填页；把浮动体整体移出正文
才是确定性的减页手段。图的 label 不变，正文里的 \\ref 仍能正确解析。
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGETS = ["fig_q1_cover_stats", "fig_q3_errors", "fig_convergence"]
SRC = ["paper_p2.tex", "paper_p3.tex"]

moved = []
for fname in SRC:
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for name in TARGETS:
        i = s.find(name)
        if i < 0:
            print("  - %s 不在 %s" % (name, fname))
            continue
        a = s.rfind("\\begin{figure}", 0, i)
        b = s.find("\\end{figure}", i) + len("\\end{figure}")
        block = s[a:b]
        assert "figures/%s.png" % name in block, "块内未含图片文件名: %s" % name
        s = s[:a] + s[b:]
        # 清掉紧邻的空行，避免留出大段空白
        s = re.sub(r"\n{3,}", "\n\n", s)
        moved.append((name, block))
        print("  ✓ 移出 %s（%d 字符，来自 %s）" % (name, len(block), fname))
    io.open(p, "w", encoding="utf-8").write(s)

if not moved:
    print("!! 没有移动任何图")
    sys.exit(1)

# 追加到附录开头（支撑材料清单之后）
p4 = os.path.join(HERE, "paper_p4.tex")
t = io.open(p4, encoding="utf-8").read()
anchor = "\\section{补充图表}"
section = ["\\section{补充图表}", "",
           "以下三张图为正文中的诊断性插图，为控制正文篇幅移至此处；"
           "正文中对应的引用编号保持不变。", ""]
if anchor in t:
    print("  附录已存在补充图表节，直接追加")
    idx = t.find(anchor)
    # 插到该节标题之后
    ins = t.find("\n", idx) + 1
    t = t[:ins] + "\n" + "\n".join(section[2:]) + "\n" + \
        "\n\n".join(b for _, b in moved) + "\n" + t[ins:]
else:
    i = t.find("\\section{", t.find("\\appendix"))
    ins = t.find("\n", t.find("\\end{longtable}", i)) if i > 0 else len(t)
    if ins <= 0:
        ins = len(t)
    t = t[:ins] + "\n" + "\n".join(section) + "\n" + \
        "\n\n".join(b for _, b in moved) + "\n" + t[ins:]
io.open(p4, "w", encoding="utf-8").write(t)
print("已把 %d 张图移入附录「补充图表」" % len(moved))
