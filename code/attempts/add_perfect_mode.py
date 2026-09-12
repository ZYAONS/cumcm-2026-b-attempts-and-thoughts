# -*- coding: utf-8 -*-
"""add_perfect_mode.py -- 把"完美配置"（完成率 1.0000 且时间大幅下降）固化下来。

调参池（种子 30000+，24 例）实测：
    论文配置 s1100 + 认证搜索 : 1.0000（最差 1.0000）/ 874.9 s / 24.0 站
    完美配置 s900  纯扫描     : 1.0000（最差 1.0000）/ 540.3 s / 18.5 站   <- 时间 -38%
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_data.py")
s = io.open(p, encoding="utf-8").read()
anchor = "P4_FAST = dict(P4)"
assert anchor in s, "anchor"
preset = '''# ---------------------------------------------------------------------------
# P4_PERFECT : 完成率 1.0000 且时间比论文配置低约 38 % 的配置。
#
# 调参池（种子 30000+，24 例）：
#     P4 (paper)    : 完成率 1.0000 (最差 1.0000)  874.9 s   24.0 个站位
#     P4_PERFECT    : 完成率 1.0000 (最差 1.0000)  540.3 s   18.5 个站位
#
# 组成：
#   * 间距 900 m 的格点一次扫完——这个间距同时满足
#     "全向源必被发现"（覆盖半径 520 m < R_min）与
#     "定向源可认证"（候选点所在格点三角形的三个顶点都在认证半径 958 m 内），
#     因此把认证搜索整个去掉；
#   * 最远点采样给站位排序，截断时保留均匀覆盖；
#   * relocate：只有一条方位的频道，用"横向偏移二分 + 沿射线爬行"拿第二条方位；
#   * exhaustive：已定位但反复清不掉的源，在 σ 圆盘上做 <=15 m 间距的穷举清除
#     （15/√2 = 10.6 m < 20 m 清除半径，因此**有保证**）。
P4_PERFECT = dict(P4)
P4_PERFECT.update({
    "survey_spacing": 900.0,
    "max_search_stops": 0,
    "verify_margin": 900.0,
    "periodic_cert": True,
    "periodic_cert_every": 1,
    "spread_stops": True,
    "max_survey_stops": 0,
    "clear_bonus": 500.0,
    "locate_sigma": 400.0,
    "hard_attempt_cap": 24,
    "exhaustive_clear": True,
    "relocate": True,
    "enroute_clear": False,
})


'''
s = s.replace(anchor, preset + anchor, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("P4_PERFECT added")

p2 = os.path.join(HERE, "validate_fast.py")
s2 = io.open(p2, encoding="utf-8").read()
s2 = s2.replace("from make_data import P4  # noqa: E402",
                "from make_data import P4, P4_PERFECT  # noqa: E402", 1)
s2 = s2.replace("SAFE = dict(P4)          # the configuration the paper currently reports",
                "SAFE = dict(P4)          # the configuration the paper currently reports\n"
                "PERFECT = dict(P4_PERFECT)   # 1.0000 completion at ~38 % less time")
s2 = s2.replace('        b = ev(FAST, seeds)\n        show("   fast (<500 s target)", b)\n'
                '        out[name] = {"current": a, "fast": b}',
                '        b = ev(FAST, seeds)\n        show("   fast (<500 s target)", b)\n'
                '        c = ev(PERFECT, seeds)\n        show("   perfect (1.0000 target)", c)\n'
                '        out[name] = {"current": a, "fast": b, "perfect": c}')
io.open(p2, "w", encoding="utf-8").write(s2)
print("validate_fast.py compares all three")
