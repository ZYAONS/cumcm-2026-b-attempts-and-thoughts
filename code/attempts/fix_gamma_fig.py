# -*- coding: utf-8 -*-
"""fix_gamma_fig.py -- annotate the region where the first-order formula fails."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
a = """    ax.axvline(90, color="gray", ls="--", lw=2.0)
    ax.annotate(r"$\\gamma=90^\\circ$", xy=(90, 2600), xytext=(96, 2600),
                fontsize=15, color="gray")"""
b = """    ax.axvline(90, color="gray", ls="--", lw=2.0)
    ax.annotate(r"$\\gamma=90^\\circ$", xy=(90, 1900), xytext=(96, 1900),
                fontsize=15, color="gray")
    ax.annotate("$\\gamma>110^\\circ$ 时源已靠近某一站\\n一阶近似偏小（见正文）",
                xy=(140, 700), xytext=(112, 2200), fontsize=13, color="tab:red",
                arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=1.6),
                bbox=dict(fc="white", ec="tab:red", alpha=0.9))"""
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
