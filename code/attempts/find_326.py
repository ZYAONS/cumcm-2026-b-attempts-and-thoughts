# -*- coding: utf-8 -*-
"""find_326.py -- 找出 326.8 这个数字记录在哪里，判断它是否已过期。"""
import glob
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))

print("=== data/*.json 中含 326. 的文件 ===")
for f in glob.glob(os.path.join(ROOT, "data", "*.json")):
    s = io.open(f, encoding="utf-8", errors="ignore").read()
    if "326." in s:
        print("  HIT", os.path.basename(f))

print("=== q34_agg.json 摘要 ===")
try:
    d = json.load(io.open(os.path.join(ROOT, "data", "q34_agg.json"), encoding="utf-8"))
    for k, v in d.items():
        if isinstance(v, dict):
            print("  %-10s mean_time=%.1f ratio=%.4f n=%s"
                  % (k, v.get("mean_time", -1), v.get("mean_ratio", -1), v.get("n_cases")))
except Exception as exc:
    print("  ERR", exc)

print("=== q3_agg.json（刚重跑） ===")
try:
    d = json.load(io.open(os.path.join(ROOT, "data", "q3_agg.json"), encoding="utf-8"))
    print("  ", {k: d[k] for k in ("n_cases", "mean_ratio", "mean_time", "mean_travel")})
except Exception as exc:
    print("  ERR", exc)

print("=== 文档中提到 326.8 的位置 ===")
for pat in ("*.md", "report/*.md", "paper/*.tex"):
    for f in glob.glob(os.path.join(ROOT, pat)):
        s = io.open(f, encoding="utf-8", errors="ignore").read()
        if "326.8" in s:
            print("  HIT", os.path.relpath(f, ROOT))
