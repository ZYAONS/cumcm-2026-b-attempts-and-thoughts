# -*- coding: utf-8 -*-
"""dump_numbers.py -- 把论文要用到的全部数字打印出来，供逐项改写论文。"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


def j(name):
    return json.load(io.open(os.path.join(DATA, name), encoding="utf-8"))


for name in ("q3_agg", "q4_agg", "q4_alldir_agg", "q4_omni_agg"):
    d = j(name + ".json")
    print("== %s" % name)
    print("   n=%s ratio=%.4f min=%.4f time=%.1f median=%.1f sd=%.1f travel=%.0f"
          " measure=%.1f clears=%.1f vtime=%.0f"
          % (d.get("n_cases"), d["mean_ratio"], d.get("min_ratio", -1), d["mean_time"],
             d.get("median_time", -1), d.get("sd_time", -1), d["mean_travel"],
             d.get("mean_measure", -1), d.get("mean_clear_actions", -1),
             d.get("mean_vtime", -1)))

print("== q34_agg")
d = j("q34_agg.json")
for k, v in d.items():
    print("   %-10s n=%s ratio=%.4f time=%.1f travel=%.0f"
          % (k, v.get("n_cases"), v.get("mean_ratio", -1), v.get("mean_time", -1),
             v.get("mean_travel", -1)))

print("== policy_compare")
d = j("policy_compare.json")
for k, v in d.items():
    mt = v.get("mean_time", -1)
    print("   %-12s ratio=%.4f time=%s travel=%.0f"
          % (k, v.get("mean_ratio", -1),
             "inf" if mt == float("inf") else "%.1f" % mt, v.get("mean_travel", -1)))

print("== formal tests")
for mode in ("q3", "q4"):
    for r in j("formal_%s_formal.json" % mode):
        print("   %s n=%s cleared=%s mean=%.1f wall=%.2f vtime=%.0f travel=%.0f meas=%s"
              % (r["case_code"], r["n_sources"], r["n_cleared"], r["mean_time"],
                 r.get("wall_s", 0), r["virtual_time"], r["travel_m"], r["n_measure"]))

print("== sensitivity")
import csv
for f in ("q3_sensitivity.csv", "q4_sensitivity.csv"):
    print("  ", f)
    with io.open(os.path.join(DATA, f), encoding="utf-8") as fh:
        for row in csv.reader(fh):
            print("     %-22s %s %s" % tuple(row))
