# -*- coding: utf-8 -*-
"""
tidy.py -- 把散落的一次性补丁脚本集中到 archive/。

code/attempts/ 保存算法层面的历史实验；docs/、paper/、report/ 里还散落着
大量只用于修排版、改数字、调图的一次性脚本，它们的效果已经体现在最终文件里，
但留在这里会掩盖真正的交付物。统一移到 archive/ 并保留来源子目录。
"""
import io
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = os.path.join(ROOT, "archive")

# 各目录下需要移走的脚本（保留真正的交付物：.tex/.pdf/.md/.json）
MOVE = {
    "docs": [".py"],
    "paper": [".py"],
    "report": [".py"],
    "": ["prepare_repo.py"],
}


def is_deliverable(fn):
    return fn.lower().endswith((".tex", ".pdf", ".md", ".json", ".png", ".csv"))


if __name__ == "__main__":
    moved = 0
    for sub, exts in MOVE.items():
        src_dir = os.path.join(ROOT, sub) if sub else ROOT
        dst_dir = os.path.join(ARCH, sub) if sub else ARCH
        os.makedirs(dst_dir, exist_ok=True)
        for fn in sorted(os.listdir(src_dir)):
            full = os.path.join(src_dir, fn)
            if not os.path.isfile(full):
                continue
            if not any(fn.endswith(e) for e in exts):
                continue
            if sub == "docs" and fn in ("tech_common.tex",):
                continue
            shutil.move(full, os.path.join(dst_dir, fn))
            moved += 1

    # docs/_build 也一并归档
    b = os.path.join(ROOT, "docs", "_build")
    if os.path.isdir(b):
        for fn in os.listdir(b):
            shutil.move(os.path.join(b, fn), os.path.join(ARCH, "docs", fn))
            moved += 1
        os.rmdir(b)

    # code/organize.py 已完成使命
    for extra in ("code/organize.py",):
        p = os.path.join(ROOT, extra)
        if os.path.exists(p):
            shutil.move(p, os.path.join(ARCH, os.path.basename(extra)))
            moved += 1

    print("archived %d one-off scripts" % moved)
    for d in ("", "code", "code/attempts", "archive", "archive/docs",
              "archive/paper", "archive/report", "data", "docs", "figures",
              "logs", "paper", "report", "tools"):
        full = os.path.join(ROOT, d) if d else ROOT
        if not os.path.isdir(full):
            continue
        n = sum(1 for f in os.listdir(full)
                if os.path.isfile(os.path.join(full, f)))
        print("  %-18s %4d 个文件" % (d or "(根目录)", n))
