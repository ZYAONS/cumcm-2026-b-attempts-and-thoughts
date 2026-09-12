# -*- coding: utf-8 -*-
"""fix_legend_helper.py -- allow figure_legend() to take handles that already
carry their own labels."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
old = '''def figure_legend(fig, handles, labels, ncol=3, y=0.02, fontsize=13):
    """One legend for the whole figure, below all panels."""
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, y),
               ncol=ncol, frameon=False, fontsize=fontsize, handlelength=1.8,
               columnspacing=1.5)'''
new = '''def figure_legend(fig, handles, labels=None, ncol=3, y=0.02, fontsize=13):
    """One legend for the whole figure, below all panels.

    `labels` may be omitted when every handle already carries its own label.
    """
    if labels is None:
        labels = [h.get_label() for h in handles]
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, y),
               ncol=ncol, frameon=False, fontsize=fontsize, handlelength=1.8,
               columnspacing=1.5)'''
assert old in s, "anchor missing"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
