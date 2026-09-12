# -*- coding: utf-8 -*-
"""fix_docs4.py -- break the long unbreakable \\texttt{} tokens that overflow.

Strategy (same as the paper): insert zero-width break points (\\hspace{0pt}) at
sensible places inside long code tokens, and give the offending table columns a
fixed width so they can wrap.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def edit(fname, pairs):
    p = os.path.join(HERE, fname)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s:
            print("  !! missing in %s: %s" % (fname, a[:50].replace("\n", " ")))
            continue
        s = s.replace(a, b, 1)
        print("  ok %s" % a[:50].replace("\n", " "))
    io.open(p, "w", encoding="utf-8").write(s)


edit("code_walkthrough.tex", [
    # (1) 返回值列表：改成项之间可断的短片段
    ("\\texttt{region\\_from\\_bearings} & \\textbf{总入口}：返回 \\texttt{vertices/empty/bounded/diameter/d\\_pair/cover\\_ok/cover\\_slack/mec}\n（空集与无界情形提前返回，不继续算直径） \\\\",
     "\\texttt{region\\_from\\_bearings} & \\textbf{总入口}，返回一个字典：\\texttt{vertices}、\\texttt{empty}、\n"
     "\\texttt{bounded}、\\texttt{diameter}、\\texttt{d\\_pair}、\\texttt{cover\\_ok}、\n"
     "\\texttt{cover\\_slack}、\\texttt{mec}（空集与无界情形提前返回，不继续算直径） \\\\"),
    # (2) 参数分组表：第二列改为定宽
    ("\\begin{tabular}{llp{7.4cm}}", "\\begin{tabular}{p{1.85cm}p{4.55cm}p{6.9cm}}"),
    # (3) 状态字段段落：拆分并加断点
    ("状态字段包括：\\texttt{pos, cur\\_channel, vtime}（位置/频道/虚拟时刻）、\n"
     "\\texttt{status[c]}（\\texttt{unknown/seen/located/cleared/empty}）、\n"
     "\\texttt{obs[c], nosig[c], est[c], last\\_seen[c], meas\\_cache}、\n"
     "\\texttt{\\_task\\_count/\\_task\\_travel/\\_task\\_time}（**任务级统计，调试故障 4 的关键基础设施**）。",
     "状态字段包括：位置与时钟 \\texttt{pos}、\\texttt{cur\\_channel}、\\texttt{vtime}；\n"
     "频道状态 \\texttt{status[c]}（取值 \\texttt{unknown}、\\texttt{seen}、\\texttt{located}、\n"
     "\\texttt{cleared}、\\texttt{empty}）；信息集合 \\texttt{obs[c]}、\\texttt{nosig[c]}、\n"
     "\\texttt{est[c]}、\\texttt{last\\_seen[c]}、\\texttt{meas\\_cache}；以及\n"
     "\\texttt{\\_task\\_count}、\\texttt{\\_task\\_travel}、\\texttt{\\_task\\_time}\n"
     "（\\textbf{任务级统计，是发现故障 4 那类死循环的关键基础设施}）。"),
    # (4) 长函数名加零宽断点
    ("\\texttt{\\_circular\\_arc\\_intersection} &", "\\texttt{\\_circular\\_\\hspace{0pt}arc\\_intersection} &"),
    ("\\texttt{rotating\\_calipers\\_diameter} &", "\\texttt{rotating\\_\\hspace{0pt}calipers\\_diameter} &"),
])

edit("simulator_spec.tex", [
    ("\\begin{longtable}{p{2.6cm}p{2.4cm}p{3.4cm}p{6.4cm}}",
     "\\begin{longtable}{p{2.3cm}p{3.1cm}p{3.9cm}p{6.1cm}}"),
    ("accepted, virtual\\_time\\_s, max\\_virtual\\_duration\\_s, max\\_real\\_duration\\_s &",
     "accepted, virtual\\_time\\_s,\\newline max\\_virtual\\_duration\\_s,\\newline max\\_real\\_duration\\_s &"),
    ("measure\\_result, svd\\_deg? &", "measure\\_result, svd\\_deg? &"),
    ("日志目录约定：\\texttt{logs/formal/formal\\_seed<种子>.log}（正式测试）、\n\\texttt{logs/drill/drill\\_seed<种子>.log}（演练）。",
     "日志目录约定：正式测试写入 \\texttt{logs/formal/}，文件名为\n"
     "\\texttt{formal\\_\\hspace{0pt}seed<种子>.log}；演练写入 \\texttt{logs/drill/}，\n"
     "文件名为 \\texttt{drill\\_\\hspace{0pt}seed<种子>.log}。"),
    ("内存模式 & \\texttt{LocalClient(Arena(...))} & 大规模调参、60 组演练。\n无 HTTP 开销，单局 0.3$\\sim$0.6 s \\\\",
     "内存模式 & \\texttt{LocalClient}\\newline\\texttt{(Arena(...))} & 大规模调参、60 组演练。\n无 HTTP 开销，单局 0.3$\\sim$0.6 s \\\\"),
    ("后台线程 & \\texttt{run\\_server\\_thread(port, ...)} & 自动化脚本（\\texttt{run\\_http\\_tests.py}）：\n在同进程内起服务线程，主线程用 \\texttt{HTTPClient} 走真实 HTTP \\\\",
     "后台线程 & \\texttt{run\\_server\\_\\hspace{0pt}thread}\\newline\\texttt{(port, ...)} & 自动化脚本（\\texttt{run\\_http\\_tests.py}）：\n在同进程内起服务线程，主线程用 \\texttt{HTTPClient} 走真实 HTTP \\\\"),
])
print("done")
