# -*- coding: utf-8 -*-
"""adopt_best.py -- 把本轮的最优配置固化为默认（严格优于原配置）。

四池 120 例（种子 62000+/51000+/12000+/30000+，各 30 例），按最差池判定：

    原 P4（s1100 + 认证搜索，无贴边环）      最差 0.9978   880.7 s   24.0 站   1/120 失败
    新配置（s950 + 贴边环12@1750 + 边距700） **最差 0.9978   597.0 s**  24.4 站   1/120 失败

**完成率完全相同，时间下降 32%。** 因此新配置严格占优，直接替换 P4。

新配置的四个组成：
  * 间距 950 m 的三角格点（覆盖半径 548 m < R_min，且间距 <= 认证半径 958 m，
    候选点所在格点三角形的三顶点都在认证半径内 —— 认证可由格点自身完成）；
  * 贴边环 12 个点 @ r=1750 m —— 边界附近的候选点最难认证，也最难发现，
    预先按环布站既省下昂贵的自适应补站，又提高了边界源的发现率；
  * 认证边距 700 m —— 只要求认证到 r <= 1100，边界的发现交给贴边环，
    避免为"永远无法用域内读数认证的贴边候选点"浪费站位；
  * 保留认证搜索（上限 40 站）兜底，处理格点未覆盖的零星候选点。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- make_data
p = os.path.join(HERE, "make_data.py")
s = io.open(p, encoding="utf-8").read()

old_p4 = None
i = s.index("P4 = ")
j = s.index("\n\n", i)
print("--- current P4 ---")
print(s[i:j][:900])

new_p4 = '''P4 = {
    "survey_mode": "lattice",
    "survey_spacing": 950.0,      # 覆盖半径 548 m < R_min；间距 <= 认证半径 958 m
    "directional": True,
    # 本轮新增：贴边环 + 认证边距（四池 120 例：880.7 s -> 597.0 s，完成率不变）
    "rim_ring_n": 12,             # 贴边环 12 个站位
    "rim_ring_r": 1750.0,
    "verify_margin": 700.0,       # 只认证 r <= 1100；边界发现交给贴边环
    "max_search_stops": 40,       # 认证搜索兜底
    "periodic_cert": True,
    "periodic_cert_every": 1,
    "spread_stops": True,
    "max_survey_stops": 0,
    "clear_bonus": 500.0,
    "locate_sigma": 400.0,
    "probe_spacing": 650.0,
    "relocate": True,
    "exhaustive_clear": True,
    "enroute_clear": False,
    "hard_attempt_cap": 24,
}'''
s = s[:i] + new_p4 + s[j:]
io.open(p, "w", encoding="utf-8").write(s)
print("--- P4 replaced ---")

p2 = os.path.join(HERE, "run_http_tests.py")
s2 = io.open(p2, encoding="utf-8").read()
print("run_http_tests uses P4:", "from make_data import P3, P4" in s2)
