# -*- coding: utf-8 -*-
"""fix_sim_from_verify.py -- two real defects found by verify_simulator.py.

  R1  robot_id was only enforced when the server was started with an explicit
      robot_id; started without one (the default) every id was accepted.
      Now the arena binds the id of the first successful /enter, which is what
      the official runtime does (it knows the team).

  R2  svd_deg was rounded to two decimals after the +-1 deg error was added, so
      the reported value could deviate from the true bearing by up to
      1 deg + 0.005 deg.  Attachment 1 makes the +-1 deg bound a hard statement
      about the reading, so the rounded value is now pulled back inside it.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "simulator.py")
s = io.open(p, encoding="utf-8").read()

# ---- R1: bind the robot id on the first successful enter ------------------
a = """    def enter(self, robot_id, request_id):
        if self.started:
            return self._reject()
        self.started = True"""
b = """    def enter(self, robot_id, request_id):
        if self.started:
            return self._reject()
        self.started = True
        if self.robot_id is None:
            # the official runtime knows the team; binding on the first enter
            # reproduces that, so a later different id is rejected
            self.robot_id = robot_id"""
assert a in s, "R1 anchor"
s = s.replace(a, b, 1)

a = """        self.virtual_time = 0.0
        self.pos = (0.0, 0.0)
        self.channel = 1
        self.started = False"""
b = """        self.virtual_time = 0.0
        self.pos = (0.0, 0.0)
        self.channel = 1
        self.robot_id = None
        self.started = False"""
assert a in s, "R1 anchor 2"
s = s.replace(a, b, 1)

# ---- R2: keep the reported bearing inside +- BEARING_ERROR ----------------
a = """                    svd = (true_brg + _loc_error(target[0], target[1], channel)) % 360.0
                    svd = round(svd, 2)"""
b = """                    svd = (true_brg + _loc_error(target[0], target[1], channel)) % 360.0
                    svd = _round_within_error(svd, true_brg, BEARING_ERROR)"""
assert a in s, "R2 anchor"
s = s.replace(a, b, 1)

a = """def _loc_error(px, py, channel):"""
b = """def _round_within_error(value, truth, bound):
    \"\"\"
    Round `value` to two decimals without letting the deviation from `truth`
    exceed `bound`.  Rounding alone can push a value that sits exactly on the
    limit a few thousandths of a degree outside it, which would violate the
    +-1 deg guarantee of attachment 1.
    \"\"\"
    v = round(value, 2)
    d = ((v - truth + 180.0) % 360.0) - 180.0
    while abs(d) > bound and abs(round(d, 6)) > 0.0:
        v = round(v - math.copysign(0.01, d), 2)
        d = ((v - truth + 180.0) % 360.0) - 180.0
    return v


def _loc_error(px, py, channel):"""
assert a in s, "R2 helper anchor"
s = s.replace(a, b, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("simulator patched: R1 robot_id binding, R2 bearing rounding")
