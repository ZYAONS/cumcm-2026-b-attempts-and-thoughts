# -*- coding: utf-8 -*-
"""caption_style.py -- Chinese style caption separator (a wide space, no colon)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "tech_common.tex")
s = io.open(p, encoding="utf-8").read()
a = "\\captionsetup{font=small,labelfont=bf}"
b = "\\captionsetup{font=small,labelfont=bf,labelsep=quad}"
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("caption style set to Chinese convention")
