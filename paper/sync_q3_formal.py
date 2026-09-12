# -*- coding: utf-8 -*-
"""sync_q3_formal.py -- 把新一轮问题三正式测试（Q3-990001..3）写进论文表。"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
rows = json.load(io.open(os.path.join(ROOT, "data", "formal_q3_formal.json"),
                         encoding="utf-8"))
for r in rows:
    print("%s n=%s cleared=%s mean=%.1f wall=%.2f" %
          (r["case_code"], r["n_sources"], r["n_cleared"], r["mean_time"], r["wall_s"]))

p = os.path.join(HERE, "paper_p3.tex")
s = io.open(p, encoding="utf-8").read()
start = s.find(r"\ttfamily Q3-970001-")
end = s.find(r"\\", s.find(r"\ttfamily Q3-970003-")) + 2
assert start > 0 and end > start, "formal table anchor missing"

def latex_code(code):
    """把案例编码拆成带 \\hspace{0pt} 的可断行形式"""
    head, tail = code.split("-", 1)
    seed, chans = tail.split("-", 1)
    parts = [chans[i:i + 8] for i in range(0, len(chans), 8)]
    return ("\\ttfamily %s-%s-\\hspace{0pt}%s" %
            (head, seed, "\\hspace{0pt}".join(parts)))

lines = []
for i, r in enumerate(rows):
    lines.append("%s & %s（%s） & %.1f & %.1f\\\\"
                 % (latex_code(r["case_code"]), r["n_cleared"], r["n_sources"],
                    r["mean_time"], r.get("wall_s", 0.0)))
new = "\n".join(lines) + "\n"
s = s[:start] + new + s[end - 1:]
io.open(p, "w", encoding="utf-8").write(s)
print("tab:q3formal 已更新为 %d 条" % len(rows))
sys.exit(0)
