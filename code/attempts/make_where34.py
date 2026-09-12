# -*- coding: utf-8 -*-
"""make_where34.py -- create where_q34.py (mode-aware cost breakdown)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
s = io.open(os.path.join(HERE, "where_q4.py"), encoding="utf-8").read()
s = s.replace("from make_data import P4", "from make_data import P3, P4")
s = s.replace("import robot_core as rc",
              "import robot_core as rc\n\nMODE = os.environ.get('MODE', 'q4')")
s = s.replace('    p.update(P4)', "    p.update(P3 if MODE == 'q3' else P4)")
s = s.replace("sim.make_case(random.Random(seed), kind_mix=0.5)",
              "sim.make_case(random.Random(seed), kind_mix=(0.0 if MODE == 'q3' else 0.5))")
s = s.replace('"where_q4.json"', '"where_%s.json" % MODE')
io.open(os.path.join(HERE, "where_q34.py"), "w", encoding="utf-8").write(s)
print("where_q34.py written")
