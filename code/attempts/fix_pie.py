# -*- coding: utf-8 -*-
"""fix_pie.py -- make the time-composition figure legible: percentages only on
the large slices, full list in a legend."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

old = '''    wedges, texts, autotexts = ax.pie(
        vals, labels=labels, autopct="%1.1f%%", colors=colors,
        textprops={"fontsize": 14}, startangle=95,
        wedgeprops={"edgecolor": "white", "linewidth": 2})
    for t in autotexts:
        t.set_fontsize(13)
    ax.set_title(T("fig_pie"))
    save(fig, "fig_q3_time_pie.png")'''

new = '''    total = float(sum(vals))
    wedges, texts, autotexts = ax.pie(
        vals, labels=None,
        autopct=lambda pct: ("%.1f%%" % pct) if pct >= 5.0 else "",
        colors=colors, textprops={"fontsize": 15}, startangle=95,
        pctdistance=0.62, wedgeprops={"edgecolor": "white", "linewidth": 2})
    for t in autotexts:
        t.set_fontsize(15)
    for i, w in enumerate(wedges):
        if vals[i] / total < 0.05:
            ang = math.radians((w.theta1 + w.theta2) / 2.0)
            ax.annotate("%s %.1f%%" % (labels[i], 100.0 * vals[i] / total),
                        xy=(0.86 * math.cos(ang), 0.86 * math.sin(ang)),
                        xytext=(1.45 * math.cos(ang), 1.45 * math.sin(ang)),
                        fontsize=13, ha="center", va="center",
                        arrowprops=dict(arrowstyle="-", color="gray", lw=1.2))
    ax.legend(wedges, ["%s  %.1f%%" % (labels[i], 100.0 * vals[i] / total)
                       for i in range(len(labels))],
              loc="upper center", bbox_to_anchor=(0.5, 0.02), fontsize=13, ncol=2,
              frameon=False)
    ax.set_title(T("fig_pie"), pad=18)
    save(fig, "fig_q3_time_pie.png")'''
assert old in s, "pie anchor missing"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("patched pie")
