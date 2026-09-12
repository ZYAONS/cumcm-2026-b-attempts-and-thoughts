# -*- coding: utf-8 -*-
"""fix_angle_leader.py -- route the angle leader line so that it does not cross
the baseline."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()
a = """    amid = math.radians(0.5 * (t1 + t2))
    ax.annotate("$\\\\varphi^{*}=%.1f^\\\\circ$" % sol["phi"],
                xy=(s1[0] + Rarc * math.cos(amid), s1[1] + Rarc * math.sin(amid)),
                xytext=(-1660, 1180), fontsize=15, color="red", ha="left",
                arrowprops=dict(arrowstyle="-|>", color="red", lw=1.6,
                                connectionstyle="arc3,rad=0.15"))"""
b = """    # the leader stops at the LEFT end of the arc, so it never crosses the
    # baseline or the bearing ray
    aend = math.radians(t2)
    ax.annotate("$\\\\varphi^{*}=%.1f^\\\\circ$" % sol["phi"],
                xy=(s1[0] + Rarc * math.cos(aend), s1[1] + Rarc * math.sin(aend)),
                xytext=(-1740, 940), fontsize=15, color="red", ha="left",
                arrowprops=dict(arrowstyle="-|>", color="red", lw=1.6))"""
assert a in s, "leader anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("leader rerouted")
