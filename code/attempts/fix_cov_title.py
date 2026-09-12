# -*- coding: utf-8 -*-
"""fix_cov_title.py -- the long left title of the coverage figure ran into the
right panel's y label; shorten both panel titles."""
import io
import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
lp = os.path.join(HERE, "zh_labels.json")
d = json.load(io.open(lp, encoding="utf-8-sig"))
d["fig_cov1"] = "(a) 七点覆盖配置"
d["fig_cov2"] = "(b) 六边形半径的选取"
io.open(lp, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
print("titles shortened")
