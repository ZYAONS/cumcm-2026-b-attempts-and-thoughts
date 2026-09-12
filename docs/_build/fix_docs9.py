# -*- coding: utf-8 -*-
"""fix_docs9.py -- prevent ugly hyphenation ("re-quest_id") in the field-spec
table by setting the code columns in typewriter type."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "simulator_spec.tex")
s = io.open(p, encoding="utf-8").read()
pairs = [
    ("\\texttt{/enter} & arena\\_id, robot\\_id, request\\_id &",
     "\\texttt{/enter} & \\texttt{arena\\_id},\\newline\\texttt{robot\\_id},\\newline\\texttt{request\\_id} &"),
    ("accepted,\\newline virtual\\_time\\_s,\\newline max\\_virtual\\_\\hspace{0pt}duration\\_s,\\newline max\\_real\\_\\hspace{0pt}duration\\_s &",
     "\\texttt{accepted},\\newline\\texttt{virtual\\_time\\_s},\\newline\\texttt{max\\_virtual\\_\\hspace{0pt}duration\\_s},\\newline\\texttt{max\\_real\\_\\hspace{0pt}duration\\_s} &"),
    ("\\texttt{/measure} & $+$ position\\{x,y\\}, channel &\nmeasure\\_result, svd\\_deg? &",
     "\\texttt{/measure} & \\texttt{position},\\newline\\texttt{channel} &\n\\texttt{measure\\_result},\\newline\\texttt{svd\\_deg} &"),
    ("\\texttt{/clear} & $+$ position\\{x,y\\}, channel &\nclear\\_result &",
     "\\texttt{/clear} & \\texttt{position},\\newline\\texttt{channel} &\n\\texttt{clear\\_result} &"),
    ("\\texttt{/exit} & arena\\_id, robot\\_id, request\\_id &\naccepted, virtual\\_time\\_s, exit\\_reason &",
     "\\texttt{/exit} & \\texttt{arena\\_id},\\newline\\texttt{robot\\_id},\\newline\\texttt{request\\_id} &\n\\texttt{accepted},\\newline\\texttt{virtual\\_time\\_s},\\newline\\texttt{exit\\_reason} &"),
    ("全部 & --- & real\\_timestamp\\_\\hspace{0pt}ms,\\newline virtual\\_time\\_s & 每个成功响应都带 \\\\",
     "全部 & --- & \\texttt{real\\_timestamp\\_\\hspace{0pt}ms},\\newline\\texttt{virtual\\_time\\_s} & 每个成功响应都带 \\\\"),
    ("\\begin{longtable}{p{2.1cm}p{2.8cm}p{3.5cm}p{5.9cm}}",
     "\\begin{longtable}{p{2.1cm}p{2.6cm}p{3.4cm}p{6.2cm}}"),
]
for a, b in pairs:
    if a not in s:
        print("  !! missing:", a[:44].replace("\n", " "))
        continue
    s = s.replace(a, b, 1)
    print("  ok:", a[:44].replace("\n", " "))
io.open(p, "w", encoding="utf-8").write(s)
print("done")
