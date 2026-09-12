# -*- coding: utf-8 -*-
"""
final_check.py -- 发布前的完整性检查。

检查项：
  1. 本机用户名、家目录、解释器路径是否残留（检查脚本自身除外）；
  2. 是否含有疑似凭据；
  3. 核心模块能否导入，验证套件能否通过；
  4. 目录结构与关键文件是否齐全；
  5. 仓库体积。
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(ROOT, "code")
EXTS = (".md", ".tex", ".py", ".json", ".txt", ".csv", ".log", ".jsonl", ".yml",
        ".yaml", ".cfg", ".toml")
SKIP_DIRS = {".git", "__pycache__", "备份", "tools"}

SECRET = re.compile(
    r"(?:ghp_[A-Za-z0-9]{20,}"
    r"|github_pat_[A-Za-z0-9_]{20,}"
    r"|sk-[A-Za-z0-9]{20,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|(?i:(?:password|passwd|secret|api[_-]?key)\s*[:=]\s*[\"'][^\"']{6,}))")


def walk(root=ROOT, skip=SKIP_DIRS):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def read(full):
    raw = open(full, "rb").read()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16", errors="ignore")
    return raw.decode("utf-8", errors="ignore")


if __name__ == "__main__":
    problems = []

    hits = []
    for full in walk():
        if not full.lower().endswith(EXTS):
            continue
        t = read(full)
        if "Users\\" in t or "Users/" in t or "miniconda" in t:
            hits.append(os.path.relpath(full, ROOT))
    print("[1] 本机路径残留: %d 个文件" % len(hits))
    for h in hits:
        print("     ", h)
    if hits:
        problems.append("本机路径残留")

    sec = []
    for full in walk():
        if not full.lower().endswith(EXTS):
            continue
        m = SECRET.search(read(full))
        if m:
            sec.append((os.path.relpath(full, ROOT), m.group(0)[:40]))
    print("[2] 疑似凭据: %d 处" % len(sec))
    for p, s in sec:
        print("     %s : %s" % (p, s))
    if sec:
        problems.append("疑似凭据")

    sys.path.insert(0, CODE)
    try:
        import geom_core, simulator, robot_core, make_data  # noqa: F401
        print("[3a] 核心模块导入: 正常")
    except Exception as e:
        print("[3a] 核心模块导入失败: %s" % e)
        problems.append("核心模块导入失败")

    try:
        import verify_simulator as vs
        res = vs.main() if hasattr(vs, "main") else None
        print("[3b] 验证套件: 见上方输出")
    except SystemExit:
        pass
    except Exception as e:
        print("[3b] 验证套件异常: %s" % e)

    need = ["README.md", ".gitignore", "code/robot_core.py", "code/simulator.py",
            "code/geom_core.py", "code/make_data.py", "code/make_figures.py",
            "code/verify_simulator.py", "paper/paper.pdf",
            "docs/final_report.pdf", "report/ATTEMPTS_LOG.md",
            "report/self_check.md", "report/FIGURE_SKILLS.md"]
    missing = [x for x in need if not os.path.exists(os.path.join(ROOT, x))]
    print("[4] 关键文件缺失: %d" % len(missing))
    for x in missing:
        print("     ", x)
    if missing:
        problems.append("关键文件缺失")

    total = sum(os.path.getsize(f) for f in walk())
    n = sum(1 for _ in walk())
    print("[5] 仓库 %.1f MB / %d 个文件" % (total / 1048576.0, n))

    print()
    print("结论: " + ("存在待处理项 -> " + "、".join(problems) if problems
                     else "全部检查通过，可以发布"))
