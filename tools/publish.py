# -*- coding: utf-8 -*-
"""
publish.py -- 在 GitHub 上创建公开仓库并推送。

凭据取自 git 的 credential helper（Windows 凭据管理器中的
git:https://github.com 项），不写入任何文件，也不打印令牌。
远端使用普通 HTTPS 地址，由 credential helper 在推送时提供凭据，
因此令牌不会落到 .git/config 里。

用法：
    python tools/publish.py --check        只检查，不改动任何东西
    python tools/publish.py --create       创建公开仓库
    python tools/publish.py --push         推送 main 分支
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "cumcm-2026-b-attempts-and-thoughts"
DESC = ("2026 年高教社杯全国大学生数学建模竞赛 B 题：无线电干扰源的快速自动定位与清除。"
        "含建模推导、算法实现、本地模拟器、验证套件与全部尝试记录。")


def fill():
    p = subprocess.run(["git", "credential", "fill"],
                       input="protocol=https\nhost=github.com\n\n",
                       capture_output=True, text=True, encoding="utf-8")
    user = token = None
    for line in (p.stdout or "").splitlines():
        if line.startswith("username="):
            user = line.split("=", 1)[1].strip()
        elif line.startswith("password="):
            token = line.split("=", 1)[1].strip()
    return user, token


def api(path, token, method="GET", payload=None):
    req = urllib.request.Request("https://api.github.com" + path,
                                 data=json.dumps(payload).encode() if payload else None,
                                 method=method)
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "publish")
    if payload:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode(errors="ignore") or "{}")
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"error": str(e)}


def run(args, **kw):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", **kw)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    user, token = fill()
    if not token:
        print("未取得凭据，终止")
        sys.exit(1)
    print("账号:", user)

    enc = urllib.parse.quote(REPO)
    st, body = api("/repos/%s/%s" % (user, enc), token)
    exists = (st == 200)
    print("仓库存在:", exists)

    if mode == "--check":
        print("检查模式，未做改动")
        sys.exit(0)

    if mode == "--create":
        if exists:
            print("仓库已存在，跳过创建")
        else:
            st, body = api("/user/repos", token, "POST", {
                "name": REPO, "description": DESC, "private": False,
                "has_issues": True, "has_wiki": False, "auto_init": False})
            if st in (200, 201):
                print("已创建公开仓库:", body.get("html_url"))
            else:
                print("创建失败:", st, body.get("message", ""))
                sys.exit(1)
        sys.exit(0)

    if mode == "--push":
        url = "https://github.com/%s/%s.git" % (user, urllib.parse.quote(REPO))
        r = run(["git", "remote", "remove", "origin"])
        r = run(["git", "remote", "add", "origin", url])
        if r.returncode:
            print("设置远端失败:", r.stderr[:300])
            sys.exit(1)
        print("远端:", url)
        r = run(["git", "push", "-u", "origin", "main"])
        print("推送返回码:", r.returncode)
        tail = (r.stderr or "")[-1500:]
        for line in tail.splitlines():
            if "github_pat_" in line or "ghp_" in line:
                line = "<redacted>"
            print("   ", line)
        sys.exit(0 if r.returncode == 0 else 1)
