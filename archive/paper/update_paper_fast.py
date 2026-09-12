# -*- coding: utf-8 -*-
"""update_paper_fast.py -- refresh the problem-4 numbers in the paper after the
32 % speed-up (completion unchanged)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    hit = 0
    for a, b in pairs:
        if a not in s:
            print("  -- not found: %s" % a[:60].replace("\n", " "))
            continue
        s = s.replace(a, b, 1)
        hit += 1
    io.open(p, "w", encoding="utf-8").write(s)
    print("  %s : %d replaced" % (fname, hit))


edit("paper_p1.tex", [
    ("60 组混合演练完成率 \\textbf{100\\%}，平均定位清除时间 \\textbf{888.3} s；三次正式测试清除 11/11、12/12、11/11，平均时间 1133.1 s、945.2 s、1193.4 s。",
     "60 组混合演练完成率 \\textbf{100\\%}，平均定位清除时间 \\textbf{597.0} s；三次正式测试清除 14/14、12/12、14/14，平均时间 503.5 s、714.4 s、519.5 s（均值 579.2 s）。"),
])

edit("paper_p3.tex", [
    ("规划式（本文） & 四 & \\textbf{1.000} & 888.3 & 42629\\\\",
     "规划式（本文） & 四 & \\textbf{1.000} & 597.0 & 33889\\\\"),
    ("\\hspace{0pt}0810131718\\hspace{0pt}20 & 11（11） & 1133.1 & 7.4\\\\",
     "\\hspace{0pt}0810131718\\hspace{0pt}20 & \\textbf{14（14）} & 503.5 & 3.9\\\\"),
    ("\\hspace{0pt}0911121516\\hspace{0pt}1920 & \\textbf{12（12）} & 945.2 & 5.9\\\\",
     "\\hspace{0pt}0911121516\\hspace{0pt}1920 & \\textbf{12（12）} & 714.4 & 4.1\\\\"),
    ("\\hspace{0pt}1314151718\\hspace{0pt}19 & 11（11） & 1193.4 & 7.3\\\\",
     "\\hspace{0pt}1314151718\\hspace{0pt}19 & \\textbf{14（14）} & 519.5 & 2.3\\\\"),
    ("混合（全向/定向各 50\\%） & 60 & \\textbf{1.0000} & 888.3\\\\",
     "混合（全向/定向各 50\\%） & 60 & \\textbf{1.0000} & 597.0\\\\"),
    ("全部为定向源 & 30 & \\textbf{1.0000} & 983.4\\\\",
     "全部为定向源 & 30 & \\textbf{1.0000} & 652.0\\\\"),
    ("全部为全向源 & 30 & 1.0000 & 860.6\\\\",
     "全部为全向源 & 30 & 1.0000 & 583.0\\\\"),
])
print("done")
