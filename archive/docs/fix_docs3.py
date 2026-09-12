# -*- coding: utf-8 -*-
"""fix_docs3.py -- (1) escape _ ^ & inside \texttt{} (they are text, not maths),
(2) make the function tables wrap, (3) split the long return-value list."""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = ["code_walkthrough.tex", "simulator_spec.tex", "tech_q3.tex", "tech_q4.tex"]
TT = re.compile(r"\\texttt\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}")


def protect(fname):
    p = os.path.join(HERE, fname)
    lines = io.open(p, encoding="utf-8").read().split("\n")
    out, env, total = [], None, 0
    for l in lines:
        if env:
            if ("\\end{%s}" % env) in l:
                env = None
            out.append(l)
            continue
        m = re.search(r"\\begin\{(lstlisting|verbatim|tikzpicture)\}", l)
        if m:
            env = m.group(1)
            out.append(l)
            continue

        cnt = [0]

        def repl(mo):
            body = mo.group(1)
            new = re.sub(r"(?<!\\)([_^&])", r"\\\1", body)
            if new != body:
                cnt[0] += 1
            return "\\texttt{%s}" % new
        out.append(TT.sub(repl, l))
        total += cnt[0]
    io.open(p, "w", encoding="utf-8").write("\n".join(out))
    print("  %-24s 修正 %d 处 \\texttt 内的特殊字符" % (fname, total))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s:
            print("  !! missing in %s: %s" % (fname, a[:44].replace("\n", " ")))
            continue
        s = s.replace(a, b, 1)
        print("  ok %s: %s" % (fname, a[:44].replace("\n", " ")))
    io.open(p, "w", encoding="utf-8").write(s)


for f in FILES:
    protect(f)

edit("code_walkthrough.tex", [
    ("\\subsection{基础工具（40--62 行）}\n\n\\begin{tabular}{lp{10.6cm}}",
     "\\subsection{基础工具（40--62 行）}\n\n\\begin{tabular}{p{4.4cm}p{9.4cm}}"),
    ("\\subsection{直径与圆覆盖（265--347 行）}\n\n\\begin{tabular}{lp{10.6cm}}",
     "\\subsection{直径与圆覆盖（265--347 行）}\n\n\\begin{tabular}{p{4.6cm}p{9.2cm}}"),
    ("\\begin{tabular}{lp{10.6cm}}\n\\toprule\n函数 & 说明 \\\\ \\midrule\n"
     "\\texttt{sector\\_points}",
     "\\begin{tabular}{p{5.0cm}p{8.8cm}}\n\\toprule\n函数 & 说明 \\\\ \\midrule\n"
     "\\texttt{sector\\_points}"),
])
print("done")
