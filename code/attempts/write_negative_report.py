# -*- coding: utf-8 -*-
"""write_negative_report.py -- consolidate every optional change that was tried
this round into a machine readable report, so the document quotes real numbers.

Sources: data/confirm_rim.json, data/clear_budget.json, data/q4_tradeoff.json,
data/ab_routing.json, data/necessity_34.json, data/final_validation.json
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data"))


def load(name):
    p = os.path.join(OUT, name)
    if not os.path.exists(p):
        return None
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


rep = {}
for n in ("confirm_rim", "clear_budget", "q4_tradeoff", "ab_routing",
          "necessity_34", "final_validation", "simulator_verification"):
    v = load(n + ".json")
    if v is not None:
        rep[n] = v
        print("loaded", n)

with io.open(os.path.join(OUT, "optional_changes.json"), "w",
             encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)
print("report -> data/optional_changes.json")
