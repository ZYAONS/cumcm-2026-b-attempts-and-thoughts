# -*- coding: utf-8 -*-
"""fix_two_figs.py

  fig_coverage        : the shared legend sat on the two x labels -> more bottom
                        room and the legend pushed further down
  fig_q2_montecarlo   : the "theoretical worst-case bound" was printed inside the
                        histogram; move it into the figure-level legend
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

# ------------------------------------------------------------ coverage ----
a = """    fig.tight_layout()
    figure_legend(fig, h1 + h2, ncol=3, y=-0.015)
    fig.subplots_adjust(bottom=0.26)
    save(fig, "fig_coverage.png")"""
b = """    fig.tight_layout()
    figure_legend(fig, h1 + h2, ncol=3, y=-0.10)
    fig.subplots_adjust(bottom=0.40)
    save(fig, "fig_coverage.png")"""
assert a in s, "coverage anchor missing"
s = s.replace(a, b, 1)

# ------------------------------------------------------- monte-carlo ------
a2 = """    ax[0].axvline(sol["J"], color="r", ls="--", lw=2.6)
    ax[0].annotate(T("fig_Jstar") % sol["J"],
                   xy=(sol["J"], 0.80 * ax[0].get_ylim()[1]), xytext=(-12, 0),
                   textcoords="offset points", ha="right", fontsize=13, color="r")"""
b2 = """    ax[0].axvline(sol["J"], color="r", ls="--", lw=2.6,
                  label=T("fig_Jstar") % sol["J"])"""
assert a2 in s, "mc anchor missing"
s = s.replace(a2, b2, 1)

a3 = """    h = [Line2D([], [], color="tab:green", marker=".", ls="", ms=10, label="单次抽样"),
         Line2D([], [], color="k", lw=3.2, label="分箱中位数")]
    fig.tight_layout(w_pad=3.5)
    figure_legend(fig, h, ncol=2, y=-0.02)
    fig.subplots_adjust(bottom=0.30)"""
b3 = """    h = [Line2D([], [], color="tab:green", marker=".", ls="", ms=10, label="单次抽样"),
         Line2D([], [], color="k", lw=3.2, label="分箱中位数"),
         Line2D([], [], color="r", ls="--", lw=2.6,
                label=T("fig_Jstar") % sol["J"])]
    fig.tight_layout(w_pad=3.5)
    figure_legend(fig, h, ncol=3, y=-0.06)
    fig.subplots_adjust(bottom=0.36)"""
assert a3 in s, "mc legend anchor missing"
s = s.replace(a3, b3, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("patched both figures")
