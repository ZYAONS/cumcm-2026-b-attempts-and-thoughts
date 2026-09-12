# -*- coding: utf-8 -*-
"""fix_after_shrink.py -- the smaller canvas made two legends collide with the
panel tick labels; give them more bottom room and shorten the tick labels."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

# --- fig_q34_stats: single line tick labels + deeper bottom margin ---------
s = s.replace('''    names = [T("q3_name"), T("q4_name")]
    vals = [a["q3"]["mean_time"], a["q4"]["mean_time"]]''',
              '''    names = [T("q3_name").replace("\\n", ""), T("q4_name").replace("\\n", "")]
    vals = [a["q3"]["mean_time"], a["q4"]["mean_time"]]''', 1)
s = s.replace('''    fig.tight_layout()
    figure_legend(fig, [b1, b2], [T("travel"), T("measure")], ncol=2, y=-0.015)
    fig.subplots_adjust(bottom=0.24)
    save(fig, "fig_q34_stats.png")''',
              '''    fig.tight_layout()
    figure_legend(fig, [b1, b2], [T("travel"), T("measure")], ncol=2, y=-0.03)
    fig.subplots_adjust(bottom=0.34)
    save(fig, "fig_q34_stats.png")''', 1)

# --- fig_q2_region_rule: legend lower --------------------------------------
s = s.replace('''        ncol=3, y=-0.03)
    fig.subplots_adjust(bottom=0.36)
    save(fig, "fig_q2_region_rule.png")''',
              '''        ncol=3, y=-0.05)
    fig.subplots_adjust(bottom=0.42)
    save(fig, "fig_q2_region_rule.png")''', 1)

# --- fig_q1_region: keep a little more room as well ------------------------
s = s.replace('''        ncol=3, y=-0.02)
    fig.subplots_adjust(bottom=0.30)
    save(fig, "fig_q1_region.png")''',
              '''        ncol=3, y=-0.04)
    fig.subplots_adjust(bottom=0.34)
    save(fig, "fig_q1_region.png")''', 1)
io.open(p, "w", encoding="utf-8").write(s)
print("spacing adjusted")
