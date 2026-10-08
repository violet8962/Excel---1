# -*- coding: utf-8 -*-
"""
一键运行全部实验
================

    python scripts/run_all.py            # 全部
    python scripts/run_all.py --only ch2 # 只跑某一章（ch2 / ch3 / ch4）
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["ch2", "ch3", "ch4"], default=None,
                    help="只运行指定章节")
    args = ap.parse_args()

    from excel_viz import ch2_part1, ch2_part2, ch3_dynamic, ch4_dashboard

    groups = {
        "ch2": ("第二章 · 30 例基础图表", ch2_part1.CHARTS + ch2_part2.CHARTS),
        "ch3": ("第三章 · 动态图表", ch3_dynamic.CHARTS),
        "ch4": ("第四章 · 看板与大屏", ch4_dashboard.CHARTS),
    }

    outputs = []
    for key in ["ch2", "ch3", "ch4"]:
        if args.only and key != args.only:
            continue
        title, fns = groups[key]
        print(f"\n===== {title}（{len(fns)} 个） =====")
        for i, fn in enumerate(fns, 1):
            t0 = time.perf_counter()
            out = fn()
            outputs.append(out)
            print(f"  [{i:2d}/{len(fns)}] {Path(out).name}  "
                  f"({time.perf_counter() - t0:.1f}s)")

    print(f"\n全部完成，共生成 {len(outputs)} 个文件，输出目录：")
    print(" ", ROOT / "output")
    return 0


if __name__ == "__main__":
    sys.exit(main())
