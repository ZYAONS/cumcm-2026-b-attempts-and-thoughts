# -*- coding: utf-8 -*-
"""redraw_framework.py -- replace the cramped TikZ flow chart of section 2.1 by a
clear, evenly spaced diagram (no arrow label overlaps the boxes)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "paper_p1.tex")
s = io.open(p, encoding="utf-8").read()

start = s.index("\\begin{center}\n\\begin{tikzpicture}")
end = s.index("\\captionof{figure}{四个问题的逻辑关系")
new = r"""\begin{center}
\begin{tikzpicture}[
  font=\small,
  box/.style={draw, rounded corners=3pt, align=center, inner sep=6pt,
              minimum height=1.55cm, minimum width=3.05cm, fill=blue!6,
              line width=0.7pt},
  core/.style={draw, rounded corners=3pt, align=center, inner sep=6pt,
               fill=orange!14, line width=0.7pt},
  lbl/.style={font=\scriptsize, text=black!70, inner sep=1.5pt},
  ar/.style={-{Stealth[length=2.2mm]}, line width=0.8pt},
  dar/.style={-{Stealth[length=2.2mm]}, line width=0.8pt, dashed}
]
% --- four problem boxes -------------------------------------------------
\node[box] (q1) {\textbf{问题一}\\[1pt] 定位区域 $\mathcal{R}$\\[1pt] 直径 $D$、圆覆盖判据};
\node[box, right=1.55cm of q1] (q2) {\textbf{问题二}\\[1pt] 第二检测点\\[1pt] minimax 站位优化};
\node[box, right=1.55cm of q2] (q3) {\textbf{问题三}\\[1pt] 全向源在线\\[1pt] 搜索—定位—清除};
\node[box, right=1.55cm of q3] (q4) {\textbf{问题四}\\[1pt] 含定向源\\[1pt] 检测与认证策略};

% --- chain arrows with labels placed ABOVE the arrows -------------------
\draw[ar] (q1) -- node[lbl, above=2pt] {不确定度度量} (q2);
\draw[ar] (q2) -- node[lbl, above=2pt] {站位规则} (q3);
\draw[ar] (q3) -- node[lbl, above=2pt] {覆盖 $\Rightarrow$ 认证} (q4);

% --- shared kernel ------------------------------------------------------
\node[core, below=1.35cm of q2, xshift=1.55cm, minimum width=11.4cm] (core)
     {\textbf{统一内核}：角度楔交会 $\Rightarrow$ 定位区域（凸多边形）$\Rightarrow$ 最小包围圆作位置不确定度 $\sigma$};

% --- kernel feeds every problem ----------------------------------------
\draw[dar] (core.north -| q1.south) -- node[lbl, right=1.5pt] {} (q1.south);
\draw[dar] (core.north -| q3.south) -- (q3.south);
\draw[dar] (core.north -| q4.south) -- (q4.south);
\draw[dar] ([yshift=3pt]core.north) -- ([yshift=-3pt]q2.south);

% --- uncertainty propagates from problem 1 to problems 3/4 -------------
\draw[ar, rounded corners=4pt] (q1.south) ++(0,-0.28) -- ++(0,-0.42)
      -- node[lbl, pos=0.5, below=1pt] {位置估计} ([xshift=-1.0cm]q3.south);
\end{tikzpicture}
\captionof{figure}{四个问题的逻辑关系：问题一给出几何内核与不确定度度量，问题二给出站位规则，
问题三、四是在线决策问题；统一内核（下方橙色框）为四个问题共用}
\label{fig:frame}
\end{center}"""
s = s[:start] + new + s[end + len("\\captionof{figure}{四个问题的逻辑关系：问题一提供几何内核，问题二提供站位规则，问题三、四是在线决策问题}\n\\label{fig:frame}\n\\end{center}"):]
io.open(p, "w", encoding="utf-8").write(s)
print("framework diagram redrawn")
