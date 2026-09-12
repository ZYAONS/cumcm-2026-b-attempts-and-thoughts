# -*- coding: utf-8 -*-
"""restore_p4_keys.py -- 新 P4 必须保留原 P4 的全部参数键。"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_data.py")
s = io.open(p, encoding="utf-8").read()
old = '''    "max_attempts": 6,
}''' if '"max_attempts": 6,\n}' in s else None

a = '''    "locate_sigma": 400.0,
    "probe_spacing": 650.0,
    "relocate": True,
    "exhaustive_clear": True,
    "enroute_clear": False,
    "hard_attempt_cap": 24,
}'''
b = '''    "locate_sigma": 400.0,
    "probe_spacing": 650.0,
    "probe_min_angle": 22.0,
    "search_cost_bias": 0.0,
    "term_cap": 420.0,
    "endgame_radius": 90.0,
    "max_attempts": 6,
    "ring_radius": 1280.0,
    "outer_ring_gap": 0.0,
    "relocate": True,
    "exhaustive_clear": True,
    "enroute_clear": False,
    "hard_attempt_cap": 24,
}'''
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("P4 keys restored")
import subprocess
print(subprocess.run(["python", "-c",
                      "import make_data as m; print(len(m.P4), 'keys'); "
                      "print(sorted(m.P4))"],
                     capture_output=True, text=True, cwd=HERE).stdout)
