# -*- coding: utf-8 -*-
"""polish_panels2.py -- last spacing fixes for the two reworked figures."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

# more room between the panels and the shared legend; legend a bit lower
s = s.replace('''        ncol=3, y=0.005)
    fig.subplots_adjust(bottom=0.28)
    save(fig, "fig_q2_region_rule.png")''',
              '''        ncol=3, y=-0.03)
    fig.subplots_adjust(bottom=0.36)
    save(fig, "fig_q2_region_rule.png")''', 1)
# shift the S2 label and the 1400 m tag apart in the overview panel
s = s.replace('''    ax.annotate("$S_2^{*}$", sol["S2"], textcoords="offset points", xytext=(12, 10),
                fontsize=16)''',
              '''    ax.annotate("$S_2^{*}$", sol["S2"], textcoords="offset points", xytext=(-64, 12),
                fontsize=16)''', 1)
s = s.replace('''                    xytext=(16, -4) if i == 0 else ((20, 8) if i == 1 else (14, 14)),''',
              '''                    xytext=(18, -8) if i == 0 else ((24, 6) if i == 1 else (10, 20)),''', 1)
# legend of the Q1 figure slightly lower as well
s = s.replace('''        ncol=3, y=-0.01)
    fig.subplots_adjust(bottom=0.26)
    save(fig, "fig_q1_region.png")''',
              '''        ncol=3, y=-0.02)
    fig.subplots_adjust(bottom=0.30)
    save(fig, "fig_q1_region.png")''', 1)
io.open(p, "w", encoding="utf-8").write(s)
print("spacing fixed")
