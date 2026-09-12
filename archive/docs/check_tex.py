# -*- coding: utf-8 -*-
"""check_tex.py -- find math-mode characters used in text mode (a common source
of "Missing $ inserted"), skipping verbatim/listing environments and maths."""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BAD = re.compile(r"(?<!\\)[_^&]")           # unescaped _ ^ & in text mode


def check(fname):
    lines = io.open(os.path.join(HERE, fname), encoding="utf-8").read().split("\n")
    env = None
    depth = 0                                   # $ ... $ nesting
    for i, raw in enumerate(lines):
        l = raw
        if env:
            if ("\\end{%s}" % env) in l:
                env = None
            continue
        m = re.search(r"\\begin\{(lstlisting|verbatim|tikzpicture|equation|align|aligned|tabular|longtable|center)\}", l)
        if m and m.group(1) in ("lstlisting", "verbatim", "tikzpicture"):
            env = m.group(1)
            continue
        if l.strip().startswith("%"):
            continue
        # strip inline maths and inline verbatim
        stripped = re.sub(r"\$[^$]*\$", "", l)
        stripped = re.sub(r"\\texttt\{[^}]*\}", "", stripped)
        stripped = re.sub(r"\\lstinline\|[^|]*\|", "", stripped)
        for mm in BAD.finditer(stripped):
            print("%s:%d: '%s'  |  %s" % (fname, i + 1, mm.group(0), l.strip()[:90]))


for f in sys.argv[1:]:
    check(f)
print("scan finished")
