# -*- coding: utf-8 -*-
"""fix_docs5.py -- the last overfull boxes in the two new documents."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s:
            print("  !! missing in %s: %s" % (fname, a[:48].replace("\n", " ")))
            continue
        s = s.replace(a, b, 1)
        print("  ok %s" % a[:48].replace("\n", " "))
    io.open(p, "w", encoding="utf-8").write(s)


edit("code_walkthrough.tex", [
    # 性能表改定宽首列 + 缩短行标签
    ("\\begin{tabular}{llll}\n\\toprule\n环节 & 复杂度 & 单次耗时（实测） & 说明 \\\\ \\midrule",
     "\\begin{tabular}{p{3.5cm}p{3.5cm}p{2.8cm}p{4.4cm}}\n\\toprule\n环节 & 复杂度 & 单次耗时（实测） & 说明 \\\\ \\midrule"),
    ("完整一局（60 组演练） & --- & 0.3$\\sim$0.6 s & 本地内存模式 \\\\",
     "一局（内存模式） & --- & 0.3$\\sim$0.6 s & 60 组演练使用 \\\\"),
    ("完整一局（HTTP 模式） & --- & 1.3$\\sim$2.3 s & 约 1500 次请求 \\\\",
     "一局（HTTP 模式） & --- & 1.3$\\sim$2.3 s & 约 1500 次请求 \\\\"),
    # 工程约束条目：拆行
    ("  \\item \\textbf{可执行源码纯 ASCII，中文只在注释与外部数据文件}。所有图内中文标签集中在\n"
     "        \\texttt{zh\\_labels.json}（UTF-8-sig，100 个键），由 \\texttt{T(key)} 读取。\n"
     "        好处：源码在任何编码环境下都不会乱码，标签可以随时改而不用动代码逻辑。",
     "  \\item \\textbf{可执行源码纯 ASCII，中文只在注释与外部数据文件}。\n"
     "        所有图内中文标签集中在 \\texttt{zh\\_labels.json}（UTF-8-sig，100 个键），\n"
     "        由 \\texttt{T(key)} 读取。好处是源码在任何编码环境下都不会乱码，\n"
     "        标签可以随时修改而不必改动代码逻辑。"),
])

edit("simulator_spec.tex", [
    ("\\begin{longtable}{p{2.3cm}p{3.1cm}p{3.9cm}p{6.1cm}}",
     "\\begin{longtable}{p{2.2cm}p{2.9cm}p{3.6cm}p{6.0cm}}"),
    ("accepted, virtual\\_time\\_s,\\newline max\\_virtual\\_duration\\_s,\\newline max\\_real\\_duration\\_s &",
     "accepted,\\newline virtual\\_time\\_s,\\newline max\\_virtual\\_\\hspace{0pt}duration\\_s,\\newline max\\_real\\_\\hspace{0pt}duration\\_s &"),
])
print("done")
