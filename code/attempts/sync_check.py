# -*- coding: utf-8 -*-
"""sync_check.py -- 盘点论文里用到的每个数字与当前数据文件是否一致。"""
import glob
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))


def j(name):
    p = os.path.join(ROOT, "data", name)
    if not os.path.exists(p):
        return None
    return json.load(io.open(p, encoding="utf-8"))


print("=== 数据文件现状 ===")
for name in ("q3_agg.json", "q4_agg.json", "q4_alldir_agg.json", "q4_omni_agg.json",
             "q34_agg.json", "policy_compare.json", "formal_q3_formal.json",
             "formal_q4_formal.json", "q3_greedy_agg.json", "q4_greedy_agg.json"):
    d = j(name)
    if d is None:
        print("  %-26s (缺)" % name)
        continue
    mt = os.path.getmtime(os.path.join(ROOT, "data", name))
    import datetime
    stamp = datetime.datetime.fromtimestamp(mt).strftime("%m-%d %H:%M")
    if isinstance(d, dict) and "mean_time" in d:
        print("  %-26s [%s] n=%-3s ratio=%.4f  time=%7.1f  travel=%6.0f"
              % (name, stamp, d.get("n_cases"), d.get("mean_ratio"),
                 d.get("mean_time", -1), d.get("mean_travel", -1)))
    elif isinstance(d, dict) and "q3" in d:
        print("  %-26s [%s] q3=%.1f/%.4f(q4=%s)  q4=%.1f/%.4f"
              % (name, stamp, d["q3"].get("mean_time", -1), d["q3"].get("mean_ratio", -1),
                 d["q3"].get("n_cases"), d["q4"].get("mean_time", -1),
                 d["q4"].get("mean_ratio", -1)))
    elif isinstance(d, list):
        print("  %-26s [%s] %d 条记录" % (name, stamp, len(d)))
    else:
        print("  %-26s [%s] %s" % (name, stamp, str(d)[:80]))

print()
print("=== 论文中出现的关键数字 ===")
tex = io.open(os.path.join(ROOT, "paper", "paper.tex"), encoding="utf-8").read()
for key in ("331.0", "330.98", "326.8", "313.3", "661.0", "595.9", "579", "268.4",
            "375.2", "399.6", "602.6", "654.5", "718.8", "14715", "28476", "0.9574"):
    n = tex.count(key)
    if n:
        print("  %-8s 出现 %d 次" % (key, n))
