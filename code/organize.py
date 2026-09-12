# -*- coding: utf-8 -*-
"""
organize.py -- 整理项目目录。

分类原则：
  code/            最终可运行的流水线（核心模块 + 工具），保持平铺以保证 import 正常
  code/attempts/   历史尝试与补丁脚本（记录用；运行时加 PYTHONPATH=.. 即可）
其余目录（data/docs/figures/logs/paper/report）保持原有职责。
"""
import io
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# 最终流水线：核心模块 + 报告所用工具（全部平铺，互相 import 正常）
KEEP = {
    # 核心模型
    "geom_core.py", "simulator.py", "robot_core.py",
    "q2_solver.py", "q2_strategy.py",
    # 数据与图
    "make_data.py", "make_figures.py", "zh_labels.json",
    # 验证与测试
    "verify_simulator.py", "run_http_tests.py", "final_validate.py",
    # 分析工具（最终报告中的所有数字都由这些脚本产出）
    "multi_pool.py", "miss_rate.py", "find_missed.py", "time_budget.py",
    "leg_audit.py", "floor.py", "route_check.py", "tour_bound.py", "cert_gap.py",
    # 参数寻优与数据再生成
    "regen_stage.py", "finish_q34_data.py", "optimize_q34.py",
    "tune.py", "tune_q4.py",
    # 问题一的小工具
    "q1_scan.py", "q1_smoke.py", "q1_counterexample.py",
}

if __name__ == "__main__":
    att = os.path.join(HERE, "attempts")
    os.makedirs(att, exist_ok=True)
    moved = 0
    for name in sorted(os.listdir(HERE)):
        full = os.path.join(HERE, name)
        if not os.path.isfile(full):
            continue
        if name in KEEP or name == "organize.py":
            continue
        if name.endswith(".py") or name.endswith(".jsonl"):
            shutil.move(full, os.path.join(att, name))
            moved += 1
    print("moved %d files into code/attempts/" % moved)
    print("kept in code/:")
    for n in sorted(os.listdir(HERE)):
        if os.path.isfile(os.path.join(HERE, n)):
            print("   ", n)
