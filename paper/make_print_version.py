# -*- coding: utf-8 -*-
"""make_print_version.py -- 由同一份 paper.tex 生成纸质版（含承诺书与编号专用页）。

电子版：\documentclass[withoutpreface,bwprint]{cumcmthesis}  第一页为摘要页
纸质版：\documentclass{cumcmthesis}                          第一页承诺书、第二页编号页
"""
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
