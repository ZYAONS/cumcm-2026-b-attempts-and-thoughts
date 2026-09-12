# -*- coding: utf-8 -*-
"""fix_baselines.py -- Chinese strategy names + infinity markers in the baseline
chart, and a little more room in the timing chart."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

# --- baseline chart -------------------------------------------------------
old = '''def fig_q2_baselines():
    head, rows = load_csv("q2_baselines.csv")
    names = [T("bl_" + r[0].split("_")[0].lower(), r[0].replace("_", " ")) for r in rows]
    mean = [float(r[1]) for r in rows]
    p95 = [float(r[2]) for r in rows]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    b1 = ax.bar(x - 0.21, mean, 0.42, label=T("mean"), color="tab:blue")
    b2 = ax.bar(x + 0.21, p95, 0.42, label=T("p95"), color="tab:orange")
    ax.set_yscale("log")
    ax.bar_label(b1, fmt="%.1f", fontsize=12, padding=2)
    ax.bar_label(b2, fmt="%.1f", fontsize=12, padding=2)
    ax.set_xticks(x)
    ax.set_xticklabels([n.replace(" ", "\\n") for n in names], fontsize=13)
    ax.set_ylabel(T("D_m"))
    ax.set_title(T("fig_q2_base"))
    ax.grid(True, axis="y", which="both")
    ax.legend(loc="upper center", ncol=2, framealpha=0.95)
    ax.set_ylim(8, 20000)
    fig.tight_layout()
    save(fig, "fig_q2_baselines.png")'''

new = '''BL_NAMES = {"A_proposed": "A 本文规则", "B_perp_800": "B 垂直偏移\\n800 m",
            "C_along_800": "C 沿示向度\\n前进 800 m", "D_random": "D 可行域内\\n随机取点",
            "E_oracle": "E 先知策略\\n(性能下界)"}


def fig_q2_baselines():
    head, rows = load_csv("q2_baselines.csv")
    keys = [r[0] for r in rows]
    names = [BL_NAMES.get(k, k) for k in keys]
    mean = [float(r[1]) for r in rows]
    p95 = [float(r[2]) if r[2] not in ("Infinity", "inf", "") else float("nan")
           for r in rows]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
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
    ax.legend(loc="upper center", ncol=2, framealpha=0.95)
    ax.set_ylim(8, 30000)
    fig.tight_layout()
    save(fig, "fig_q2_baselines.png")'''
assert old in s, "baseline anchor missing"
s = s.replace(old, new, 1)

# --- timing chart: more head-room ----------------------------------------
a = '    ax.set_ylim(0, max(dt) * 1.35)\n    save(fig, "fig_simulator_timing.png")'
b = ('    ax.set_ylim(0, max(dt) * 1.45)\n    ax.margins(x=0.02)\n'
     '    save(fig, "fig_simulator_timing.png")')
assert a in s, "timing anchor missing"
s = s.replace(a, b, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("patched baselines + timing")
