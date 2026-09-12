# -*- coding: utf-8 -*-
"""fix_spacing_text.py -- 摘要里写的"间距 1100 m 的三角格点"与实际配置（950 m）不符；
同时把灵敏度段落里的旧数字改成新值。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EDITS = [
    ("paper_p1.tex",
     "并把站位加密为间距 1100 m 的三角格点。",
     "并把站位加密为间距 950 m 的三角格点（仿真证明间距不超过 958 m 时格点可自认证），"
     "再沿 $r=1750$ m 补一圈 12 个贴边站位以发现朝外辐射的贴边定向源。",
     "abstract-spacing"),
    ("paper_p3.tex",
     "时间随源数显著变化（10 源 411.2 s，16 源 254.3 s），因为搜索成本近似固定而被更多目标分摊。",
     "时间随源数显著变化（10 源 380.7 s，16 源 251.4 s），因为搜索成本近似固定而被更多目标分摊。",
     "sens-text-q3"),
]
ok = 0
for fname, a, b, tag in EDITS:
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    if a not in s:
        print("  !! 锚点未找到 [%s]" % tag)
        continue
    io.open(p, "w", encoding="utf-8").write(s.replace(a, b, 1))
    ok += 1
    print("  ok [%s]" % tag)
print("更新 %d/%d" % (ok, len(EDITS)))
sys.exit(0 if ok == len(EDITS) else 1)
