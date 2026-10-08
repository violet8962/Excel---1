# -*- coding: utf-8 -*-
"""
excel_viz —— 《Excel数据可视化：从图表到数据大屏》的 Python 实现
================================================================

把原书基于 Excel 的图表技法，逐一改写成 Python（pandas + matplotlib）实现。

章节结构
--------
``ch2_part1``  第二章前 15 例：渐变柱形图 → 水球图
``ch2_part2``  第二章后 15 例：波浪水球图 → 对比滑珠图
``ch3_dynamic`` 第三章：动态图表（控件驱动的图表）
``ch4_dashboard`` 第四章：人力资源看板 / 销售数据大屏

快速开始
--------
::

    python -m excel_viz.run_all          # 一次生成全部图表
    python -m excel_viz.ch2_part1        # 只跑第二章前 15 例

输出目录默认为项目下的 ``output/``。
"""

__version__ = "1.0.0"

__all__ = [
    "theme",
    "data",
    "utils",
    "ch2_part1",
    "ch2_part2",
    "ch3_dynamic",
    "ch4_dashboard",
]
