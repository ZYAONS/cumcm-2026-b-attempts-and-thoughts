# -*- coding: utf-8 -*-
"""
scrub_paths.py -- 发布前清洗文本文件。

做两件事：
  1. 把本机绝对路径（C:\\Users\\<用户名>\\... 与 TeX 发行版路径）替换为空；
  2. 把 UTF-16 编码的文本统一转成 UTF-8。

第二件事是必要的：Windows PowerShell 的 ">" 重定向默认写 UTF-16LE，
日志里字符之间夹着 \\x00，用 UTF-8 读取时正则匹配不到任何东西，
上一版清洗脚本因此漏掉了 8 个日志文件。
"""
import io
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.basename(ROOT)
PATTERNS = [
    (re.compile(r"[A-Za-z]:\\Users\\[^\\\s\"']+\\Desktop\\[^\\\s\"']+\\"
                + re.escape(PROJ) + r"\\"), ""),
    (re.compile(r"[A-Za-z]:\\Users\\[^\\\s\"']+\\Desktop\\[^\\\s\"']+\\"), ""),
    (re.compile(r"[A-Za-z]:\\Users\\[^\\\s\"']+\\"), ""),
    (re.compile(r"[A-Za-z]:\\Users\\[^\\\s\"']+"), ""),
    (re.compile(r"[A-Za-z]:/Users/[^/\s\"']+/Desktop/[^/\s\"']+/"
                + re.escape(PROJ) + r"/"), ""),
    (re.compile(r"[A-Za-z]:/Users/[^/\s\"']+/"), ""),
    (re.compile(r"[A-Za-z]:\\tl\d{4}\\bin\\[^\\\s\"']+\\"), ""),
    (re.compile(r"[A-Za-z]:\\tl\d{4}\\[^\\\s\"']*\\"), ""),
]
EXTS = (".md", ".tex", ".py", ".json", ".txt", ".csv", ".log", ".jsonl")
SKIP_DIRS = {".git", "__pycache__", "备份"}


def read_text(full):
    """按 BOM 判断编码；没有 BOM 时用空字节比例判断 UTF-16。"""
    raw = open(full, "rb").read()
    if raw.startswith(b"\xff\xfe"):
        return raw.decode("utf-16-le").lstrip("\ufeff"), "utf16"
    if raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16-be").lstrip("\ufeff"), "utf16"
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig"), "utf8"
    if raw and raw.count(b"\x00") > len(raw) // 4:
        try:
            return raw.decode("utf-16-le").lstrip("\ufeff"), "utf16"
        except Exception:
            pass
    return raw.decode("utf-8", errors="ignore"), "utf8"


if __name__ == "__main__":
    n_files = n_hits = n_conv = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.lower().endswith(EXTS):
                continue
            full = os.path.join(dirpath, fn)
            try:
                s, enc = read_text(full)
            except Exception:
                continue
            orig, hits = s, 0
            for pat, rep in PATTERNS:
                s, k = pat.subn(rep, s)
                hits += k
            if s != orig or enc == "utf16":
                io.open(full, "w", encoding="utf-8", newline="").write(s)
                n_files += 1
                n_hits += hits
                if enc == "utf16":
                    n_conv += 1
    print("scrubbed %d path occurrences; rewrote %d files; "
          "converted %d from UTF-16 to UTF-8" % (n_hits, n_files, n_conv))

    left = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.lower().endswith(EXTS):
                continue
            full = os.path.join(dirpath, fn)
            t, _ = read_text(full)
            if ("Users\\" in t or "Users/" in t
                    or re.search(r"[A-Za-z]:\\tl\d{4}", t)):
                left.append(os.path.relpath(full, ROOT))
    print("files still containing a local path: %d" % len(left))
    for x in left:
        print("   ", x)
