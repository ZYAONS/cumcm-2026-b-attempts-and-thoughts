# -*- coding: utf-8 -*-
"""inset_to_panel.py -- replace the overlaid zoom insets by real panels.

  fig_q1_region      : [overall geometry | zoom of the positioning region]
  fig_q2_region_rule : [overview | zoom for r = 300 / 900 / 1400 m]
Nothing is drawn on top of anything else any more.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

# ------------------------------------------------------------------ Q1 ----
start = s.index("def fig_q1_region():")
end = s.index("def fig_q1_diameter_vs_gamma():")
new_q1 = '''def fig_q1_region():
    """Left: overall geometry.  Right: zoom of the positioning region.

    The zoom is a real panel (not an inset), so nothing covers the main figure.
    """
    S1, S2 = (0.0, 0.0), (1200.0, 0.0)
    G = (600.0, 900.0)
    th1, th2 = g.bearing(*S1, *G), g.bearing(*S2, *G)
    res = g.region_from_bearings([S1, S2], [th1, th2], 1.0)
    A, B = res["d_pair"]
    cx, cy, r = res["mec"]
    fig, axs = plt.subplots(1, 2, figsize=(9.8, 4.8))

    ax = axs[0]
    for S, th, c, tag in ((S1, th1, "tab:blue", "$S_1$"), (S2, th2, "tab:green", "$S_2$")):
        for sg in (-1, 1):
            a = math.radians(th + sg)
            ax.plot([S[0], S[0] + 1600 * math.cos(a)], [S[1], S[1] + 1600 * math.sin(a)],
                    ls="--", lw=1.6, color=c, alpha=0.85,
                    label=("$\\pm1^\\circ$ 边界" if (S == S1 and sg == -1) else None))
        a = math.radians(th)
        ax.plot([S[0], S[0] + 1600 * math.cos(a)], [S[1], S[1] + 1600 * math.sin(a)],
                lw=2.8, color=c,
                label=("%s 处示向度方向" % tag))
        ax.plot(*S, "^", color=c, ms=13, zorder=6)
        ax.annotate(tag, S, textcoords="offset points",
                    xytext=(6, -32) if S == S1 else (-34, -32), fontsize=16, zorder=7)
    ax.add_patch(MplPolygon(res["vertices"], closed=True, fc="tab:red", alpha=0.9,
                            ec="tab:red", lw=1.5, zorder=5, label="定位区域 $\\\\mathcal{R}$"))
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
    legend_below(ax, ncol=2, y=-0.16)

    ax = axs[1]
    ax.add_patch(MplPolygon(res["vertices"], closed=True, fc="tab:red", alpha=0.55,
                            ec="tab:red", lw=2.2, zorder=4, label="定位区域 $\\\\mathcal{R}$"))
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
    legend_below(ax, ncol=2, y=-0.16)
    fig.tight_layout()
    save(fig, "fig_q1_region.png")


'''
s = s[:start] + new_q1 + s[end:]

# ------------------------------------------------------------------ Q2 ----
start = s.index("def fig_q2_region_rule():")
end = s.index("# ===========================================================================\n# problems 3 / 4")
new_q2 = '''def fig_q2_region_rule():
    """Panel 1: overview with the three source positions; panels 2-4: the
    positioning region for each of them (real panels, no inset)."""
    s1 = (-420.0, 260.0)
    th1 = 63.0
    sol = q2.solve_second_point(s1, th1, r_guard=1000.0)
    ranges = (300.0, 900.0, 1400.0)
    cols = ("tab:blue", "tab:green", "darkorchid")
    a0 = math.radians(th1)
    Gs = [(s1[0] + rr * math.cos(a0), s1[1] + rr * math.sin(a0)) for rr in ranges]
    fig = plt.figure(figsize=(11.2, 3.9))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.35, 1, 1, 1], wspace=0.42)

    ax = fig.add_subplot(gs[0, 0])
    ax.add_patch(Circle(s1, 1000.0, fill=False, ls=":", color="gray", lw=1.6,
                        label="$R_{\\\\min}=1000$ m"))
    ax.plot([s1[0], sol["S2"][0]], [s1[1], sol["S2"][1]], "-", color="red", lw=2.0)
    for G, rr, col in zip(Gs, ranges, cols):
        ax.plot([s1[0], G[0]], [s1[1], G[1]], "-", color=col, lw=2.0)
        ax.plot([sol["S2"][0], G[0]], [sol["S2"][1], G[1]], "--", color=col, lw=1.6)
        ax.plot(*G, "o", ms=10, color=col, zorder=6)
        ax.annotate("%.0f m" % rr, G, textcoords="offset points", xytext=(8, 6),
                    fontsize=13, color=col)
    ax.plot(*s1, "^", ms=13, color="tab:blue", zorder=6)
    ax.annotate("$S_1$", s1, textcoords="offset points", xytext=(10, -30), fontsize=16)
    ax.plot(*sol["S2"], marker="*", ms=22, color="red", zorder=6)
    ax.annotate("$S_2^{*}$", sol["S2"], textcoords="offset points", xytext=(12, 10),
                fontsize=16)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.tick_params(labelsize=12)
    ax.set_xlim(-1650, 1650)
    ax.set_ylim(-1000, 1900)
    ax.set_title("(a) 几何总览", fontsize=15)
    ax.set_xlabel(T("x_east"), fontsize=14)
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
        half = max(res["diameter"], 2 * res["mec"][2]) * 0.95 + 8
        ax.set_xlim(G[0] - half, G[0] + half)
        ax.set_ylim(G[1] - half, G[1] + half)
        ax.tick_params(labelsize=11)
        ax.set_title(T("fig_q2_r%d" % i) % res["diameter"], fontsize=14, color=col)
        ax.set_xlabel(T("x_east"), fontsize=13)
        if i == 0:
            ax.set_ylabel(T("y_north"), fontsize=13)

    fig.tight_layout()
    figure_legend(fig, [
        Line2D([], [], color="tab:blue", lw=2.0, label="干扰源至 $S_1$ 的视线"),
        Line2D([], [], color="red", lw=2.0, label="检测基线 $S_1S_2^{*}$"),
        MplPolygon([(0, 0)], fc="tab:red", alpha=0.55, ec="tab:red", label="定位区域"),
        Line2D([], [], color="k", lw=2.2, label="直径 $AB$"),
        Line2D([], [], color="k", ls="--", lw=1.8, label="以 $AB$ 为直径的圆"),
        Line2D([], [], color="purple", ls=":", lw=2.2, label="最小包围圆")],
        ncol=3, y=0.005)
    fig.subplots_adjust(bottom=0.28)
    save(fig, "fig_q2_region_rule.png")


'''
s = s[:start] + new_q2 + s[end:]
io.open(p, "w", encoding="utf-8").write(s)
print("insets replaced by real panels")
