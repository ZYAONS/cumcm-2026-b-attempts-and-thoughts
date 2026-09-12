# -*- coding: utf-8 -*-
"""fix_last_rows.py -- the two remaining table rows of the paper."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p3.tex")
s = io.open(p, encoding="utf-8").read()

pairs = [
    ("\\hspace{0pt}0911121516\\hspace{0pt}1920 & 12（12） & 920.8 & 4.3\\\\",
     "\\hspace{0pt}0911121516\\hspace{0pt}1920 & \\textbf{12（12）} & 945.2 & 5.9\\\\"),
]
for a, b in pairs:
    if a not in s:
        print("  !! missing:", a[:50])
        continue
    s = s.replace(a, b, 1)
    print("  ok:", a[:50])
io.open(p, "w", encoding="utf-8").write(s)
print("done")
