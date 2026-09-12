# -*- coding: utf-8 -*-
"""fix_region_rule.py -- rewrite fig_q2_region_rule so that the (tiny) positioning
region is actually visible: each panel is a zoom around the source with a locator
inset showing the overall geometry."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

start = s.index("def fig_q2_region_rule():")
end = s.index("# ===========================================================================\n# problems 3 / 4")
new = '''def fig_q2_region_rule():
    """Zoom on the positioning region for three true source ranges; a locator
    inset shows where the two stations and the source are."""
    s1 = (-420.0, 260.0)
    th1 = 63.0
    sol = q2.solve_second_point(s1, th1, r_guard=1000.0)
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 4.3))
    for i, rr in enumerate((300.0, 900.0, 1400.0)):
        a = math.radians(th1)
        G = (s1[0] + rr * math.cos(a), s1[1] + rr * math.sin(a))
        b2 = g.bearing(sol["S2"][0], sol["S2"][1], G[0], G[1])
        res = g.region_from_bearings([s1, sol["S2"]], [th1, b2], 1.0)
        ax = axs[i]
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
        ax.annotate("$G$", G, textcoords="offset points", xytext=(10, 6), fontsize=15)
        ax.set_aspect("equal")
        ax.grid(True)
        half = max(res["diameter"], 2 * res["mec"][2]) * 0.95 + 8
        ax.set_xlim(G[0] - half, G[0] + half)
        ax.set_ylim(G[1] - half, G[1] + half)
        ax.tick_params(labelsize=12)
        ax.set_title(T("fig_q2_r%d" % i) % res["diameter"], fontsize=15)
        ax.set_xlabel(T("x_east"), fontsize=14)
        if i == 0:
            ax.set_ylabel(T("y_north"), fontsize=14)
        # locator inset: overall geometry
        axin = ax.inset_axes([0.60, 0.60, 0.38, 0.38])
        axin.add_patch(Circle(s1, 1000.0, fill=False, ls=":", color="gray", lw=1.2))
        axin.plot([s1[0], G[0]], [s1[1], G[1]], "-", color="tab:blue", lw=2.0)
        axin.plot([sol["S2"][0], G[0]], [sol["S2"][1], G[1]], "-", color="tab:green",
                  lw=2.0)
        axin.plot(*s1, "^", ms=8, color="tab:blue")
        axin.plot(*sol["S2"], marker="*", ms=13, color="red")
        axin.plot(*G, "o", ms=6, color="k")
        axin.set_xlim(-1350, 1250)
        axin.set_ylim(-900, 1700)
        axin.set_aspect("equal")
        axin.set_xticks([])
        axin.set_yticks([])
        axin.set_title(T("fig_inset"), fontsize=11, pad=2)
    fig.suptitle(T("fig_q2_rule_title"), fontsize=16)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save(fig, "fig_q2_region_rule.png")


'''
s = s[:start] + new + s[end:]
io.open(p, "w", encoding="utf-8").write(s)
print("fig_q2_region_rule rewritten")
