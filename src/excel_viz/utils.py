# -*- coding: utf-8 -*-
"""
绘图辅助算法
============

* ``catmull_rom``  —— Catmull-Rom 样条插值，实现 Excel「平滑线」效果
                      （不依赖 scipy，纯 numpy 即可）
"""
from __future__ import annotations

import numpy as np


def catmull_rom(points, samples_per_segment: int = 40, tension: float = 0.5):
    """
    对折线做 Catmull-Rom 平滑，返回插值后的 (x, y)。

    原书「平滑折线图」用的是 Excel 的「平滑线」选项，
    底层就是一种经过所有原始数据点的插值样条，这里用 Catmull-Rom 复现：
    曲线一定穿过每个数据点，且不会像多项式拟合那样产生过冲抖动。

    Parameters
    ----------
    points : (N, 2) 原始点坐标
    samples_per_segment : 每段插值的采样点数
    tension : 张力，0.5 为 Catmull-Rom 标准值
    """
    pts = np.asarray(points, dtype=float)
    if len(pts) < 3:
        return pts[:, 0], pts[:, 1]

    xs, ys = [], []
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else pts[i + 1]
        for t in np.linspace(0, 1, samples_per_segment, endpoint=(i == n - 2)):
            t2, t3 = t * t, t * t * t
            x = (tension * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                            + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                            + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
                 + (1 - tension) * (p1[0] * (1 - t) + p2[0] * t))
            y = (tension * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                            + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                            + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
                 + (1 - tension) * (p1[1] * (1 - t) + p2[1] * t))
            xs.append(x)
            ys.append(y)
    return np.asarray(xs), np.asarray(ys)


def drop_lines(ax, x, y, bottom=0, color="#C8C8C8", lw=0.9, ls=(0, (3, 3)),
               zorder=1):
    """
    从数据点向横轴画垂直虚线，对应 Excel 图表元素里的「线条 / 垂直线」。

    原书第三章「菱形走势图」正是靠这组垂直线撑起版面。
    """
    for xi, yi in zip(x, y):
        ax.plot([xi, xi], [bottom, yi], color=color, linewidth=lw,
                linestyle=ls, zorder=zorder)


def nice_ylim(values, headroom: float = 0.18, bottom: float = 0.0):
    """按数据范围留出顶部空间，避免数据标签被裁掉。"""
    vmax = float(np.nanmax(values))
    return bottom, vmax * (1 + headroom)
