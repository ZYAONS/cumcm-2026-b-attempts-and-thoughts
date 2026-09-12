# -*- coding: utf-8 -*-
"""make_print_version.py -- build the paper version (with the commitment and the
numbering page) from the same source as the electronic version."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
s = io.open(os.path.join(HERE, "paper.tex"), encoding="utf-8").read()
old = "\\documentclass[withoutpreface,bwprint]{cumcmthesis}"
new = "\\documentclass{cumcmthesis}"
assert old in s, "class line not found"
s = s.replace(old, new, 1)
io.open(os.path.join(HERE, "paper_print.tex"), "w", encoding="utf-8").write(s)
print("paper_print.tex written")
