# -*- coding: utf-8 -*-
"""fix_docs7.py -- the final two overfull boxes."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s:
            print("  !! missing: %s" % a[:46].replace("\n", " "))
            continue
        s = s.replace(a, b, 1)
        print("  ok %s" % a[:46].replace("\n", " "))
    io.open(p, "w", encoding="utf-8").write(s)


edit("code_walkthrough.tex", [
    ("        所有图内中文标签集中在 \\texttt{zh\\_labels.json}（100 个键），由 \\texttt{T(key)} 读取，\n"
     "        因此源码在任何编码环境下都不会乱码，改标签也不必动代码。",
     "        所有图内中文标签集中在一个外部文件里（\\texttt{zh\\_labels.json}，100 个键），\n"
     "        由 \\texttt{T(key)} 读取，因此源码不会乱码，改标签也不必动代码。"),
])

edit("simulator_spec.tex", [
    ("全部 & --- & real\\_timestamp\\_ms, virtual\\_time\\_s & 每个成功响应都带 \\\\",
     "全部 & --- & real\\_timestamp\\_ms,\\newline virtual\\_time\\_s & 每个成功响应都带 \\\\"),
])
print("done")
