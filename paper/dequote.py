# -*- coding: utf-8 -*-
"""
dequote.py -- 去掉装饰性引号，保留功能性引号。

功能性引号指的是：协议返回值（near、no_signal）、自定义术语的首次定义
（半平面黑洞、顶点枚举）、以及引文原话。这些在中文科技写作里是规范用法，保留。

装饰性引号指的是：把普通短语括起来强调，例如 容易"丢失信号"、回答"是否已清除全部"。
这类是机器写作的痕迹，去掉后句子更自然。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))

DECORATIVE = [
    "地点固定、重复检测无效",
    "保证第二次能收到信号",
    "继续搜索",
    "前往清除已知目标",
    "是否已清除全部",
    "丢失信号",
    "同 request_id 重试",
    "沿示向度前进导致定位失效",
    "以直径为直径的圆能否覆盖",
    "干扰源必在目标域内",
    "检测点处必在接收半径内",
    "覆盖即认证",
    "搜索即认证",
    "最优交会角",
    "可覆盖",
    "不可覆盖",
    "无界",
    "普查—机会式交会—射线归航—可证终止",
    "以定位区域直径为直径的圆能否覆盖此定位区域",
]


def strip_quotes(text):
    n = 0
    for phrase in DECORATIVE:
        for q in ("\u201c%s\u201d" % phrase,):
            if q in text:
                n += text.count(q)
                text = text.replace(q, phrase)
    return text, n


if __name__ == "__main__":
    total = 0
    for name in ("paper.tex", "paper_print.tex", "paper_p1.tex", "paper_p2.tex",
                 "paper_p3.tex", "paper_p4.tex"):
        full = os.path.join(HERE, name)
        if not os.path.exists(full):
            continue
        s = io.open(full, encoding="utf-8").read()
        s2, n = strip_quotes(s)
        if n:
            io.open(full, "w", encoding="utf-8").write(s2)
        print("%-18s removed %d decorative quote pairs" % (name, n))
        total += n
    print("total", total)
