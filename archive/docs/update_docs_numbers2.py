# -*- coding: utf-8 -*-
"""update_docs_numbers2.py -- the remaining table rows (the \\ttfamily and the
hspace break points made the earlier anchors mismatch)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    hit = 0
    for a, b in pairs:
        if a not in s:
            print("  -- not found: %s" % a[:56].replace("\n", " "))
            continue
        s = s.replace(a, b, 1)
        hit += 1
    io.open(p, "w", encoding="utf-8").write(s)
    print("  %s : %d replacements" % (fname, hit))


edit("tech_q3.tex", [
    ("\\hspace{0pt}1415171819 & 15（15） & 268.4 & 1.7 \\\\",
     "\\hspace{0pt}1415171819 & 15（15） & 274.4 & 1.6 \\\\"),
    ("\\hspace{0pt}1819 & 12（12） & 375.2 & 1.3 \\\\",
     "\\hspace{0pt}1819 & 12（12） & 378.4 & 1.3 \\\\"),
    ("\\hspace{0pt}1013141516 & 10（10） & 399.6 & 1.5 \\\\",
     "\\hspace{0pt}1013141516 & 10（10） & 369.0 & 1.3 \\\\"),
])

edit("tech_q4.tex", [
    ("默认（关闭域外补测） & 0.957 & 661.0 & 28476 \\\\",
     "默认（关闭域外补测） & 0.9965 & 937.9 & 46450 \\\\"),
    ('注意"全全向"场景在本策略下也能达到 1.000，但平均时间（535.7 s）高于问题三的 331.0 s——',
     '注意"全全向"场景在本策略下也能达到 1.000，但平均时间（868.4 s）高于问题三的 328.0 s——'),
    ("\\hspace{0pt}0810131718\\hspace{0pt}20 & 11（11） & 602.6 & 2.0 \\\\",
     "\\hspace{0pt}0810131718\\hspace{0pt}20 & 11（11） & 966.4 & 4.3 \\\\"),
    ("\\hspace{0pt}0911121516\\hspace{0pt}1920 & 11（12） & 654.5 & 2.3 \\\\",
     "\\hspace{0pt}0911121516\\hspace{0pt}1920 & \\textbf{12（12）} & 920.8 & 4.3 \\\\"),
    ("\\hspace{0pt}1314151718\\hspace{0pt}19 & 11（11） & 718.8 & 2.3 \\\\",
     "\\hspace{0pt}1314151718\\hspace{0pt}19 & 11（11） & 1204.3 & 4.8 \\\\"),
    ("规划式（本文，正张成认证） & \\textbf{0.957} & 661.0 & 28476 \\\\",
     "规划式（本文，正张成认证） & \\textbf{0.997} & 937.9 & 46450 \\\\"),
])
print("done")
