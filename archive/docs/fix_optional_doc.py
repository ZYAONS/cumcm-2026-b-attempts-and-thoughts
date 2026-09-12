# -*- coding: utf-8 -*-
"""fix_optional_doc.py -- clean up the remaining LaTeX issues of the report:
the N-table header used a bare '#', and one paragraph still had a markdown style
heading."""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "optional_changes.tex")
s = io.open(p, encoding="utf-8").read()

# the longtable header cell
s = s.replace("\\# & 尝试 & 结果 & 判定 & 依据", "序号 & 尝试 & 结果 & 判定 & 依据")
# any leftover markdown heading
s = re.sub(r"(?m)^#{1,6}\s*", "", s)
# a stray "###" that became "\#\#\#"
s = s.replace("\\#\\#\\# ", "")
# normalise the escaped hashes used as plain text
s = s.replace("\\# ", "# ")
# make sure the "no line here to end" came from a blank line after \end{keybox}
s = s.replace("\\end{keybox}\n\n\n", "\\end{keybox}\n\n")
io.open(p, "w", encoding="utf-8").write(s)
print("cleaned")
