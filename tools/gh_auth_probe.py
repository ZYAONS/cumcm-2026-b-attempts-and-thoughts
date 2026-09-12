# -*- coding: utf-8 -*-
"""
gh_auth_probe.py -- 探测已保存的 GitHub 凭据，只输出账号与权限，不打印令牌。

凭据来自 git 的 credential helper（Git Credential Manager），
存放于 Windows 凭据管理器的 git:https://github.com 项。
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request

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
    return user, token, (p.stderr or "")


def api(path, token, method="GET", payload=None):
    url = "https://api.github.com" + path
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "probe")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"raw": body[:200]}
    except Exception as e:
        return 0, {"error": str(e)}


if __name__ == "__main__":
    user, token, err = fill()
    print("credential helper :", "ok" if token else "no credential returned")
    print("account           :", user or "(unknown)")
    print("token length      :", len(token) if token else 0)
    if err.strip():
        print("helper stderr     :", err.strip()[:200])
    if not token:
        sys.exit(1)

    st, body = api("/user", token)
    print("GET /user         :", st,
          body.get("login", body.get("message", "")) if isinstance(body, dict) else "")
    scopes = None
    req = urllib.request.Request("https://api.github.com/user")
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("User-Agent", "probe")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            scopes = r.headers.get("X-OAuth-Scopes")
    except Exception:
        pass
    print("X-OAuth-Scopes    :", scopes)

    st, body = api("/user/repos?per_page=1&sort=updated", token)
    print("GET /user/repos   :", st,
          "(可读取仓库列表)" if st == 200 else body.get("message", "") if isinstance(body, dict) else "")

    st, body = api("/repos/%s/%s" % (user, "个人对建模b题的一些尝试和思考"), token)
    print("目标仓库是否已存在 :", "是" if st == 200 else "否（可创建）" if st == 404 else st)
