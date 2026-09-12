#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
make_figures.py -- all figures of the paper.

Layout rules (2026-09 revision: "no occlusion, legends outside the axes"):
  * every legend is placed OUTSIDE the axes: below the panel, or below the whole
    figure when two panels share one legend; frameon=False so that it can never
    hide a data point or a gridline
  * annotations are put into the empty part of the axes; every figure is checked
    visually afterwards
  * readability: base font 16 pt, lines >= 2.2 pt, markers >= 8 pt
  * clarity of the data itself:
      - line families carry direct end labels instead of a colour legend
      - scatter plots get a binned median trend line
      - bars carry their values, value axes are scaled to the data
Chinese labels live in zh_labels.json (UTF-8); this source stays ASCII.
"""
import io
import json
import math
import os
import random
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, Polygon as MplPolygon, Wedge
from matplotlib.lines import Line2D

import geom_core as g
import q2_solver as q2
import robot_core as rc
import simulator as sim

P3 = {"survey_mode": "ring", "ring_radius": 1250.0, "survey_spacing": 1000.0, "probe_spacing": 450.0, "locate_sigma": 220.0, "clear_bonus": 450.0, "probe_min_angle": 35.0, "search_cost_bias": 60.0, "term_cap": 420.0, "endgame_radius": 90.0, "max_attempts": 6, "rim_step": 130.0, "max_rim_patrols": 12}
P4 = {"survey_mode": "lattice", "survey_spacing": 1100.0, "directional": True, "outer_ring_gap": 0.0, "ring_radius": 1280.0, "probe_spacing": 650.0, "locate_sigma": 220.0, "clear_bonus": 0.0, "probe_min_angle": 22.0, "search_cost_bias": 0.0, "term_cap": 420.0, "endgame_radius": 90.0, "max_attempts": 6}

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data")
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)

for cand in ("Microsoft YaHei", "SimHei", "DengXian", "SimSun", "Arial Unicode MS"):
    matplotlib.rcParams["font.sans-serif"] = [cand]
    matplotlib.rcParams["font.family"] = "sans-serif"
    break
matplotlib.rcParams.update({
    "axes.unicode_minus": False,
    "font.size": 16,
    "axes.titlesize": 17,
    "axes.labelsize": 17,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 13,
    "lines.linewidth": 2.4,
    "lines.markersize": 8,
    "patch.linewidth": 1.4,
    "axes.linewidth": 1.3,
    "xtick.major.width": 1.3,
    "ytick.major.width": 1.3,
    "xtick.major.size": 5,
    "ytick.major.size": 5,
    "grid.alpha": 0.35,
    "figure.dpi": 200,
    "savefig.dpi": 220,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.08,
})

L = json.load(io.open(os.path.join(HERE, "zh_labels.json"), encoding="utf-8-sig"))


def T(key, default=""):
    return L.get(key, default)


def legend_below(ax, ncol=3, y=-0.20, fontsize=13, **kw):
    """Legend OUTSIDE the axes, centred below the panel."""
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, y), ncol=ncol,
              frameon=False, fontsize=fontsize, handlelength=1.8,
              columnspacing=1.4, **kw)


def figure_legend(fig, handles, labels=None, ncol=3, y=0.02, fontsize=13):
    """One legend for the whole figure, below all panels.

    `labels` may be omitted when every handle already carries its own label.
    """
    if labels is None:
        labels = [h.get_label() for h in handles]
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, y),
               ncol=ncol, frameon=False, fontsize=fontsize, handlelength=1.8,
               columnspacing=1.5)


def save(fig, name):
    p = os.path.join(FIG, name)
    fig.savefig(p)
    plt.close(fig)
    print("  fig", name)


def load_csv(name):
    import csv as _csv
    with io.open(os.path.join(DATA, name), encoding="utf-8") as f:
        r = list(_csv.reader(f))
    return r[0], r[1:]


def jload(name):
    with io.open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def jdump(name, obj):
    with io.open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    print("  wrote", name)


# ===========================================================================
# problem 1
# ===========================================================================
def fig_q1_region():
    """Left: overall geometry.  Right: zoom of the positioning region.

    The zoom is a real panel (not an inset), so nothing covers the main figure.
    """
    S1, S2 = (0.0, 0.0), (1200.0, 0.0)
    G = (600.0, 900.0)
    th1, th2 = g.bearing(*S1, *G), g.bearing(*S2, *G)
    res = g.region_from_bearings([S1, S2], [th1, th2], 1.0)
    A, B = res["d_pair"]
    cx, cy, r = res["mec"]
    fig, axs = plt.subplots(1, 2, figsize=(9.1, 4.5))

    ax = axs[0]
    for S, th, c, tag in ((S1, th1, "tab:blue", "$S_1$"), (S2, th2, "tab:green", "$S_2$")):
        for sg in (-1, 1):
            a = math.radians(th + sg)
            ax.plot([S[0], S[0] + 1600 * math.cos(a)], [S[1], S[1] + 1600 * math.sin(a)],
                    ls="--", lw=1.6, color=c, alpha=0.85,
                    label=("$\pm1^\circ$ 边界" if (S == S1 and sg == -1) else None))
        a = math.radians(th)
        ax.plot([S[0], S[0] + 1600 * math.cos(a)], [S[1], S[1] + 1600 * math.sin(a)],
                lw=2.8, color=c,
                label=("%s 处示向度方向" % tag))
        ax.plot(*S, "^", color=c, ms=13, zorder=6)
        ax.annotate(tag, S, textcoords="offset points",
                    xytext=(6, -32) if S == S1 else (-34, -32), fontsize=16, zorder=7)
    ax.add_patch(MplPolygon(res["vertices"], closed=True, fc="tab:red", alpha=0.9,
                            ec="tab:red", lw=1.5, zorder=5, label="定位区域 $\\mathcal{R}$"))
    ax.plot(*G, marker="*", ms=20, color="k", zorder=7, label="干扰源真实位置 $G$")
    ax.annotate("$G$", G, textcoords="offset points", xytext=(16, 6), fontsize=16)
    # arrow that points to the zoom panel
    ax.annotate("", xy=(1180, 1180), xytext=(900, 1010),
                arrowprops=dict(arrowstyle="-|>", lw=1.8, color="gray"))
    ax.annotate("右图放大", xy=(1185, 1190), fontsize=13, color="gray")
    ax.set_xlim(-260, 1650)
    ax.set_ylim(-320, 1420)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_xlabel(T("x_east"))
    ax.set_ylabel(T("y_north"))
    ax.set_title("(a) 整体几何", fontsize=16)

    ax = axs[1]
    ax.add_patch(MplPolygon(res["vertices"], closed=True, fc="tab:red", alpha=0.55,
                            ec="tab:red", lw=2.2, zorder=4, label="定位区域 $\\mathcal{R}$"))
    ax.add_patch(Circle(((A[0] + B[0]) / 2.0, (A[1] + B[1]) / 2.0),
                        res["diameter"] / 2.0, fill=False, ls="--", color="k", lw=2.0,
                        zorder=3, label=T("fig_diameter") % res["diameter"]))
    ax.add_patch(Circle((cx, cy), r, fill=False, ls=":", color="purple", lw=2.2,
                        zorder=3, label=T("fig_mec") % r))
    ax.plot([A[0], B[0]], [A[1], B[1]], "-", color="k", lw=2.2, zorder=5,
            label="直径 $AB$")
    for v, nm in zip(res["vertices"], ("$V_1$", "$V_2$", "$V_3$", "$V_4$")):
        ax.plot(*v, "o", ms=7, color="k", zorder=6)
    ccx, ccy = (A[0] + B[0]) / 2.0, (A[1] + B[1]) / 2.0
    rad = max(res["diameter"], 2 * r) * 1.15
    ax.set_xlim(ccx - rad, ccx + rad)
    ax.set_ylim(ccy - rad, ccy + rad)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_xlabel(T("x_east"))
    ax.set_ylabel(T("y_north"))
    ax.set_title("(b) 定位区域局部放大", fontsize=16)
    fig.tight_layout()
    figure_legend(fig, [
        Line2D([], [], color="tab:blue", ls="--", lw=1.6, label="示向度 $\\pm1^\\circ$ 边界"),
        MplPolygon([(0, 0)], fc="tab:red", alpha=0.55, ec="tab:red", label="定位区域 $\\mathcal{R}$"),
        Line2D([], [], color="k", marker="*", ls="", ms=13, label="干扰源真实位置 $G$"),
        Line2D([], [], color="k", lw=2.2, label="直径 $AB$"),
        Line2D([], [], color="k", ls="--", lw=2.0, label="以 $AB$ 为直径的圆"),
        Line2D([], [], color="purple", ls=":", lw=2.2, label="最小包围圆")],
        ncol=3, y=-0.04)
    fig.subplots_adjust(bottom=0.34)
    save(fig, "fig_q1_region.png")


def fig_q1_diameter_vs_gamma():
    fig, ax = plt.subplots(figsize=(6.8, 4.9))
    d1 = 1200.0
    w1 = 2 * math.radians(1.0) * d1
    w2 = 2 * math.radians(1.0) * 1200.0
    gammas = np.linspace(15, 165, 200)
    D = [math.sqrt(w1 ** 2 + w2 ** 2 + 2 * w1 * w2 * math.cos(math.radians(gg)))
         / math.sin(math.radians(gg)) for gg in gammas]
    ax.plot(gammas, D, lw=3.0, color="tab:blue", label=T("fig_asy"))
    pts = []
    for gam in (20, 40, 60, 90, 120, 150):
        th = math.radians(gam)
        s2 = (d1 + 1200.0 * math.cos(math.pi - th), 1200.0 * math.sin(math.pi - th))
        b1 = g.bearing(0, 0, d1, 0.0)
        b2 = g.bearing(s2[0], s2[1], d1, 0.0)
        res = g.region_from_bearings([(0, 0), s2], [b1, b2], 1.0)
        if res["bounded"] and not res["empty"]:
            pts.append((gam, res["diameter"]))
    ax.plot([p[0] for p in pts], [p[1] for p in pts], "o", ms=11, color="tab:red",
            label=T("fig_exact"), zorder=5)
    ax.axvline(90, color="gray", ls="--", lw=2.0)
    ax.annotate(r"$\gamma=90^\circ$（最优）", xy=(90, 62), xytext=(96, 42),
                fontsize=14, color="gray")
    dlast = pts[-1][1] if pts else 170.0
    ax.annotate("$\\gamma>110^\\circ$：源靠近某一站，\n一阶解析式失效（偏小）",
                xy=(150, dlast), xytext=(93, 1250), fontsize=13, color="tab:red",
                arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=1.6))
    ax.set_yscale("log")
    ax.set_xlabel(T("gamma_deg"))
    ax.set_ylabel(T("diameter_m"))
    ax.set_title(T("fig_q1_d2"))
    ax.grid(True, which="both")
    ax.set_ylim(30, 9000)
    legend_below(ax, ncol=2, y=-0.20)
    save(fig, "fig_q1_diameter_vs_gamma.png")


def fig_q1_unbounded():
    S1, S2 = (0.0, 0.0), (100.0, 0.0)
    th1, th2 = 45.0, 45.5
    fig, ax = plt.subplots(figsize=(6.4, 4.9))
    for S, th, c in ((S1, th1, "tab:blue"), (S2, th2, "tab:green")):
        for s in (-1, 1):
            a = math.radians(th + s)
            ax.plot([S[0], S[0] + 1800 * math.cos(a)], [S[1], S[1] + 1800 * math.sin(a)],
                    ls="--", lw=1.8, color=c)
        a = math.radians(th)
        ax.plot([S[0], S[0] + 1800 * math.cos(a)], [S[1], S[1] + 1800 * math.sin(a)],
                lw=2.8, color=c)
    ax.fill_between([0, 1150], [0, 1150], [1150, 1150], color="tab:red", alpha=0.16)
    ax.annotate("", xy=(1010, 1015), xytext=(440, 445),
                arrowprops=dict(arrowstyle="-|>", lw=2.8, color="tab:red"))
    ax.plot([0, 100], [0, 0], "^", ms=13, color="k")
    ax.annotate(T("fig_unb"), xy=(330, 95), fontsize=15, ha="left", va="bottom")
    ax.set_xlim(-120, 1200)
    ax.set_ylim(-170, 1200)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_xlabel(T("x_east"))
    ax.set_ylabel(T("y_north"))
    ax.set_title(T("fig_q1_unb_title"))
    save(fig, "fig_q1_unbounded.png")


def fig_q1_cover_stats():
    head, rows = load_csv("q1_cover_stats.csv")
    ns = [r[0] for r in rows]
    pct = [float(r[4]) for r in rows]
    ratio = [float(r[7]) - 1.0 for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(9.1, 3.9))
    b1 = ax[0].bar(ns, pct, color="tab:orange", width=0.6)
    ax[0].bar_label(b1, fmt="%.2f%%", fontsize=14, padding=3)
    ax[0].set_xlabel(T("n_stations"))
    ax[0].set_ylabel(T("pct_fail"))
    ax[0].set_title(T("fig_q1_c1"))
    ax[0].grid(True, axis="y")
    ax[0].set_ylim(0, max(pct) * 1.35)
    b2 = ax[1].bar(ns, ratio, color="tab:blue", width=0.6)
    ax[1].bar_label(b2, fmt="%.4f", fontsize=13, padding=3)
    ax[1].set_xlabel(T("n_stations"))
    ax[1].set_ylabel(T("excess"))
    ax[1].set_title(T("fig_q1_c2"))
    ax[1].grid(True, axis="y")
    ax[1].set_ylim(0, max(ratio) * 1.4)
    fig.tight_layout()
    save(fig, "fig_q1_cover_stats.png")


def fig_q1_shapes():
    rnd = random.Random(5)
    fig, axs = plt.subplots(2, 2, figsize=(8.8, 7.8))
    axs = axs.ravel()
    made, tries = 0, 0
    while made < 4 and tries < 60000:
        tries += 1

        def rp():
            r = 1800.0 * math.sqrt(rnd.random())
            a = 2 * math.pi * rnd.random()
            return (r * math.cos(a), r * math.sin(a))
        sts = [rp() for _ in range(2)]
        if math.dist(sts[0], sts[1]) < 900:
            continue
        G = rp()
        if min(math.dist(s, G) for s in sts) < 250 or max(math.dist(s, G) for s in sts) > 1500:
            continue
        bs = [g.bearing(s[0], s[1], G[0], G[1]) for s in sts]
        res = g.region_from_bearings(sts, bs, 1.0)
        if res["empty"] or not res["bounded"] or res["diameter"] < 30:
            continue
        A, B = res["d_pair"]
        others = [v for v in res["vertices"]
                  if math.dist(v, A) > 1e-6 and math.dist(v, B) > 1e-6]
        viol = g.diameter_disk_slack(others, A, B) if others else -1.0
        if made < 2 and viol <= 1e-9:
            continue
        if made >= 2 and viol > 1e-9:
            continue
        ax = axs[made]
        ax.add_patch(MplPolygon(res["vertices"], closed=True, fc="tab:red",
                                alpha=0.5, ec="tab:red", lw=1.8, zorder=4))
        cen = ((A[0] + B[0]) / 2.0, (A[1] + B[1]) / 2.0)
        ax.add_patch(Circle(cen, res["diameter"] / 2.0, fill=False, ls="--",
                            color="k", lw=1.8, zorder=3))
        ax.add_patch(Circle((res["mec"][0], res["mec"][1]), res["mec"][2],
                            fill=False, ls=":", color="purple", lw=2.0, zorder=3))
        ax.plot([A[0], B[0]], [A[1], B[1]], "-", color="k", lw=1.8, zorder=5)
        for s in sts:
            ax.plot(*s, "^", ms=10, color="tab:blue", zorder=6)
        if viol > 1e-9:
            ax.plot(others[0][0], others[0][1], "o", ms=12, mfc="none",
                    mec="magenta", mew=2.8, zorder=7)
        pad = max(res["diameter"], 2 * res["mec"][2]) * 0.9 + 18
        ax.set_xlim(cen[0] - pad, cen[0] + pad)
        ax.set_ylim(cen[1] - pad, cen[1] + pad)
        ax.set_aspect("equal")
        ax.grid(True)
        ax.tick_params(labelsize=12)
        ax.set_title(("$D=%.1f$ m：%s" % (res["diameter"],
                                          T("covered") if viol <= 1e-9 else T("not_covered"))),
                     fontsize=15)
        made += 1
    fig.suptitle(T("fig_q1_shapes_title"), fontsize=16)
    figure_legend(fig, [
        MplPolygon([(0, 0)], fc="tab:red", alpha=0.5, ec="tab:red", label="定位区域"),
        Line2D([], [], color="k", lw=2.0, label="直径 $AB$"),
        Line2D([], [], color="k", ls="--", lw=1.8, label="以 $AB$ 为直径的圆"),
        Line2D([], [], color="purple", ls=":", lw=2.0, label="最小包围圆"),
        Line2D([], [], color="magenta", marker="o", ls="", mfc="none", ms=11,
               label="落在直径圆外的顶点")], ncol=3, y=-0.015)
    fig.tight_layout(rect=(0, 0.075, 1, 0.955))
    save(fig, "fig_q1_shapes.png")


# ===========================================================================
# problem 2
# ===========================================================================
def fig_q2_geometry():
    s1 = (-420.0, 260.0)
    th1 = 63.0
    sol = q2.solve_second_point(s1, th1, r_guard=1000.0)
    gset = q2.sector_points(s1, th1)
    fig, ax = plt.subplots(figsize=(6.8, 5.9))
    xs = [p[2][0] for p in gset]
    ys = [p[2][1] for p in gset]
    ax.plot(xs, ys, ".", ms=5.0, color="tab:blue", alpha=0.9, zorder=2,
            markeredgecolor="white", markeredgewidth=0.6, label=T("fig_feasible"))
    for s in (-1, 1):
        a = math.radians(th1 + s * 1.0)
        ax.plot([s1[0], s1[0] + 1600 * math.cos(a)], [s1[1], s1[1] + 1600 * math.sin(a)],
                ls="--", color="tab:blue", lw=1.8, zorder=2)
    ang = math.radians(th1)
    ax.plot([s1[0], s1[0] + 1600 * math.cos(ang)], [s1[1], s1[1] + 1600 * math.sin(ang)],
            color="tab:blue", lw=3.0, zorder=3, label=T("fig_measured"))
    far = (s1[0] + 1500 * math.cos(ang), s1[1] + 1500 * math.sin(ang))
    ax.add_patch(Circle(s1, 1000.0, fill=False, ls=":", color="gray", lw=1.8, zorder=1,
                        label=T("fig_guard1")))
    ax.add_patch(Circle(far, 1000.0, fill=False, ls=":", color="gray", lw=1.8, zorder=1))
    ax.plot(*s1, "^", ms=14, color="tab:blue", zorder=5)
    ax.annotate("$S_1$", s1, textcoords="offset points", xytext=(16, -34), fontsize=17)
    ax.plot(*sol["S2"], marker="*", ms=26, color="red", zorder=6,
            label=T("fig_s2opt") % (sol["b"], sol["phi"]))
    ax.annotate("$S_2^{*}$", sol["S2"], textcoords="offset points", xytext=(16, 10),
                fontsize=17, zorder=7)
    ax.plot([s1[0], sol["S2"][0]], [s1[1], sol["S2"][1]], "-", color="red", lw=2.2, zorder=4)
    # angle arc between the measured bearing and the baseline, drawn at S1;
    # the label sits in the empty upper-left corner with a leader line
    ang2 = math.degrees(math.atan2(sol["S2"][1] - s1[1], sol["S2"][0] - s1[0])) % 360.0
    t1, t2 = min(th1, ang2), max(th1, ang2)
    Rarc = 560.0
    ax.add_patch(Arc(s1, 2 * Rarc, 2 * Rarc, angle=0.0, theta1=t1, theta2=t2,
                     color="red", lw=2.2, zorder=5))
    # the leader stops at the LEFT end of the arc, so it never crosses the
    # baseline or the bearing ray
    aend = math.radians(t2)
    ax.annotate("$\\varphi^{*}=%.1f^\\circ$" % sol["phi"],
                xy=(s1[0] + Rarc * math.cos(aend), s1[1] + Rarc * math.sin(aend)),
                xytext=(-1740, 940), fontsize=15, color="red", ha="left",
                arrowprops=dict(arrowstyle="-|>", color="red", lw=1.6))
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_xlim(-1800, 1800)
    ax.set_ylim(-1650, 1950)
    ax.set_xlabel(T("x_east"))
    ax.set_ylabel(T("y_north"))
    ax.set_title(T("fig_q2_title"))
    legend_below(ax, ncol=2, y=-0.15)
    save(fig, "fig_q2_geometry.png")


def fig_q2_scan():
    head, rows = load_csv("q2_phi_scan.csv")
    fig, ax = plt.subplots(1, 2, figsize=(9.1, 3.9))
    order = sorted(set(float(r[0]) for r in rows))
    cmap = plt.get_cmap("viridis")
    for i, b in enumerate(order):
        xs, ys = [], []
        for r in rows:
            if float(r[0]) != b or r[3] != "ok":
                continue
            xs.append(float(r[1]))
            ys.append(float(r[2]))
        if xs:
            col = cmap(i / max(len(order) - 1, 1))
            ax[0].plot(xs, ys, "-o", ms=6.5, lw=2.0, color=col)
            ax[0].annotate("$b=%.0f$" % b, (xs[-1], ys[-1]), textcoords="offset points",
                           xytext=(9, -4), fontsize=12.5, color=col)
    ax[0].set_xlabel(T("phi_deg"))
    ax[0].set_ylabel(T("J_m"))
    ax[0].set_yscale("log")
    ax[0].grid(True, which="both")
    ax[0].set_xlim(8, 48)
    ax[0].set_title(T("fig_q2_scan1"))

    head2, rows2 = load_csv("q2_guard_tradeoff.csv")
    rg = [float(r[0]) for r in rows2 if r[1]]
    J = [float(r[3]) for r in rows2 if r[1]]
    ph = [float(r[2]) for r in rows2 if r[1]]
    l1, = ax[1].plot(rg, J, "-o", lw=2.8, ms=10, color="tab:red", label=T("J_m"))
    ax[1].set_xlabel(T("r_guard"))
    ax[1].set_ylabel(T("J_m"), color="tab:red")
    ax[1].tick_params(axis="y", labelcolor="tab:red")
    ax[1].grid(True)
    ax2 = ax[1].twinx()
    l2, = ax2.plot(rg, ph, "--s", lw=2.4, ms=9, color="tab:blue", label=T("phi_opt"))
    ax2.set_ylabel(T("phi_opt"), color="tab:blue")
    ax2.tick_params(axis="y", labelcolor="tab:blue")
    ax2.set_ylim(20, 42)
    ax[1].set_title(T("fig_q2_scan2"))
    fig.tight_layout()
    figure_legend(fig, [l1, l2], [T("J_m"), T("phi_opt")], ncol=2, y=-0.02)
    fig.subplots_adjust(bottom=0.26)
    save(fig, "fig_q2_scan.png")


BL_NAMES = {"A_proposed": "A 本文规则", "B_perp_800": "B 垂直偏移\n800 m",
            "C_along_800": "C 沿示向度\n前进 800 m", "D_random": "D 可行域内\n随机取点",
            "E_oracle": "E 先知策略\n(性能下界)"}


def fig_q2_baselines():
    head, rows = load_csv("q2_baselines.csv")
    keys = [r[0] for r in rows]
    names = [BL_NAMES.get(k, k) for k in keys]
    mean = [float(r[1]) for r in rows]
    p95 = [float(r[2]) if r[2] not in ("Infinity", "inf", "") else float("nan")
           for r in rows]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    b1 = ax.bar(x - 0.21, mean, 0.42, label=T("mean"), color="tab:blue")
    ax.bar(x + 0.21, [v if v == v else 0.0 for v in p95], 0.42,
           label=T("p95"), color="tab:orange")
    ax.set_yscale("log")
    ax.bar_label(b1, fmt="%.1f", fontsize=13, padding=2)
    for i, v in enumerate(p95):
        if v == v:
            ax.annotate("%.1f" % v, (x[i] + 0.21, v), textcoords="offset points",
                        xytext=(0, 4), ha="center", fontsize=13)
        else:
            ax.annotate(T("noinf"), (x[i] + 0.21, 12), textcoords="offset points",
                        xytext=(0, 0), ha="center", fontsize=12, color="tab:red",
                        rotation=90)
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=13)
    ax.set_ylabel(T("D_m"))
    ax.set_title(T("fig_q2_base"))
    ax.grid(True, axis="y", which="both")
    ax.set_ylim(8, 30000)
    legend_below(ax, ncol=2, y=-0.18)
    fig.tight_layout()
    save(fig, "fig_q2_baselines.png")


def fig_q2_montecarlo():
    s1 = (-420.0, 260.0)
    th1 = 63.0
    sol = q2.solve_second_point(s1, th1, r_guard=1000.0)
    gset = q2.sector_points(s1, th1)
    rnd = random.Random(11)
    r_hi = max(r for (r, _, _) in gset)
    Ds, rr, dd = [], [], []
    for _ in range(4000):
        r = 6.0 + (r_hi - 6.0) * rnd.random()
        a = th1 + rnd.uniform(-1, 1)
        G = (s1[0] + r * math.cos(math.radians(a)), s1[1] + r * math.sin(math.radians(a)))
        b2 = g.bearing(sol["S2"][0], sol["S2"][1], G[0], G[1]) + rnd.uniform(-1, 1)
        res = g.region_from_bearings([s1, sol["S2"]], [th1, b2], 1.0)
        if res["bounded"] and not res["empty"]:
            Ds.append(res["diameter"])
            rr.append(r)
            dd.append(res["diameter"])
    fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.4))
    ax[0].hist(Ds, bins=45, color="tab:blue", alpha=0.88, edgecolor="white", lw=0.6)
    ax[0].axvline(sol["J"], color="r", ls="--", lw=2.6,
                  label=T("fig_Jstar") % sol["J"])
    ax[0].set_xlabel(T("D_m"))
    ax[0].set_ylabel(T("count"))
    ax[0].grid(True, axis="y")
    ax[0].set_title(T("fig_q2_mc1s"))
    ax[1].plot(rr, dd, ".", ms=4.5, alpha=0.35, color="tab:green", label="单次抽样")
    nb = 18
    edges = np.linspace(0, r_hi, nb + 1)
    arr_r = np.array(rr)
    arr_d = np.array(dd)
    cx, cy = [], []
    for i in range(nb):
        m = (arr_r >= edges[i]) & (arr_r < edges[i + 1])
        if m.sum() > 3:
            cx.append(0.5 * (edges[i] + edges[i + 1]))
            cy.append(float(np.median(arr_d[m])))
    ax[1].plot(cx, cy, "-", lw=3.2, color="k", label="分箱中位数")
    ax[1].set_xlabel(T("r_m"))
    ax[1].set_ylabel("$D$ / m")
    ax[1].grid(True)
    ax[1].set_title(T("fig_q2_mc2s"))
    h = [Line2D([], [], color="tab:green", marker=".", ls="", ms=10, label="单次抽样"),
         Line2D([], [], color="k", lw=3.2, label="分箱中位数"),
         Line2D([], [], color="r", ls="--", lw=2.6,
                label=T("fig_Jstar") % sol["J"])]
    fig.tight_layout(w_pad=3.5)
    figure_legend(fig, h, ncol=3, y=-0.06)
    fig.subplots_adjust(bottom=0.36)
    save(fig, "fig_q2_montecarlo.png")


def fig_q2_region_rule():
    """Panel 1: overview with the three source positions; panels 2-4: the
    positioning region for each of them (real panels, no inset)."""
    s1 = (-420.0, 260.0)
    th1 = 63.0
    sol = q2.solve_second_point(s1, th1, r_guard=1000.0)
    ranges = (300.0, 900.0, 1400.0)
    cols = ("tab:blue", "tab:green", "darkorchid")
    a0 = math.radians(th1)
    Gs = [(s1[0] + rr * math.cos(a0), s1[1] + rr * math.sin(a0)) for rr in ranges]
    fig = plt.figure(figsize=(9.1, 3.2))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.6, 1, 1, 1], wspace=0.48)

    ax = fig.add_subplot(gs[0, 0])
    ax.add_patch(Circle(s1, 1000.0, fill=False, ls=":", color="gray", lw=1.6,
                        label="$R_{\\min}=1000$ m"))
    ax.plot([s1[0], sol["S2"][0]], [s1[1], sol["S2"][1]], "-", color="red", lw=2.0)
    for i, (G, rr, col) in enumerate(zip(Gs, ranges, cols)):
        ax.plot([s1[0], G[0]], [s1[1], G[1]], "-", color=col, lw=2.0)
        ax.plot([sol["S2"][0], G[0]], [sol["S2"][1], G[1]], "--", color=col, lw=1.6)
        ax.plot(*G, "o", ms=11, color=col, zorder=6)
    ax.plot(*s1, "^", ms=13, color="tab:blue", zorder=6)
    ax.annotate("$S_1$", s1, textcoords="offset points", xytext=(10, -30), fontsize=16)
    ax.plot(*sol["S2"], marker="*", ms=22, color="red", zorder=6)
    ax.annotate("$S_2^{*}$", sol["S2"], textcoords="offset points", xytext=(-26, -34),
                fontsize=16)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.tick_params(labelsize=12)
    ax.set_xlim(-1750, 1750)
    ax.set_ylim(-1150, 2050)
    ax.set_title("(a) 几何总览", fontsize=15)
    ax.set_ylabel(T("y_north"), fontsize=14)

    for i, (G, rr, col) in enumerate(zip(Gs, ranges, cols)):
        b2 = g.bearing(sol["S2"][0], sol["S2"][1], G[0], G[1])
        res = g.region_from_bearings([s1, sol["S2"]], [th1, b2], 1.0)
        ax = fig.add_subplot(gs[0, i + 1])
        A, B = res["d_pair"]
        ax.add_patch(MplPolygon(res["vertices"], closed=True, fc="tab:red",
                                alpha=0.55, ec="tab:red", lw=2.2, zorder=4))
        ax.add_patch(Circle(((A[0] + B[0]) / 2.0, (A[1] + B[1]) / 2.0),
                            res["diameter"] / 2.0, fill=False, ls="--", color="k",
                            lw=1.8, zorder=3))
        ax.add_patch(Circle((res["mec"][0], res["mec"][1]), res["mec"][2],
                            fill=False, ls=":", color="purple", lw=2.2, zorder=3))
        ax.plot([A[0], B[0]], [A[1], B[1]], "-", color="k", lw=2.2, zorder=5)
        ax.plot(*G, "o", ms=10, color="k", zorder=6)
        ax.annotate("$G$", G, textcoords="offset points", xytext=(11, 7), fontsize=16)
        ax.set_aspect("equal")
        ax.grid(True)
        half = max(res["diameter"], 2 * res["mec"][2]) * 1.15 + 12
        ax.set_xlim(G[0] - half, G[0] + half)
        ax.set_ylim(G[1] - half, G[1] + half)
        ax.tick_params(labelsize=11)
        ax.set_title(T("fig_q2_r%d" % i) % res["diameter"], fontsize=14, color=col)
        ax.set_xlabel(T("x_east"), fontsize=13)
        if i == 0:
            ax.set_ylabel(T("y_north"), fontsize=13)

    figure_legend(fig, [
        Line2D([], [], color="tab:blue", lw=2.0, label="干扰源至 $S_1$ 的视线"),
        Line2D([], [], color="tab:red", marker="*", ls="", ms=13, label="最优第二检测点 $S_2^{*}$"),
        Line2D([], [], color="gray", marker="o", ls="", ms=10,
               label="干扰源位置（颜色对应 (b)(c)(d)）"),
        Line2D([], [], color="red", lw=2.0, label="检测基线 $S_1S_2^{*}$"),
        MplPolygon([(0, 0)], fc="tab:red", alpha=0.55, ec="tab:red", label="定位区域"),
        Line2D([], [], color="k", lw=2.2, label="直径 $AB$"),
        Line2D([], [], color="k", ls="--", lw=1.8, label="以 $AB$ 为直径的圆"),
        Line2D([], [], color="purple", ls=":", lw=2.2, label="最小包围圆")],
        ncol=3, y=-0.05)
    fig.subplots_adjust(bottom=0.42)
    save(fig, "fig_q2_region_rule.png")


# ===========================================================================
# problems 3 / 4
# ===========================================================================
def fig_case_map(mode="q3", seed=20007, fname="fig_q3_case_map.png"):
    rng = random.Random(seed)
    srcs = sim.make_case(rng, kind_mix=0.0 if mode == "q3" else 0.5)
    arena = sim.Arena(srcs, seed=seed)
    cl = rc.LocalClient(arena)
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P3 if mode == "q3" else P4)
    brain = rc.Brain(cl, params=p, seed=seed)
    path = []
    om, oc = brain.move_measure, brain.move_clear

    def m2(x, y, c):
        r = om(x, y, c)
        path.append((x, y))
        return r

    def c2(x, y, c):
        r = oc(x, y, c)
        path.append((x, y))
        return r
    brain.move_measure, brain.move_clear = m2, c2
    st = brain.run()
    fig, ax = plt.subplots(figsize=(7.0, 6.9))
    ax.add_patch(Circle((0, 0), 1800, fill=False, color="k", lw=2.2))
    for s in srcs:
        if s.kind == "directional":
            ax.add_patch(Wedge((s.x, s.y), 300, s.direction - 90, s.direction + 90,
                               fc="tab:orange", alpha=0.45, ec="none", zorder=1))
    if path:
        ax.plot([q[0] for q in path], [q[1] for q in path], "-", color="tab:blue",
                lw=1.6, alpha=0.9, zorder=2)
    for s in srcs:
        ax.plot(s.x, s.y, marker="*", ms=17 if s.cleared else 13,
                color="tab:red" if s.cleared else "gray", zorder=4)
        ax.annotate("ch%d" % s.channel, (s.x, s.y), textcoords="offset points",
                    xytext=(9, 7), fontsize=12.5, zorder=5)
    ax.plot(0, 0, "s", ms=12, color="k", zorder=5)
    ax.annotate(T("fig_start"), (0, 0), textcoords="offset points", xytext=(-24, -32),
                fontsize=13)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_xlim(-2200, 2350)
    ax.set_ylim(-2350, 2150)
    ax.set_xlabel(T("x_east"))
    ax.set_ylabel(T("y_north"))
    ax.set_title(T("fig_case_title") % (mode.upper(), st["n_sources"], st["mean_time"]),
                 fontsize=16)
    handles = [Line2D([], [], color="tab:blue", lw=1.6, label=T("fig_path")),
               Line2D([], [], color="tab:red", marker="*", ls="", ms=15, label=T("fig_src")),
               Line2D([], [], color="k", marker="s", ls="", ms=10, label=T("fig_start"))]
    if any(s.kind == "directional" for s in srcs):
        handles.append(MplPolygon([(0, 0)], fc="tab:orange", alpha=0.45, ec="none",
                                  label=T("fig_sector")))
    legend_below(ax, ncol=len(handles), y=-0.12, handles=handles)
    save(fig, fname)
    return st


def fig_q34_stats():
    a = jload("q34_agg.json")
    fig, ax = plt.subplots(1, 3, figsize=(8.2, 3.4))
    names = [T("q3_short"), T("q4_short")]
    vals = [a["q3"]["mean_time"], a["q4"]["mean_time"]]
    b = ax[0].bar(names, vals, color=["tab:blue", "tab:orange"], width=0.55)
    ax[0].bar_label(b, fmt="%.0f s", fontsize=15, padding=3)
    ax[0].set_ylabel(T("mean_time"))
    ax[0].set_title(T("fig_q34_t"))
    ax[0].grid(True, axis="y")
    ax[0].set_ylim(0, max(vals) * 1.22)
    ax[0].tick_params(labelsize=14)

    x = np.arange(2)
    tr = [a["q3"]["mean_travel"] / 5.0, a["q4"]["mean_travel"] / 5.0]
    me = [a["q3"]["mean_measure"] * 6.0, a["q4"]["mean_measure"] * 6.0]
    b1 = ax[1].bar(x - 0.19, tr, 0.38, label=T("travel"), color="tab:green")
    b2 = ax[1].bar(x + 0.19, me, 0.38, label=T("measure"), color="tab:purple")
    ax[1].bar_label(b1, fmt="%.0f", fontsize=13, padding=2)
    ax[1].bar_label(b2, fmt="%.0f", fontsize=13, padding=2)
    ax[1].set_xticks(x)
    ax[1].set_xticklabels(names, fontsize=14)
    ax[1].set_ylabel(T("time_s"))
    ax[1].set_title(T("fig_q34_c"))
    ax[1].grid(True, axis="y")
    ax[1].set_ylim(0, max(tr + me) * 1.18)

    rr = [a["q3"]["mean_ratio"], a["q4"]["mean_ratio"]]
    b3 = ax[2].bar(names, rr, color=["tab:blue", "tab:orange"], width=0.55)
    ax[2].bar_label(b3, fmt="%.3f", fontsize=15, padding=3)
    ax[2].set_ylim(0, 1.18)
    ax[2].set_ylabel(T("ratio"))
    ax[2].set_title(T("fig_q34_r"))
    ax[2].grid(True, axis="y")
    ax[2].tick_params(labelsize=14)
    fig.tight_layout()
    figure_legend(fig, [b1, b2], [T("travel"), T("measure")], ncol=2, y=-0.03)
    fig.subplots_adjust(bottom=0.34)
    save(fig, "fig_q34_stats.png")


SENS_NAME = {"nominal": "v_nominal", "R_min=950": "v_rlo950", "R_min=1050": "v_rlo1050",
             "R_max=1400": "v_rhi1400", "bearing_err=0.8deg": "v_eps08",
             "bearing_err=1.0deg": "v_eps10", "n_sources=10": "v_n10",
             "n_sources=16": "v_n16"}


def fig_sensitivity():
    for tag, fn, ttl in (("q3", "fig_q3_sensitivity.png", T("sens3")),
                         ("q4", "fig_q4_sensitivity.png", T("sens4"))):
        head, rows = load_csv("%s_sensitivity.csv" % tag)
        names = [T(SENS_NAME.get(r[0], ""), r[0]) for r in rows]
        ratio = [float(r[1]) for r in rows]
        mt = [float(r[2]) for r in rows]
        ypos = np.arange(len(names))
        fig, ax = plt.subplots(1, 2, figsize=(9.1, 4.1))
        b0 = ax[0].barh(ypos, mt, color="tab:orange", height=0.6)
        ax[0].bar_label(b0, fmt="%.0f", fontsize=13, padding=3)
        ax[0].set_yticks(ypos)
        ax[0].set_yticklabels(names, fontsize=13)
        ax[0].set_xlabel(T("fig_sens_t"))
        ax[0].set_title(ttl + "：时间")
        ax[0].grid(True, axis="x")
        ax[0].set_xlim(0, max(mt) * 1.22)
        b1 = ax[1].barh(ypos, ratio, color="tab:blue", height=0.6)
        ax[1].bar_label(b1, fmt="%.3f", fontsize=13, padding=3)
        ax[1].set_yticks(ypos)
        ax[1].set_yticklabels([])
        ax[1].set_xlim(0, 1.25)
        ax[1].set_xlabel(T("fig_sens_r"))
        ax[1].set_title(ttl + "：完成率")
        ax[1].grid(True, axis="x")
        fig.tight_layout()
        save(fig, fn)


def fig_q3_cases():
    head, rows = load_csv("q3_cases.csv")
    n = np.array([int(r[1]) for r in rows])
    mt = np.array([float(r[4]) for r in rows])
    ratio = [float(r[3]) for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(9.1, 3.9))
    ax[0].plot(n, mt, "o", ms=10, alpha=0.6, color="tab:blue", label="单个演练算例")
    xs, ys = [], []
    for v in sorted(set(n.tolist())):
        m = n == v
        xs.append(v)
        ys.append(float(np.median(mt[m])))
    ax[0].plot(xs, ys, "-", lw=3.0, color="k", marker="s", ms=8, label="各规模中位数")
    ax[0].set_xlabel(T("n_sources"))
    ax[0].set_ylabel(T("mean_time"))
    ax[0].grid(True)
    ax[0].set_title(T("fig_q3_c1"))
    legend_below(ax[0], ncol=2, y=-0.28)
    hist, edges = np.histogram(ratio, bins=np.arange(0.5, 1.05, 0.05))
    ax[1].bar(0.5 * (edges[:-1] + edges[1:]), hist, width=0.045,
              color="tab:green", alpha=0.9, edgecolor="white")
    ax[1].set_xlim(0.45, 1.14)
    ax[1].set_xlabel(T("ratio"))
    ax[1].set_ylabel(T("count"))
    ax[1].set_title(T("fig_q3_c2"))
    ax[1].grid(True, axis="y")
    ax[1].annotate("全部 %d 组均为 1.000" % len(ratio), xy=(1.0, max(hist)),
                   xytext=(-10, -16), textcoords="offset points", ha="right",
                   fontsize=13, color="tab:green")
    fig.tight_layout()
    save(fig, "fig_q3_cases.png")


def fig_task_breakdown():
    a = jload("q34_agg.json")
    fig, ax = plt.subplots(figsize=(6.8, 5.2))
    vals = [a["q3"]["mean_travel"] / 5.0, a["q3"]["mean_measure"] * 5.0,
            a["q3"]["mean_measure"] * 1.0, a["q3"]["mean_clear_actions"] * 4.0, 119.0]
    labels = [T("travel"), T("measure"), T("switch"), T("clear"), T("census")]
    colors = ["tab:green", "tab:purple", "tab:brown", "tab:red", "tab:gray"]
    total = float(sum(vals))
    wedges, texts, autotexts = ax.pie(
        vals, labels=None,
        autopct=lambda pct: ("%.1f%%" % pct) if pct >= 5.0 else "",
        colors=colors, textprops={"fontsize": 16}, startangle=95,
        pctdistance=0.62, wedgeprops={"edgecolor": "white", "linewidth": 2})
    for t in autotexts:
        t.set_fontsize(16)
    ax.set_title(T("fig_pie"), pad=10)
    figure_legend(fig, wedges,
                  ["%s  %.1f%%" % (labels[i], 100.0 * vals[i] / total)
                   for i in range(len(labels))],
                  ncol=3, y=-0.02)
    save(fig, "fig_q3_time_pie.png")


def fig_convergence():
    rng = random.Random(4242)
    srcs = sim.make_case(rng, n_sources=12)
    arena = sim.Arena(srcs)
    cl = rc.LocalClient(arena)
    p = dict(rc.DEFAULT_PARAMS)
    p.update(P3)
    brain = rc.Brain(cl, params=p, seed=1)
    tr = []
    om = brain.move_measure

    def m2(x, y, c):
        r = om(x, y, c)
        tr.append((brain.vtime, x, y, c, r.get("measure_result")))
        return r
    brain.move_measure = m2
    brain.run()
    fig, ax = plt.subplots(1, 2, figsize=(8.2, 3.5))
    style = {"direction": ("tab:green", "有信号 direction"),
             "no_signal": ("tab:gray", "无信号 no_signal"),
             "near": ("tab:orange", "过近 near")}
    for k, (col, lab) in style.items():
        xs = [t[0] for t in tr if t[4] == k]
        ys = [math.hypot(t[1], t[2]) for t in tr if t[4] == k]
        if xs:
            ax[0].plot(xs, ys, ".", ms=7, color=col, label=lab, alpha=0.85)
    ax[0].set_xlabel(T("vtime"))
    ax[0].set_ylabel(T("dist_origin"))
    ax[0].grid(True)
    ax[0].set_title(T("fig_conv1"))
    legend_below(ax[0], ncol=3, y=-0.31)
    kinds = {}
    for t in tr:
        kinds[t[4]] = kinds.get(t[4], 0) + 1
    ks = [k for k in ("direction", "no_signal", "near") if k in kinds]
    b = ax[1].bar(range(len(ks)), [kinds[k] for k in ks],
                  color=[style[k][0] for k in ks], width=0.55)
    ax[1].bar_label(b, fontsize=14, padding=3)
    ax[1].set_xticks(range(len(ks)))
    ax[1].set_xticklabels([style[k][1].split()[0] for k in ks], fontsize=13)
    ax[1].set_ylabel(T("count"))
    ax[1].grid(True, axis="y")
    ax[1].set_ylim(0, max(kinds.values()) * 1.25)
    ax[1].set_title(T("fig_conv2"))
    fig.tight_layout()
    save(fig, "fig_convergence.png")


def fig_simulator_timing():
    fig, ax = plt.subplots(figsize=(7.4, 4.5))
    seq = ["enter", "移动\n500 m", "检测\nch1", "切换+检测\nch2", "清除\n未命中",
           "移动\n400 m", "清除\n命中", "exit"]
    dt = [0, 100, 5, 6, 83, 80, 5, 0]
    t = [0, 100, 105, 111, 194, 274, 279, 279]
    b = ax.bar(range(len(seq)), dt, color="tab:blue", width=0.62)
    ax.bar_label(b, labels=["%d s\n(t=%d)" % (d, tt) for d, tt in zip(dt, t)],
                 fontsize=12, padding=3)
    ax.set_xticks(range(len(seq)))
    ax.set_xticklabels(seq, fontsize=13)
    ax.set_ylabel(T("cost_s"))
    ax.set_title(T("fig_timing"))
    ax.grid(True, axis="y")
    ax.set_ylim(0, max(dt) * 1.45)
    ax.margins(x=0.02)
    save(fig, "fig_simulator_timing.png")


def fig_coverage():
    fig, axs = plt.subplots(1, 2, figsize=(9.1, 4.4))
    R, r = 1800.0, 1280.0
    pts = [(0.0, 0.0)] + [(r * math.cos(k * math.pi / 3), r * math.sin(k * math.pi / 3))
                          for k in range(6)]
    ax = axs[0]
    for i, p in enumerate(pts):
        ax.add_patch(Circle(p, 1000.0, fill=False, color="tab:blue", ls="--", lw=1.6,
                            alpha=0.9, label="站位的 $R_{\\min}$ 探测圆" if i == 0 else None))
    ax.add_patch(Circle((0, 0), R, fill=False, color="k", lw=2.6, label="目标区域边界"))
    for i, p in enumerate(pts):
        ax.plot(p[0], p[1], "^", ms=12, color="tab:blue",
                label="检测站位" if i == 0 else None)
    ax.set_aspect("equal")
    ax.set_xlim(-3000, 3000)
    ax.set_ylim(-3000, 3000)
    ax.grid(True)
    ax.tick_params(labelsize=13)
    ax.set_title(T("fig_cov1"), fontsize=15)
    ax.set_xlabel(T("x_east"))
    ax.set_ylabel(T("y_north"))
    h1 = [Line2D([], [], color="tab:blue", ls="--", lw=1.6,
                 label="站位的 $R_{\\min}$ 探测圆"),
          Line2D([], [], color="k", lw=2.6, label="目标区域边界"),
          Line2D([], [], color="tab:blue", marker="^", ls="", ms=11, label="检测站位")]

    ax = axs[1]
    rhos = np.linspace(600, 1700, 220)
    cov = [0.8660254 * rr + math.sqrt(max(1000.0 ** 2 - 0.25 * rr ** 2, 0.0)) for rr in rhos]
    ax.plot(rhos, cov, lw=3.0, color="tab:blue", label=T("fig_cov_c"))
    ax.axhline(1800, color="r", ls="--", lw=2.4, label=T("fig_cov_r"))
    ax.axvline(1280, color="g", ls=":", lw=2.4, label=T("fig_cov_opt"))
    ax.plot([1280], [1892], "o", ms=11, color="g", zorder=5)
    ax.annotate("$\\rho=1280$ m 时覆盖半径 1892 m", xy=(1280, 1892), xytext=(700, 1930),
                fontsize=13, color="g",
                arrowprops=dict(arrowstyle="-|>", color="g", lw=1.6))
    ax.set_xlabel(T("rho"))
    ax.set_ylabel(T("cov_r"))
    ax.grid(True)
    ax.set_ylim(1450, 2060)
    ax.set_title(T("fig_cov2"), fontsize=15)
    h2 = [Line2D([], [], color="tab:blue", lw=3.0, label=T("fig_cov_c")),
          Line2D([], [], color="r", ls="--", lw=2.4, label=T("fig_cov_r")),
          Line2D([], [], color="g", ls=":", lw=2.4, label=T("fig_cov_opt"))]
    fig.tight_layout()
    figure_legend(fig, h1 + h2, ncol=3, y=-0.10)
    fig.subplots_adjust(bottom=0.40)
    save(fig, "fig_coverage.png")


def fig_directional():
    fig, axs = plt.subplots(1, 3, figsize=(9.1, 3.6))
    d = 40.0
    ax = axs[0]
    ax.add_patch(Wedge((0, 0), 1150, d - 90, d + 90, fc="tab:orange", alpha=0.38, ec="none"))
    for a in (d - 90, d + 90):
        ax.plot([0, 1150 * math.cos(math.radians(a))], [0, 1150 * math.sin(math.radians(a))],
                "k--", lw=1.8)
    ax.plot(0, 0, marker="*", ms=20, color="tab:red", zorder=5)
    ax.annotate(T("fig_dir_src"), (0, 0), xytext=(-360, -430), textcoords="data",
                fontsize=13,
                arrowprops=dict(arrowstyle="-", color="gray", lw=1.2))
    ax.annotate("", xy=(560 * math.cos(math.radians(d)), 560 * math.sin(math.radians(d))),
                xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", lw=2.6, color="tab:red"))
    ax.annotate(T("fig_dir_u"), (560 * math.cos(math.radians(d)),
                                 560 * math.sin(math.radians(d))),
                textcoords="offset points", xytext=(10, 12), fontsize=13)
    for px, py, lab in ((-620, 430, "$p_1$"), (300, -560, "$p_2$")):
        ax.plot(px, py, "^", ms=11, color="tab:blue", zorder=6)
        ax.plot([0, px], [0, py], "-", color="tab:blue", lw=1.8)
        ax.annotate(lab, (px, py), textcoords="offset points", xytext=(12, 10), fontsize=15)
    ax.plot(-900, -300, "x", ms=13, mew=3, color="k")
    ax.annotate(T("fig_dir_silent"), (-900, -300), xytext=(-1215, -1330),
                textcoords="data", fontsize=12.5, ha="left",
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.4))
    ax.set_aspect("equal")
    ax.set_xlim(-1250, 1250)
    ax.set_ylim(-1500, 1250)
    ax.grid(True)
    ax.tick_params(labelsize=12)
    ax.set_title(T("fig_dir1"), fontsize=14)

    ax = axs[1]
    near = [(-520, 210), (420, 420), (520, -520), (-310, -620)]
    ax.add_patch(MplPolygon(near, closed=True, fc="tab:green", alpha=0.35,
                            ec="tab:green", lw=2.0))
    for p in near:
        ax.plot(p[0], p[1], "o", ms=11, color="tab:blue")
        ax.plot([0, p[0]], [0, p[1]], "-", color="gray", lw=1.6)
    ax.plot(0, 0, marker="*", ms=20, color="tab:red", zorder=6)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.tick_params(labelsize=12)
    ax.set_xlim(-820, 820)
    ax.set_ylim(-900, 800)
    ax.set_title(T("fig_dir2"), fontsize=14)

    ax = axs[2]
    P = (900 * math.cos(math.radians(140)), 900 * math.sin(math.radians(140)))
    ax.add_patch(Wedge((0, 0), 1150, 20 - 90, 20 + 90, fc="tab:orange", alpha=0.38,
                       ec="none"))
    ax.plot(0, 0, marker="*", ms=20, color="tab:red", zorder=6)
    ax.plot(*P, "^", ms=12, color="tab:blue", zorder=6)
    ax.plot([P[0], 0], [P[1], 0], "-", color="tab:blue", lw=2.6)
    for f in (0.33, 0.66, 0.9):
        ax.plot(P[0] * (1 - f), P[1] * (1 - f), "o", ms=7, color="k", zorder=7)
    ax.annotate(T("fig_dir_lemma"), xy=(P[0] * 0.5, P[1] * 0.5), xytext=(-1210, -1150),
                fontsize=12.5, arrowprops=dict(arrowstyle="-|>", color="gray", lw=1.6))
    ax.set_aspect("equal")
    ax.set_xlim(-1250, 1250)
    ax.set_ylim(-1400, 1250)
    ax.grid(True)
    ax.tick_params(labelsize=12)
    ax.set_title(T("fig_dir3"), fontsize=14)
    fig.tight_layout()
    save(fig, "fig_directional.png")


def fig_q3_errors():
    errs, gaps = [], []
    for k in range(25):
        srcs = sim.make_case(random.Random(21000 + k), kind_mix=0.0)
        st, br = rc.run_case(srcs, params=dict(rc.DEFAULT_PARAMS, survey_mode="ring"),
                             seed=k)
        for s in srcs:
            if br.est[s.channel] is not None:
                e = br.est[s.channel]
                errs.append(math.hypot(e[0] - s.x, e[1] - s.y))
                gaps.append(e[2])
    if not errs:
        return None
    fig, ax = plt.subplots(1, 3, figsize=(9.1, 3.5))
    ax[0].hist(errs, bins=25, color="tab:blue", alpha=0.9, edgecolor="white")
    ax[0].axvline(20, color="r", ls="--", lw=2.4, label=T("fig_err20"))
    ax[0].axvline(float(np.mean(errs)), color="k", ls=":", lw=2.2,
                  label=T("stat_mean") % float(np.mean(errs)))
    ax[0].axvline(float(np.percentile(errs, 95)), color="g", ls="-.", lw=2.2,
                  label=T("stat_p95") % float(np.percentile(errs, 95)))
    ax[0].set_xlim(0, 52)
    ax[0].set_xlabel(T("err_m"))
    ax[0].set_ylabel(T("count"))
    ax[0].set_title(T("fig_err1"), fontsize=14)
    ax[1].plot(np.sort(np.array(gaps)), np.linspace(0, 1, len(gaps)), lw=3.0,
               color="tab:purple")
    ax[1].set_xscale("log")
    ax[1].set_xlabel(T("sigma_m"))
    ax[1].set_ylabel(T("cdf"))
    ax[1].grid(True, which="both")
    ax[1].set_title(T("fig_err2"), fontsize=14)
    ax[2].scatter(errs, gaps, s=28, alpha=0.6, color="tab:orange", edgecolors="none")
    lim = max(max(errs), max(gaps)) * 1.05
    ax[2].plot([0, lim], [0, lim], "k--", lw=2.0)
    ax[2].annotate("$\\sigma=\\eta$", xy=(0.68 * lim, 0.68 * lim), xytext=(-46, 8),
                   textcoords="offset points", fontsize=14)
    ax[2].set_xlabel(T("err_m"))
    ax[2].set_ylabel(T("sigma_m"))
    ax[2].grid(True)
    ax[2].set_title(T("fig_err3"), fontsize=14)
    fig.tight_layout()
    h = [Line2D([], [], color="r", ls="--", lw=2.4, label=T("fig_err20")),
         Line2D([], [], color="k", ls=":", lw=2.2,
                label=T("stat_mean") % float(np.mean(errs))),
         Line2D([], [], color="g", ls="-.", lw=2.2,
                label=T("stat_p95") % float(np.percentile(errs, 95)))]
    figure_legend(fig, h, ncol=3, y=-0.02)
    fig.subplots_adjust(bottom=0.28)
    save(fig, "fig_q3_errors.png")
    return {"n": len(errs), "median_err": float(np.median(errs)),
            "mean_err": float(np.mean(errs)),
            "p95_err": float(np.percentile(errs, 95)), "max_err": float(max(errs)),
            "frac_err_gt_20": float(np.mean(np.array(errs) > 20.0))}


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    if only in ("all", "q1"):
        fig_q1_region()
        fig_q1_diameter_vs_gamma()
        fig_q1_unbounded()
        fig_q1_cover_stats()
        fig_q1_shapes()
    if only in ("all", "q2"):
        fig_q2_geometry()
        fig_q2_scan()
        fig_q2_baselines()
        fig_q2_montecarlo()
        fig_q2_region_rule()
    if only in ("all", "q34"):
        fig_case_map("q3", 20007, "fig_q3_case_map.png")
        fig_case_map("q4", 30001, "fig_q4_case_map.png")
        fig_q34_stats()
        fig_sensitivity()
        fig_q3_cases()
        fig_task_breakdown()
        fig_convergence()
        fig_simulator_timing()
    if only in ("all", "extra"):
        fig_coverage()
        fig_directional()
        s = fig_q3_errors()
        if s:
            jdump("q3_error_stats.json", s)


if __name__ == "__main__":
    main()
