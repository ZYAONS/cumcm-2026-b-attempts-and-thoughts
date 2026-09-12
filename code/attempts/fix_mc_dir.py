# -*- coding: utf-8 -*-
"""fix_mc_dir.py -- finish the two remaining crowded figures."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

# Monte-Carlo: short y label on the right panel + one figure-level legend
s = s.replace('''    ax[1].set_xlabel(T("r_m"))
    ax[1].set_ylabel(T("D_m"))
    ax[1].grid(True)
    ax[1].set_title(T("fig_q2_mc2s"))
    legend_below(ax[1], ncol=2, y=-0.36)
    fig.tight_layout(w_pad=3.0)
    save(fig, "fig_q2_montecarlo.png")''',
              '''    ax[1].set_xlabel(T("r_m"))
    ax[1].set_ylabel("$D$ / m")
    ax[1].grid(True)
    ax[1].set_title(T("fig_q2_mc2s"))
    h = [Line2D([], [], color="tab:green", marker=".", ls="", ms=10, label="单次抽样"),
         Line2D([], [], color="k", lw=3.2, label="分箱中位数")]
    fig.tight_layout(w_pad=3.5)
    figure_legend(fig, h, ncol=2, y=-0.02)
    fig.subplots_adjust(bottom=0.30)
    save(fig, "fig_q2_montecarlo.png")''', 1)

# directional panel (a): move the note to the empty lower-left corner
s = s.replace('''    ax.annotate(T("fig_dir_silent"), (-900, -300), textcoords="offset points",
                xytext=(-28, 70), fontsize=12.5,
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.4))''',
              '''    ax.annotate(T("fig_dir_silent"), (-900, -300), textcoords="offset points",
                xytext=(-46, -78), fontsize=12.5,
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.4))''', 1)
s = s.replace('''    ax.set_ylim(-1400, 1250)
    ax.grid(True)
    ax.tick_params(labelsize=12)
    ax.set_title(T("fig_dir1"), fontsize=14)''',
              '''    ax.set_ylim(-1500, 1250)
    ax.grid(True)
    ax.tick_params(labelsize=12)
    ax.set_title(T("fig_dir1"), fontsize=14)''', 1)
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
