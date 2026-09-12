# -*- coding: utf-8 -*-
"""fix_after_shrink2.py -- short axis labels so nothing collides on the smaller
canvas."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_figures.py")
s = io.open(p, encoding="utf-8").read()

# q34 stats: short tick labels ("全向/混合" is explained in the caption)
s = s.replace('''    names = [T("q3_name").replace("\\n", ""), T("q4_name").replace("\\n", "")]''',
              '''    names = [T("q3_short"), T("q4_short")]''', 1)

# region-rule: panel (a) does not need its own x label
s = s.replace('''    ax.set_title("(a) 几何总览", fontsize=15)
    ax.set_xlabel(T("x_east"), fontsize=14)
    ax.set_ylabel(T("y_north"), fontsize=14)''',
              '''    ax.set_title("(a) 几何总览", fontsize=15)
    ax.set_ylabel(T("y_north"), fontsize=14)''', 1)
io.open(p, "w", encoding="utf-8").write(s)

# new label entries
import json
lp = os.path.join(HERE, "zh_labels.json")
d = json.load(io.open(lp, encoding="utf-8-sig"))
d["q3_short"] = "问题 3"
d["q4_short"] = "问题 4"
io.open(lp, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
print("labels shortened")
