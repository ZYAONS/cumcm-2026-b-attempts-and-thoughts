# -*- coding: utf-8 -*-
"""quote_audit.py -- 统计各文档里中文引号与 AI 味词汇的密度。"""
import io
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
AI_WORDS = ["值得注意", "一句话", "总而言之", "需要强调的是", "至关重要",
            "不仅", "而且", "赋能", "深度", "全方位", "助力", "打造",
            "本质", "核心洞察", "关键洞察", "让我们"]
QUOTE = re.compile(r"[“”]")

if __name__ == "__main__":
    rows = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in {".git", "__pycache__", "备份", "figures", "data"}]
        for fn in filenames:
            if not fn.lower().endswith((".md", ".tex")):
                continue
            full = os.path.join(dirpath, fn)
            t = io.open(full, encoding="utf-8", errors="ignore").read()
            n = len(QUOTE.findall(t))
            words = sum(t.count(w) for w in AI_WORDS)
            rows.append((n, words, len(t), os.path.relpath(full, ROOT)))
    rows.sort(reverse=True)
    print("%6s %6s %8s  %s" % ("引号", "AI词", "字数", "文件"))
    for n, w, L, path in rows:
        if n or w:
            print("%6d %6d %8d  %s" % (n, w, L, path))
