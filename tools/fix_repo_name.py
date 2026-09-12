# -*- coding: utf-8 -*-
"""fix_repo_name.py -- 把 publish.py 里的仓库名换成 URL 安全的英文名。"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "publish.py")
s = io.open(p, encoding="utf-8").read()
old = 'REPO = "个人对建模b题的一些尝试和思考"'
new = 'REPO = "cumcm-2026-b-attempts-and-thoughts"'
assert old in s, "anchor missing"
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("repo name updated")
