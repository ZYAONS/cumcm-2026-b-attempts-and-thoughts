# -*- coding: utf-8 -*-
"""
rename_repo.py -- 把仓库改名为 URL 安全的形式。

GitHub 不支持非 ASCII 仓库名：申请创建 "个人对建模b题的一些尝试和思考" 时，
非 ASCII 字符被剥掉，实际得到的是 "-b-"。
改为等义的英文名，并把中文名放进仓库描述与 README 标题（两处都支持中文）。
"""
import sys
import urllib.parse

sys.path.insert(0, __file__.rsplit("\\", 1)[0])
from publish import api, fill  # noqa: E402

OLD = "-b-"
NEW = "cumcm-2026-b-attempts-and-thoughts"
DESC = ("个人对建模 B 题的一些尝试和思考。2026 年高教社杯全国大学生数学建模竞赛 B 题："
        "无线电干扰源的快速自动定位与清除，含建模推导、算法实现、本地模拟器、"
        "验证套件与全部尝试记录。")

if __name__ == "__main__":
    user, token = fill()
    st, body = api("/repos/%s/%s" % (user, urllib.parse.quote(OLD)), token,
                   "PATCH", {"name": NEW, "description": DESC, "private": False})
    if st == 200:
        print("改名成功:", body.get("full_name"))
        print("地址    :", body.get("html_url"))
        print("描述    :", body.get("description"))
        print("公开    :", not body.get("private"))
    else:
        print("改名失败:", st, body.get("message", ""))
