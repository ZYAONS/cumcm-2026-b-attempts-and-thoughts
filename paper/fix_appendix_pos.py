# -*- coding: utf-8 -*-
"""fix_appendix_pos.py -- the appendix B block was appended after
\\end{document}, so its figures were never typeset and the \\ref in section 9.5
printed "??".  Move the block before \\end{document}."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p4.tex")
s = io.open(p, encoding="utf-8").read()

marker = "\\end{document}"
i = s.index(marker)
head, tail = s[:i], s[i + len(marker):]
assert tail.strip(), "nothing after \\end{document}"

body = head + tail.rstrip() + "\n\n" + marker + "\n"
io.open(p, "w", encoding="utf-8").write(body)
print("appendix moved before \\end{document}")
