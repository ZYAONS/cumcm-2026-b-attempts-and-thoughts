# -*- coding: utf-8 -*-
"""fix_sim_r1b.py -- the HTTP layer checked the server level robot_id only; make
it also consult the id that the arena bound on the first successful /enter."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "simulator.py")
s = io.open(p, encoding="utf-8").read()
a = """        if st.robot_id is not None and body["robot_id"] != st.robot_id:
            return self._send(200, {"accepted": False,
                                    "real_timestamp_ms": int(time.time() * 1000),
                                    "virtual_time_s": 0.0})"""
b = """        # the id is either fixed at launch or bound by the first /enter
        bound = st.robot_id
        if bound is None and st.arena is not None:
            bound = getattr(st.arena, "robot_id", None)
        if bound is not None and body["robot_id"] != bound:
            return self._send(200, {"accepted": False,
                                    "real_timestamp_ms": int(time.time() * 1000),
                                    "virtual_time_s": 0.0})"""
assert a in s, "anchor missing"
s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("HTTP robot_id binding fixed")
