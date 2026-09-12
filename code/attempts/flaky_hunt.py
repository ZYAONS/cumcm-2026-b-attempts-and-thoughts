# -*- coding: utf-8 -*-
"""
flaky_hunt.py -- 找出验证套件里偶发失败的那一项。

现象：8 次里有 1~2 次是 67/68。需要定位是哪一项、以及为什么它会偶发。

用法：python flaky_hunt.py [runs]
"""
import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.normpath(os.path.join(HERE, "..", "logs", "flaky"))
os.makedirs(LOG, exist_ok=True)

if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    bad = []
    for i in range(runs):
        r = subprocess.run([sys.executable, "verify_simulator.py"],
                           capture_output=True, text=True, encoding="utf-8",
                           cwd=HERE)
        out = (r.stdout or "") + (r.stderr or "")
        m = re.search(r"(\d+)/68 checks passed", out)
        groups = re.findall(r"group ([A-H]) :\s*(\d+)/\s*(\d+)", out)
        line = "run %2d : %s   %s" % (i, m.group(0) if m else "???",
                                      " ".join("%s%s/%s" % g for g in groups))
        print(line, flush=True)
        with io.open(os.path.join(LOG, "run_%02d.txt" % i), "w",
                     encoding="utf-8") as f:
            f.write(out)
        if m and m.group(1) != "68":
            bad.append((i, groups))
    if bad:
        print("\nFAILING RUNS:")
        for i, g in bad:
            print("  run %d : %s" % (i, " ".join("%s%s/%s" % x for x in g)))
    else:
        print("\nall %d runs passed" % runs)
