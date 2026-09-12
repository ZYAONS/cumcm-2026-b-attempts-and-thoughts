# -*- coding: utf-8 -*-
"""show_region.py -- print numbered source regions for inspection."""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
fname = sys.argv[1]
a, b = int(sys.argv[2]), int(sys.argv[3])
lines = io.open(os.path.join(HERE, fname), encoding="utf-8").read().split("\n")
for i in range(max(0, a - 1), min(len(lines), b)):
    print("%4d %s" % (i + 1, lines[i]))
