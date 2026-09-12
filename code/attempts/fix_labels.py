# -*- coding: utf-8 -*-
"""fix_labels.py -- repair the mathtext escapes of a few generated labels."""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "zh_labels.json")
d = json.load(io.open(p, encoding="utf-8-sig"))
d.update({
    "fig_cov1": r"7 个检测位置（中心 1 个 + 正六边形顶点 6 个，$\rho=1280$ m）的 "
               r"$R_{\min}=1000$ m 探测圆覆盖整个目标区域",
    "fig_cov_c": "7 点配置的覆盖半径",
    "fig_cov_r": "目标区域半径 1800 m",
    "fig_cov_opt": r"$\rho=1280$ m 时覆盖半径 1892 m",
    "rho": r"六边形半径 $\rho$ / m",
    "cov_r": "可保证覆盖的圆半径 / m",
    "fig_cov2": r"六边形半径的选取：覆盖半径 $\geq$ 1800 m 即可",
    "fig_dir_src": r"定向干扰源 $q$",
    "fig_dir_u": r"定向方向 $u$",
    "fig_dir_silent": "此处收不到信号（不在覆盖角内）",
    "fig_dir1": r"定向干扰源的 $180^\circ$ 覆盖角",
    "fig_dir2": r"认证判据：$q$ 落在无信号检测点凸包内部 $\Rightarrow$ 任何定向方向都无法隐藏",
    "fig_dir_lemma": r"从曾收到信号的点 $p$ 沿射线逼近源：整条线段都在覆盖角内，信号不丢失",
    "fig_dir3": "射线逼近引理（覆盖角不变式）",
    "fig_err20": "清除半径 20 m",
    "err_m": "清除时刻定位误差 / m",
    "count": "频数",
    "fig_err1": "清除时刻的定位误差分布",
    "sigma_m": r"定位区域不确定度半径 $\sigma$ / m",
    "cdf": "累积频率",
    "fig_err2": "估计不确定度的累积分布",
    "fig_err3": r"不确定度 $\sigma$ 是实际误差的可靠上界",
    "x_east": "x / m",
    "y_north": "y / m",
})
io.open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
print("labels fixed:", len(d))
