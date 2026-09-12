# -*- coding: utf-8 -*-
"""retune_grids.py -- narrower, faster grids for the second optimization round
(the incremental certification scan made each evaluation cheap, but the
search now runs to completion, so the grids only need the parameters that move
the time/ratio trade-off)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "optimize_q34.py")
s = io.open(p, encoding="utf-8").read()

start = s.index("GRIDS = {")
end = s.index("BASE = {")
new = '''GRIDS = {
    "q3": {
        "ring_radius": [1150.0, 1200.0, 1250.0, 1320.0],
        "probe_spacing": [450.0, 650.0, 850.0],
        "locate_sigma": [220.0, 320.0, 440.0],
        "clear_bonus": [0.0, 260.0, 450.0],
        "probe_min_angle": [12.0, 22.0, 35.0],
        "search_cost_bias": [30.0, 70.0, 150.0],
        "term_cap": [300.0, 420.0, 600.0],
        "endgame_radius": [70.0, 90.0, 130.0],
    },
    "q4": {
        "survey_spacing": [850.0, 950.0, 1050.0, 1200.0],
        "probe_spacing": [450.0, 650.0, 850.0],
        "locate_sigma": [220.0, 320.0, 440.0],
        "clear_bonus": [0.0, 260.0, 450.0],
        "probe_min_angle": [12.0, 22.0, 35.0],
        "search_cost_bias": [30.0, 70.0, 150.0],
        "max_attempts": [4, 6, 10],
        "rim_step": [100.0, 130.0, 180.0],
        "max_rim_patrols": [4, 8, 14],
    },
}

'''
s = s[:start] + new + s[end:]
io.open(p, "w", encoding="utf-8").write(s)
print("grids narrowed")
