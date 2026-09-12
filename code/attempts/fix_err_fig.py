# -*- coding: utf-8 -*-
"""fix_err_fig.py -- replace the three in-plot annotations of the error histogram
by a legend placed below the panel (no text over the bars)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
old = """    ax[0].hist(errs, bins=25, color="tab:blue", alpha=0.9, edgecolor="white")
    ymax = ax[0].get_ylim()[1]
    ax[0].axvline(20, color="r", ls="--", lw=2.4)
    ax[0].axvline(float(np.mean(errs)), color="k", ls=":", lw=2.2)
    ax[0].axvline(float(np.percentile(errs, 95)), color="g", ls="-.", lw=2.2)
    ax[0].annotate(T("fig_err20"), xy=(20, 0.94 * ymax), xytext=(7, 0),
                   textcoords="offset points", fontsize=12, color="r")
    ax[0].annotate(T("stat_mean") % float(np.mean(errs)),
                   xy=(float(np.mean(errs)), 0.70 * ymax), xytext=(7, 0),
                   textcoords="offset points", fontsize=12, color="k")
    ax[0].annotate(T("stat_p95") % float(np.percentile(errs, 95)),
                   xy=(float(np.percentile(errs, 95)), 0.46 * ymax), xytext=(7, 0),
                   textcoords="offset points", fontsize=12, color="g")
    ax[0].set_xlim(0, 52)
    ax[0].set_xlabel(T("err_m"))
    ax[0].set_ylabel(T("count"))
    ax[0].set_title(T("fig_err1"), fontsize=14)"""
new = """    ax[0].hist(errs, bins=25, color="tab:blue", alpha=0.9, edgecolor="white")
    ax[0].axvline(20, color="r", ls="--", lw=2.4, label=T("fig_err20"))
    ax[0].axvline(float(np.mean(errs)), color="k", ls=":", lw=2.2,
                  label=T("stat_mean") % float(np.mean(errs)))
    ax[0].axvline(float(np.percentile(errs, 95)), color="g", ls="-.", lw=2.2,
                  label=T("stat_p95") % float(np.percentile(errs, 95)))
    ax[0].set_xlim(0, 52)
    ax[0].set_xlabel(T("err_m"))
    ax[0].set_ylabel(T("count"))
    ax[0].set_title(T("fig_err1"), fontsize=14)
    legend_below(ax[0], ncol=2, y=-0.22, fontsize=11.5)"""
assert old in s, "anchor missing"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
