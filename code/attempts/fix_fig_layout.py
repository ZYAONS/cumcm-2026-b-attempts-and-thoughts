# -*- coding: utf-8 -*-
"""fix_fig_layout.py -- resolve the remaining layout collisions in the figures."""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

pairs = [
    # 1) Q1 region: put the legend top-left, the inset bottom-centre, widen limits
    ('axin = ax.inset_axes([0.055, 0.60, 0.36, 0.36])',
     'axin = ax.inset_axes([0.34, 0.055, 0.33, 0.31])'),
    ('        loc="upper right", framealpha=0.95)\n    save(fig, "fig_q1_region.png")',
     '        loc="upper left", framealpha=0.95, borderpad=0.5)\n'
     '    save(fig, "fig_q1_region.png")'),
    ('    ax.set_xlim(-220, 1560)\n    ax.set_ylim(-260, 1290)',
     '    ax.set_xlim(-260, 1650)\n    ax.set_ylim(-300, 1420)'),
    # 2) case maps: leave room for the source labels near the rim
    ('    ax.set_xlim(-2050, 2050)\n    ax.set_ylim(-2150, 2050)',
     '    ax.set_xlim(-2150, 2300)\n    ax.set_ylim(-2250, 2150)'),
    # 3) coverage figure: legend outside the curve area
    ('    ax.legend(fontsize=12, loc="upper left")\n    ax.set_title(T("fig_cov2"), fontsize=15)',
     '    ax.legend(fontsize=12, loc="lower right")\n    ax.set_title(T("fig_cov2"), fontsize=15)'),
    # 4) Q2 geometry: legend below the axes to avoid covering the feasible set
    ('        loc="lower left", framealpha=0.95)\n    save(fig, "fig_q2_geometry.png")',
     '        loc="upper left", framealpha=0.95)\n    save(fig, "fig_q2_geometry.png")'),
    # 5) Q2 baselines: legend above the bars
    ('    ax.legend(loc="upper left")\n    ax.set_ylim(8, 6000)',
     '    ax.legend(loc="upper center", ncol=2, framealpha=0.95)\n    ax.set_ylim(8, 20000)'),
    # 6) sensitivity: wider left margin for the long tick labels
    ('        fig, ax = plt.subplots(1, 2, figsize=(9.4, 4.2))\n'
     '        b0 = ax[0].barh(ypos, mt, color="tab:orange", height=0.6)',
     '        fig, ax = plt.subplots(1, 2, figsize=(10.2, 4.4))\n'
     '        b0 = ax[0].barh(ypos, mt, color="tab:orange", height=0.6)'),
]
for a, b in pairs:
    if a not in s:
        print("  WARN anchor missing:", a[:60].replace("\n", " "))
        continue
    s = s.replace(a, b, 1)
    print("  patched:", a[:50].replace("\n", " "))
io.open(p, "w", encoding="utf-8").write(s)
print("layout fixed")
