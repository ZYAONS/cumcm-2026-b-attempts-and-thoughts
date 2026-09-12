# -*- coding: utf-8 -*-
"""fix_mc_fig.py -- shorten the panel titles and separate the axes of the
Monte-Carlo figure."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
s = s.replace('''    ax[0].set_title(T("fig_q2_mc1"))''',
              '''    ax[0].set_title(T("fig_q2_mc1s"))''', 1)
s = s.replace('''    ax[1].set_title(T("fig_q2_mc2"))''',
              '''    ax[1].set_title(T("fig_q2_mc2s"))''', 1)
s = s.replace('''    legend_below(ax[1], ncol=2, y=-0.29)
    fig.tight_layout()
    save(fig, "fig_q2_montecarlo.png")''',
              '''    legend_below(ax[1], ncol=2, y=-0.36)
    fig.tight_layout(w_pad=3.0)
    save(fig, "fig_q2_montecarlo.png")''', 1)
io.open(p, "w", encoding="utf-8").write(s)

import json
lp = os.path.join(HERE, "zh_labels.json")
d = json.load(io.open(lp, encoding="utf-8-sig"))
d["fig_q2_mc1s"] = "(a) 直径分布（4000 次抽样）"
d["fig_q2_mc2s"] = "(b) 最坏情形出现在最远源"
io.open(lp, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
print("monte-carlo figure fixed")
