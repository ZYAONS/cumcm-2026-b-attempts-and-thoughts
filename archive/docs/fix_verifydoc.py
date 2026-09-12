# -*- coding: utf-8 -*-
"""fix_verifydoc.py -- break the long repository names in the survey table
(zero-width break points after '/' and '-', the same trick the paper uses)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "simulator_verification.tex")
s = io.open(p, encoding="utf-8").read()

pairs = [
    ("\\texttt{JammersSimulator-Tool}\\newline \\scriptsize(github.com/Jammers-Simulator-Lab)",
     "\\texttt{JammersSimulator\\hspace{0pt}-\\hspace{0pt}Tool}\\newline\n"
     "\\scriptsize \\texttt{github.com/\\hspace{0pt}Jammers\\hspace{0pt}-\\hspace{0pt}Simulator\\hspace{0pt}-\\hspace{0pt}Lab}"),
    ("\\texttt{tiiuae/gnn-jamming-source-localization}\\newline \\scriptsize(阿联酋 TII)",
     "\\texttt{tiiuae/\\hspace{0pt}gnn\\hspace{0pt}-\\hspace{0pt}jamming\\hspace{0pt}-\\hspace{0pt}source\\hspace{0pt}-\\hspace{0pt}localization}\\newline\n"
     "\\scriptsize 阿联酋 TII"),
    ("\\texttt{El-Mohr/WSN-Loclaization-Simulator} & Python &",
     "\\texttt{El\\hspace{0pt}-\\hspace{0pt}Mohr/\\hspace{0pt}WSN\\hspace{0pt}-\\hspace{0pt}Loclaization\\hspace{0pt}-\\hspace{0pt}Simulator} & Python &"),
    ("\\texttt{daniyalshagiroff/acoustic-triangulation} & Python &",
     "\\texttt{daniyalshagiroff/\\hspace{0pt}acoustic\\hspace{0pt}-\\hspace{0pt}triangulation} & Python &"),
    ("\\texttt{dstl/Stone-Soup}\\newline \\scriptsize(UK 国防科技实验室)",
     "\\texttt{dstl/\\hspace{0pt}Stone\\hspace{0pt}-\\hspace{0pt}Soup}\\newline \\scriptsize UK 国防科技实验室"),
    ("\\texttt{dressel/FEBOL.jl} & Julia 研究代码 &",
     "\\texttt{dressel/\\hspace{0pt}FEBOL.jl} & Julia 研究代码 &"),
    ("\\begin{longtable}{p{4.0cm}p{2.4cm}p{8.4cm}}",
     "\\begin{longtable}{p{3.9cm}p{1.9cm}p{9.0cm}}"),
]
for a, b in pairs:
    if a not in s:
        print("  !! missing:", a[:44].replace("\n", " "))
        continue
    s = s.replace(a, b, 1)
    print("  ok:", a[:44].replace("\n", " "))
io.open(p, "w", encoding="utf-8").write(s)
print("done")
