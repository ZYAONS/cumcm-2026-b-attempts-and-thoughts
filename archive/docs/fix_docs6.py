# -*- coding: utf-8 -*-
"""fix_docs6.py -- close the last two overfull boxes."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s:
            print("  !! missing: %s" % a[:48].replace("\n", " "))
            continue
        s = s.replace(a, b, 1)
        print("  ok %s" % a[:48].replace("\n", " "))
    io.open(p, "w", encoding="utf-8").write(s)


edit("code_walkthrough.tex", [
    ("        所有图内中文标签集中在 \\texttt{zh\\_labels.json}（UTF-8-sig，100 个键），\n"
     "        由 \\texttt{T(key)} 读取。好处是源码在任何编码环境下都不会乱码，\n"
     "        标签可以随时修改而不必改动代码逻辑。",
     "        所有图内中文标签集中在 \\texttt{zh\\_labels.json}（100 个键），由 \\texttt{T(key)} 读取，\n"
     "        因此源码在任何编码环境下都不会乱码，改标签也不必动代码。"),
])

edit("simulator_spec.tex", [
    ("\\begin{longtable}{p{2.2cm}p{2.9cm}p{3.6cm}p{6.0cm}}",
     "\\begin{longtable}{p{2.1cm}p{2.8cm}p{3.5cm}p{5.9cm}}"),
])
print("done")
