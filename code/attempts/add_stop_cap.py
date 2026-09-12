# -*- coding: utf-8 -*-
"""add_stop_cap.py -- max_survey_stops：把主扫描截断到前 N 个站位。

格点本身给出 18~19 个站位（s=900）。若把扫描限制在前 N 个（按到原点的距离
排序、由内向外），则每少一个站位约省 1114 m 行程与 17 次检测。
这是一个显式的"时间/完成率"旋钮，用于在 500 s 附近寻找最高完成率。

限制只作用于**主扫描**（planned stops）；认证所需的额外站位本来就被
max_search_stops 控制，与此独立。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()


def rep(a, b, tag):
    global s
    assert a in s, "anchor missing: " + tag
    s = s.replace(a, b, 1)
    print("  ok:", tag)


rep('    "periodic_cert": True,      # evaluate the certificate during the sweep so',
    '    "max_survey_stops": 0,      # cap on the number of primary survey stops\n'
    '                                # (0 = no cap); an explicit time/ratio knob\n'
    '    "periodic_cert": True,      # evaluate the certificate during the sweep so',
    "parameter")

rep("""    def _pending_stops(self):
        \"\"\"Covering stops that still have to be visited.\"\"\"
        out = []""",
    """    def _pending_stops(self):
        \"\"\"Covering stops that still have to be visited.\"\"\"
        cap = int(self.p.get("max_survey_stops", 0) or 0)
        if cap > 0 and len(self.visited_stops) >= cap:
            return []
        out = []""",
    "pending cap")

# also stop handing out new primary stops once the cap is reached
rep("""        for p in pending:
            tasks.append(("stop", None, p))
        return tasks""",
    """        cap = int(self.p.get("max_survey_stops", 0) or 0)
        if cap > 0:
            room = cap - len(self.visited_stops)
            pending = pending[:max(room, 0)]
        for p in pending:
            tasks.append(("stop", None, p))
        return tasks""",
    "build cap")

io.open(p, "w", encoding="utf-8").write(s)
print("max_survey_stops installed")
