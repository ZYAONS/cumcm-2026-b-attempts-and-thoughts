# -*- coding: utf-8 -*-
"""fix_fig_layout2.py -- second round of layout fixes."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

pairs = [
    # Q1 region: move the S1 label out of the inset area
    ('ax.annotate(T("fig_s1"), (0, 0), textcoords="offset points", xytext=(10, -26))',
     'ax.annotate(T("fig_s1"), (0, 0), textcoords="offset points", xytext=(-118, -34))'),
    # Q2 geometry: legend to the lower-left corner (free space), star stays visible
    ('        loc="upper left", framealpha=0.95)\n    save(fig, "fig_q2_geometry.png")',
     '        loc="lower left", framealpha=0.95)\n    save(fig, "fig_q2_geometry.png")'),
    # Q2 geometry: show the feasible set as a shaded sector so it is not hidden
    ('    ax.plot(xs, ys, ".", ms=3.2, color="tab:blue", alpha=0.75, zorder=2)',
     '    ax.plot(xs, ys, ".", ms=5.0, color="tab:blue", alpha=0.9, zorder=2,\n'
     '            markeredgecolor="white", markeredgewidth=0.6)'),
    # Q2 monte-carlo: legend inside the upper-left, bars may reach it
    ('    ax[0].legend(loc="upper right")\n    ax[0].grid(True, axis="y")',
     '    ax[0].legend(loc="upper right", framealpha=0.95)\n    ax[0].grid(True, axis="y")'),
]
for a, b in pairs:
    if a not in s:
        print("  WARN anchor missing:", a[:60].replace("\n", " "))
        continue
    s = s.replace(a, b, 1)
    print("  patched:", a[:52].replace("\n", " "))
io.open(p, "w", encoding="utf-8").write(s)
print("done")
