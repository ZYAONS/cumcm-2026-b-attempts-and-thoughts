# -*- coding: utf-8 -*-
"""fix_angle_label.py -- fig_q2_geometry: the angle tag was printed on top of the
baseline and the bearing ray.  Draw a proper angle arc at S1 and put the label in
the empty upper-left corner, outside the data."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
a = """    ax.plot([s1[0], sol["S2"][0]], [s1[1], sol["S2"][1]], "-", color="red", lw=2.2, zorder=4)
    ax.annotate("$\\\\varphi^{*}=%.1f^\\\\circ$" % sol["phi"],
                (0.5 * (s1[0] + sol["S2"][0]), 0.5 * (s1[1] + sol["S2"][1])),
                textcoords="offset points", xytext=(14, -26), fontsize=15, color="red")"""
b = """    ax.plot([s1[0], sol["S2"][0]], [s1[1], sol["S2"][1]], "-", color="red", lw=2.2, zorder=4)
    # angle arc between the measured bearing and the baseline, drawn at S1;
    # the label sits in the empty upper-left corner with a leader line
    ang2 = math.degrees(math.atan2(sol["S2"][1] - s1[1], sol["S2"][0] - s1[0])) % 360.0
    t1, t2 = min(th1, ang2), max(th1, ang2)
    Rarc = 560.0
    ax.add_patch(Arc(s1, 2 * Rarc, 2 * Rarc, angle=0.0, theta1=t1, theta2=t2,
                     color="red", lw=2.2, zorder=5))
    amid = math.radians(0.5 * (t1 + t2))
    ax.annotate("$\\\\varphi^{*}=%.1f^\\\\circ$" % sol["phi"],
                xy=(s1[0] + Rarc * math.cos(amid), s1[1] + Rarc * math.sin(amid)),
                xytext=(-1660, 1180), fontsize=15, color="red", ha="left",
                arrowprops=dict(arrowstyle="-|>", color="red", lw=1.6,
                                connectionstyle="arc3,rad=0.15"))"""
assert a in s, "angle anchor missing"
s = s.replace(a, b, 1)
s = s.replace("from matplotlib.patches import Circle, Polygon as MplPolygon, Wedge",
              "from matplotlib.patches import Arc, Circle, Polygon as MplPolygon, Wedge", 1)
io.open(p, "w", encoding="utf-8").write(s)
print("angle label moved out of the data")
