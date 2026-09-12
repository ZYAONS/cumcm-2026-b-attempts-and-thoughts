# -*- coding: utf-8 -*-
"""prepare_repo.py -- 把发布前的辅助脚本归位，并生成 .gitignore。"""
import io
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(ROOT, "tools")
os.makedirs(TOOLS, exist_ok=True)

for name in ("scrub_paths.py", "quote_audit.py"):
    src = os.path.join(ROOT, name)
    if os.path.exists(src):
        shutil.move(src, os.path.join(TOOLS, name))
        print("moved %s -> tools/" % name)

gone = os.path.join(ROOT, "organize.py")
if os.path.exists(gone):
    os.remove(gone)
    print("removed organize.py (one-shot)")

GITIGNORE = """# Python
__pycache__/
*.py[cod]
.ipynb_checkpoints/

# LaTeX 中间产物
*.aux
*.log
*.out
*.toc
*.lof
*.lot
*.fls
*.fdb_latexmk
*.synctex.gz

# 编辑器与系统
.vscode/
.idea/
Thumbs.db
desktop.ini

# 备份目录
备份*/
"""
io.open(os.path.join(ROOT, ".gitignore"), "w", encoding="utf-8").write(GITIGNORE)
print("wrote .gitignore")

# 统计仓库体积与最大文件
big = []
total = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames
                   if d not in {".git", "__pycache__"} and not d.startswith("备份")]
    for fn in filenames:
        full = os.path.join(dirpath, fn)
        sz = os.path.getsize(full)
        total += sz
        big.append((sz, os.path.relpath(full, ROOT)))
big.sort(reverse=True)
print("repo size %.1f MB, %d files" % (total / 1048576.0, len(big)))
print("largest files:")
for sz, path in big[:10]:
    print("   %7.2f MB  %s" % (sz / 1048576.0, path))
