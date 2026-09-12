# -*- coding: utf-8 -*-
"""fix_q34_legend.py -- avoid the legend overlapping the bars."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
a = ('    ax[1].legend(fontsize=12, loc="upper left")\n'
     '    ax[1].set_title(T("fig_q34_c"))\n'
     '    ax[1].grid(True, axis="y")\n'
     '    ax[1].set_ylim(0, max(tr + me) * 1.2)')
b = ('    ax[1].legend(fontsize=12, loc="upper left", framealpha=0.95)\n'
     '    ax[1].set_title(T("fig_q34_c"))\n'
     '    ax[1].grid(True, axis="y")\n'
     '    ax[1].set_ylim(0, max(tr + me) * 1.42)')
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
