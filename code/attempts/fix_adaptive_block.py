# -*- coding: utf-8 -*-
"""fix_adaptive_block.py -- repair the planning block after the adaptive patch."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

broken = """                    if self.p.get("survey_mode") == "adaptive":
                    stops = self.next_search_batch(
                        unresolved, int(self.p.get("adaptive_batch", 4)))
                    stop = stops[0] if stops else None
                    if stops:
                        tour = [("stop", None, q) for q in stops[1:]]
                else:
                    stop, flags = self.next_search_stop(unresolved)
                    if stop is None or len(extra_stops) >= self.p["max_search_stops"]:
                        break
                    extra_stops.append(stop)
                    tour = [("stop", None, extra_stops.pop(0))]"""

fixed = """                    if self.p.get("survey_mode") == "adaptive":
                        # 自适应采样：一次取一批"认证最需要"的站位，
                        # 交给巡回规划排序（单个站位无顺序可言）
                        stops = self.next_search_batch(
                            unresolved, int(self.p.get("adaptive_batch", 4)))
                        if not stops:
                            break
                        tour = [("stop", None, q) for q in stops]
                    else:
                        stop, flags = self.next_search_stop(unresolved)
                        if (stop is None
                                or len(extra_stops) >= self.p["max_search_stops"]):
                            break
                        extra_stops.append(stop)
                        tour = [("stop", None, extra_stops.pop(0))]"""

assert broken in s, "block anchor missing"
s = s.replace(broken, fixed, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("planning block repaired")
