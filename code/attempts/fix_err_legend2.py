# -*- coding: utf-8 -*-
"""fix_err_legend2.py -- put the three threshold entries into one figure-level
legend at the very bottom, which can never touch a panel x label."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
a = """    ax[0].set_title(T("fig_err1"), fontsize=14)
    legend_below(ax[0], ncol=2, y=-0.46, fontsize=11.5)"""
b = """    ax[0].set_title(T("fig_err1"), fontsize=14)"""
assert a in s, "anchor 1"
s = s.replace(a, b, 1)
a2 = """    fig.tight_layout()
    save(fig, "fig_q3_errors.png")
    return {"n": len(errs), "median_err": float(np.median(errs)),"""
b2 = """    fig.tight_layout()
    h = [Line2D([], [], color="r", ls="--", lw=2.4, label=T("fig_err20")),
         Line2D([], [], color="k", ls=":", lw=2.2,
                label=T("stat_mean") % float(np.mean(errs))),
         Line2D([], [], color="g", ls="-.", lw=2.2,
                label=T("stat_p95") % float(np.percentile(errs, 95)))]
    figure_legend(fig, h, ncol=3, y=-0.02)
    fig.subplots_adjust(bottom=0.28)
    save(fig, "fig_q3_errors.png")
    return {"n": len(errs), "median_err": float(np.median(errs)),"""
assert a2 in s, "anchor 2"
s = s.replace(a2, b2, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
