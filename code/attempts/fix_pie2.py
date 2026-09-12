# -*- coding: utf-8 -*-
"""fix_pie2.py -- drop the leader-line labels (the legend already lists every
slice with its percentage)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
old = """    for i, w in enumerate(wedges):
        if vals[i] / total < 0.05:
            ang = math.radians((w.theta1 + w.theta2) / 2.0)
            ax.annotate("%s %.1f%%" % (labels[i], 100.0 * vals[i] / total),
                        xy=(0.86 * math.cos(ang), 0.86 * math.sin(ang)),
                        xytext=(1.45 * math.cos(ang), 1.45 * math.sin(ang)),
                        fontsize=13, ha="center", va="center",
                        arrowprops=dict(arrowstyle="-", color="gray", lw=1.2))
"""
assert old in s, "anchor missing"
s = s.replace(old, "", 1)
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
