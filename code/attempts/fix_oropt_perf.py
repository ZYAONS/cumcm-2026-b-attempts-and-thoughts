# -*- coding: utf-8 -*-
"""fix_oropt_perf.py -- the Or-opt loop recomputed the whole tour length for
every candidate relocation, which made one replan O(n^4) and a single problem-4
case take tens of seconds of CPU.

Rolling-horizon planning rebuilds the tour after every task, so only the
near-term prefix matters: Or-opt now works on the first LIMIT tasks and leaves
the tail untouched.  That bounds the cost to a few thousand operations per
replan instead of millions.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "robot_core.py")
s = io.open(p, encoding="utf-8").read()

a = """        # Or-opt: relocate segments of one to three tasks
        def tlen(seq):
            if not seq:
                return 0.0
            tot = self._dist(start, pos[seq[0]])
            for u, v in zip(seq, seq[1:]):
                tot += self._dist(pos[u], pos[v])
            return tot

        improved = True
        rounds = 0
        while improved and rounds < 6:
            improved = False
            rounds += 1
            base = tlen(order)
            for seg in (1, 2, 3):
                if improved or seg > len(order):
                    break
                for i in range(len(order) - seg + 1):
                    block = order[i:i + seg]
                    rest = order[:i] + order[i + seg:]
                    for k in range(len(rest) + 1):
                        if k == i:
                            continue
                        cand = rest[:k] + block + rest[k:]
                        if tlen(cand) < base - 1e-9:
                            order = cand
                            improved = True
                            break
                    if improved:
                        break
        return [tasks[i] for i in order]"""
b = """        # Or-opt: relocate segments of one to three tasks.  The plan is rebuilt
        # after every executed task, so improving the near-term prefix is what
        # matters; the tail is left alone to keep this step cheap.
        LIMIT = int(self.p.get("oropt_limit", 12))
        head = order[:LIMIT]
        tail = order[LIMIT:]

        def tlen(seq):
            if not seq:
                return 0.0
            tot = self._dist(start, pos[seq[0]])
            for u, v in zip(seq, seq[1:]):
                tot += self._dist(pos[u], pos[v])
            return tot

        improved = True
        rounds = 0
        while improved and rounds < 4 and len(head) > 3:
            improved = False
            rounds += 1
            base = tlen(head)
            for seg in (1, 2, 3):
                if improved or seg >= len(head):
                    break
                for i in range(len(head) - seg + 1):
                    block = head[i:i + seg]
                    rest = head[:i] + head[i + seg:]
                    for k in range(len(rest) + 1):
                        cand = rest[:k] + block + rest[k:]
                        if tlen(cand) < base - 1e-9:
                            head = cand
                            improved = True
                            break
                    if improved:
                        break
        order = head + tail
        return [tasks[i] for i in order]"""
assert a in s, "anchor missing"
s = s.replace(a, b, 1)

a2 = '    "rim_max_pts": 9,           # cap on outside samples per search step'
b2 = ('    "rim_max_pts": 9,           # cap on outside samples per search step\n'
      '    "oropt_limit": 12,          # Or-opt only reorders this tour prefix')
assert a2 in s, "anchor 2"
s = s.replace(a2, b2, 1)

io.open(p, "w", encoding="utf-8").write(s)
print("Or-opt bounded to the tour prefix")
