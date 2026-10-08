# -*- coding: utf-8 -*-
"""
第三章 · 动态图表
================

原书第三章在 Excel 里靠「表单控件（组合框 / 滚动条 / 复选框）+
INDEX / VLOOKUP / OFFSET 联动」让图表动起来，甚至用 VBA 驱动。

Python 里对应的做法是：把「控件当前值」变成循环变量，逐帧重绘，
再合成 GIF 动画。每张图同时输出：

* ``output/ch3/xx_名称.gif`` —— 动画成品
* ``output/ch3/frames/xx_f{i}.png`` —— 各关键帧单图（相当于控件每个档位）

「切片器」一例则直接用 pandas 透视表复现 Excel 数据透视表 + 切片器联动。
"""
from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge
from PIL import Image

from . import data as D
from .theme import (
    EXCEL_PALETTE, INK, OUTPUT_DIR, SUB_INK, new_axes, pct, rounded_bar, save,
    style_axes, title_block, value_labels,
)
from .utils import drop_lines

OUT = "ch3"


# --------------------------------------------------------------------------- 动画工具
def figures_to_gif(figures, path: Path, duration_ms: int = 1000) -> Path:
    """把一组 Figure 合成 GIF，帧图另存到同目录 frames/ 下。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frames_dir = path.parent / "frames" / path.stem
    frames_dir.mkdir(parents=True, exist_ok=True)

    imgs = []
    for i, fig in enumerate(figures):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=110, facecolor=fig.get_facecolor())
        buf.seek(0)
        imgs.append(Image.open(buf).convert("RGB"))
        # 同步保存单帧 PNG，相当于控件每个档位的静态截图
        fig.savefig(frames_dir / f"{path.stem}_f{i:02d}.png", dpi=110,
                    facecolor=fig.get_facecolor())
        plt.close(fig)

    imgs[0].save(path, save_all=True, append_images=imgs[1:],
                 duration=duration_ms, loop=0)
    return path


# --------------------------------------------------------------------------- 01
def chart_01_dynamic_bar():
    """
    1 动态柱形图：组合框选择月份 → 图表只显示该月 6 个区域的销量。

    Excel：组合框链到 J3，B13=INDEX(...)，C13=VLOOKUP(...)。
    Python：直接按行索引取数，循环 6 个月出 6 帧。
    """
    df = D.ch3("01_dynamic_bar")
    months = df["月份"].tolist()

    figures = []
    for k, month in enumerate(months):
        fig, ax = new_axes()
        vals = df.iloc[k, 1:].astype(float).tolist()
        regions = df.columns[1:].tolist()
        bars = ax.bar(regions, vals, width=0.55, color=EXCEL_PALETTE[0])
        bars[int(np.argmax(vals))].set_color(EXCEL_PALETTE[1])
        style_axes(ax)
        ax.set_ylim(0, 1100)
        value_labels(ax, bars)
        title_block(fig, ax, f"{month} 各区域销售量",
                    "数据随组合框选择联动，等价于 Excel 的 INDEX + VLOOKUP 方案",
                    f"数据来源：第三章 动态图表.xlsm / 1 动态柱形图（第 {k + 1}/{len(months)} 档）")
        figures.append(fig)

    return figures_to_gif(figures, OUTPUT_DIR / OUT / "01_动态柱形图.gif",
                          duration_ms=900)


# --------------------------------------------------------------------------- 02
def chart_02_dynamic_racetrack():
    """2 动态跑道图：滚动条切换月份，各部门人数在跑道上重新排位。"""
    df = D.ch3("02_dynamic_racetrack")
    months = df.columns[1:].tolist()
    notes = D.racetrack_note()

    figures = []
    for k, month in enumerate(months):
        sub = df.sort_values(month, ascending=False).reset_index(drop=True)
        labels = sub["部门"].tolist()
        heads = sub[month].astype(float).tolist()
        # 跑道全长略大于最大值，留出冲刺区
        L = float(max(heads) + 380)

        fig, ax = new_axes(figsize=(7.2, 6.0), rect=(0.04, 0.08, 0.92, 0.72))
        ax.set_aspect("equal")
        ax.axis("off")
        rmax, rmin = 1.0, 0.34
        n = len(labels)
        for i in range(n):
            r = rmax - i * (rmax - rmin) / max(n - 1, 1)
            ax.add_patch(Wedge((0, 0), r, 180, 0, width=(rmax - rmin) / n * 0.6,
                               facecolor="#EFEFEF", edgecolor="white", linewidth=1))
            sweep = -heads[i] / L * 180
            ax.add_patch(Wedge((0, 0), r, 180, 180 + sweep,
                               width=(rmax - rmin) / n * 0.6,
                               facecolor=EXCEL_PALETTE[i % len(EXCEL_PALETTE)],
                               edgecolor="white", linewidth=1))
            ang = np.deg2rad(225)
            ax.text(1.24 * r * np.cos(ang), 1.24 * r * np.sin(ang),
                    f"{labels[i]}  {heads[i]:.0f}", ha="center", va="center",
                    fontsize=10, color=EXCEL_PALETTE[i % len(EXCEL_PALETTE)],
                    fontweight="bold")
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.2, 1.25)
        note = notes.get("说明", "") if isinstance(notes, dict) else ""
        title_block(fig, ax, f"{month} 各部门人数跑道",
                    str(note) if note else "滚动条切换月份，各部门随人数变化重新排位",
                    f"数据来源：第三章 动态图表.xlsm / 2 动态跑道图（{k + 1}/{len(months)}）")
        figures.append(fig)

    return figures_to_gif(figures, OUTPUT_DIR / OUT / "02_动态跑道图.gif",
                          duration_ms=1100)


# --------------------------------------------------------------------------- 03
def chart_03_dynamic_rose():
    """3 动态南丁格尔圆环图：组合框切换「近7天 / 近30天」两个周期。"""
    df = D.ch3("03_dynamic_rose")
    periods = df["周期"].tolist()

    figures = []
    for k, period in enumerate(periods):
        vals = df.iloc[k, 1:].astype(float).tolist()
        labels = df.columns[1:].tolist()
        fig, ax = new_axes(figsize=(7, 5.8), rect=(0.05, 0.08, 0.9, 0.72))
        ax.set_aspect("equal")
        ax.axis("off")
        total = sum(vals)
        gap = 6.0
        usable = 360 - gap * len(vals)
        start = 90.0
        for i, (lab, v) in enumerate(zip(labels, vals)):
            sweep = v / total * usable
            r = 0.4 + (v / max(vals)) * 0.6
            ax.add_patch(Wedge((0, 0), r, start - sweep, start,
                               width=(r - 0.34) * 0.96,
                               facecolor=EXCEL_PALETTE[i % len(EXCEL_PALETTE)],
                               edgecolor="white", linewidth=1.3))
            mid = np.deg2rad(start - sweep / 2)
            ax.text(1.22 * np.cos(mid), 1.22 * np.sin(mid), lab, ha="center",
                    va="center", fontsize=10, color=INK)
            ax.text(0.86 * np.cos(mid), 0.86 * np.sin(mid), pct(v),
                    ha="center", va="center", fontsize=9, color="white",
                    fontweight="bold")
            start -= sweep + gap
        ax.set_xlim(-1.4, 1.4)
        ax.set_ylim(-1.4, 1.4)
        title_block(fig, ax, f"{period} 流量来源结构",
                    "南丁格尔圆环：角度等分、半径随占比变化",
                    f"数据来源：第三章 动态图表.xlsm / 3 动态南丁格尔圆环图（{k + 1}/{len(periods)}）")
        figures.append(fig)

    return figures_to_gif(figures, OUTPUT_DIR / OUT / "03_动态南丁格尔圆环图.gif",
                          duration_ms=1300)


# --------------------------------------------------------------------------- 04
def chart_04_dynamic_combo():
    """
    4 动态组合图：复选框控制「销售额 / 利润 / 利润率」三个系列是否显示。

    Excel 用 IF($C$13, F4, -100) 把隐藏系列的值甩出绘图区；
    Python 直接用 visible 标志控制绘制，思路更直接。
    """
    df = D.ch3("04_dynamic_combo")
    cats = df["类别"].tolist()
    products = df.columns[1:].tolist()
    sales = df.loc[df["类别"] == "销售额"].iloc[0, 1:].astype(float).tolist()
    profit = df.loc[df["类别"] == "利润"].iloc[0, 1:].astype(float).tolist()
    rate = df.loc[df["类别"] == "利润率"].iloc[0, 1:].astype(float).tolist()
    x = np.arange(len(products))

    # 复选框的 4 种典型组合
    combos = [
        ("全部显示", True, True, True),
        ("仅销售额", True, False, False),
        ("销售额+利润", True, True, False),
        ("销售额+利润率", True, False, True),
    ]

    figures = []
    for name, s_on, p_on, r_on in combos:
        fig, ax = new_axes()
        if s_on:
            ax.bar(x, sales, width=0.45, color=EXCEL_PALETTE[0])
        if p_on:
            ax.bar(x, profit, width=0.45, color=EXCEL_PALETTE[1])
        style_axes(ax)
        ax.set_ylim(-260 if not (s_on or p_on) else 0, max(sales) * 1.25)
        ax.set_xticks(x)
        ax.set_xticklabels(products)

        ax2 = ax.twinx() if r_on else None
        if r_on and ax2 is not None:
            ax2.plot(x, rate, marker="D", markersize=7, linewidth=2,
                     color=EXCEL_PALETTE[3])
            ax2.set_ylim(0, max(rate) * 1.6)
            ax2.spines["top"].set_visible(False)
            ax2.spines["right"].set_visible(False)
            ax2.tick_params(colors=SUB_INK, labelsize=10, length=0)
            ax2.set_yticks(ax2.get_yticks())
            ax2.set_yticklabels([pct(v) for v in ax2.get_yticks()])
            for i, v in enumerate(rate):
                ax2.text(i, v + max(rate) * 0.06, pct(v), ha="center",
                         fontsize=9, color=EXCEL_PALETTE[3])

        legend = [l for l, on in zip(["销售额", "利润", "利润率"],
                                     [s_on, p_on, r_on]) if on]
        colors = [c for c, on in zip(EXCEL_PALETTE[:3], [s_on, p_on, r_on]) if on]
        if legend:
            handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors]
            ax.legend(handles, legend, loc="upper center", ncol=len(legend),
                      frameon=False, bbox_to_anchor=(0.5, 1.03), fontsize=10)
        title_block(fig, ax, f"化妆品销售组合图 · {name}",
                    "复选框组合切换系列显隐，对应 Excel 的复选框 + IF 隐藏法",
                    "数据来源：第三章 动态图表.xlsm / 4 动态组合图")
        figures.append(fig)

    return figures_to_gif(figures, OUTPUT_DIR / OUT / "04_动态组合图.gif",
                          duration_ms=1300)


# --------------------------------------------------------------------------- 05
def chart_05_pivot_slicer():
    """
    5 透视表切片器：用 pandas 透视表复现「数据透视表 + 部门切片器」。

    每一帧相当于点了一下切片器上的某个部门按钮。
    """
    df = D.ch3("05_hr_detail")
    depts = ["全部"] + sorted(df["部门"].dropna().unique().tolist())
    edu_order = ["专科以下", "专科", "本科", "硕士研究生", "博士研究生"]

    figures = []
    for dept in depts:
        sub = df if dept == "全部" else df[df["部门"] == dept]
        pivot = (sub.groupby("学历")["月收入"].mean()
                 .reindex(edu_order).fillna(0))

        fig, ax = new_axes()
        bars = ax.bar(pivot.index, pivot.values, width=0.52,
                      color=EXCEL_PALETTE[0])
        style_axes(ax)
        ax.set_ylim(0, max(pivot.values) * 1.25 if max(pivot.values) else 1)
        value_labels(ax, bars, fmt="{:,.0f}")
        n = len(sub)
        avg = sub["月收入"].mean() if n else 0
        title_block(fig, ax, f"各学历平均月收入 · 切片器：{dept}",
                    f"样本 {n:,} 人，总体平均 {avg:,.0f} 元/月",
                    "数据来源：第三章 动态图表.xlsm / 5 人力资源明细 + 透视表切片器")
        figures.append(fig)

    return figures_to_gif(figures, OUTPUT_DIR / OUT / "05_透视表切片器.gif",
                          duration_ms=1100)


# --------------------------------------------------------------------------- 06
def chart_06_dynamic_jade():
    """6 VBA 动态玉玦图：VBA 换源 → Python 直接按周期循环重绘。"""
    df = D.ch3("06_dynamic_jade")
    periods = df["周期"].tolist()

    figures = []
    for k, period in enumerate(periods):
        vals = df.iloc[k, 1:].astype(float).tolist()
        labels = df.columns[1:].tolist()
        fig, ax = new_axes(figsize=(7, 5.6), rect=(0.05, 0.08, 0.9, 0.72))
        ax.set_aspect("equal")
        ax.axis("off")
        gap = 8.0
        usable = 360 - gap * len(vals)
        total = sum(vals)
        start = 90.0
        for i, (lab, v) in enumerate(zip(labels, vals)):
            sweep = v / total * usable
            ax.add_patch(Wedge((0, 0), 1.0, start - sweep, start, width=0.3,
                               facecolor=EXCEL_PALETTE[i % len(EXCEL_PALETTE)],
                               edgecolor="white", linewidth=1.3))
            mid = np.deg2rad(start - sweep / 2)
            ax.text(1.18 * np.cos(mid), 1.18 * np.sin(mid), lab, ha="center",
                    va="center", fontsize=10, color=INK)
            ax.text(0.85 * np.cos(mid), 0.85 * np.sin(mid), pct(v),
                    ha="center", va="center", fontsize=9, color="white",
                    fontweight="bold")
            start -= sweep + gap
        ax.set_xlim(-1.35, 1.35)
        ax.set_ylim(-1.35, 1.35)
        title_block(fig, ax, f"{period} 流量来源玉玦图",
                    "原书用 VBA 宏切换数据源，这里直接循环重绘",
                    f"数据来源：第三章 动态图表.xlsm / 6 VBA动态玉玦图（{k + 1}/{len(periods)}）")
        figures.append(fig)

    return figures_to_gif(figures, OUTPUT_DIR / OUT / "06_动态玉玦图.gif",
                          duration_ms=1300)


# --------------------------------------------------------------------------- 07
def chart_07_dynamic_bead():
    """7 动态滑珠图：滚动条选择月份，滑珠按当月完成率重新落位。"""
    df = D.ch3("07_dynamic_bead")
    months = df.columns[1:].tolist()

    figures = []
    for k, month in enumerate(months):
        sub = df.sort_values(month, ascending=True).reset_index(drop=True)
        labels = sub["区域"].tolist()
        rate = sub[month].astype(float).tolist()
        y = np.arange(len(labels))

        fig, ax = new_axes(figsize=(9, 5.0), rect=(0.12, 0.14, 0.84, 0.7))
        ax.barh(y, [1.0] * len(rate), height=0.18, color="#E6E6E6", zorder=1)
        ax.barh(y, rate, height=0.18, color="#EDF2F9", zorder=2)
        ax.scatter(rate, y, s=420, color=EXCEL_PALETTE[0], edgecolor="white",
                   linewidths=2, zorder=4)
        style_axes(ax, axis="x", grid=False)
        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.set_xlim(0, 1.02)
        ax.set_xticks(np.linspace(0, 1, 6))
        ax.set_xticklabels([pct(v) for v in np.linspace(0, 1, 6)])
        for i, v in enumerate(rate):
            ax.text(v, y[i] + 0.26, pct(v), ha="center", fontsize=9.5,
                    color=EXCEL_PALETTE[0], fontweight="bold")
        title_block(fig, ax, f"{month} 各区域完成率滑珠图",
                    "滚动条切换月份，滑珠位置随完成率重新分布",
                    f"数据来源：第三章 动态图表.xlsm / 7 动态滑珠图（{k + 1}/{len(months)}）")
        figures.append(fig)

    return figures_to_gif(figures, OUTPUT_DIR / OUT / "07_动态滑珠图.gif",
                          duration_ms=1000)


CHARTS = [
    chart_01_dynamic_bar, chart_02_dynamic_racetrack, chart_03_dynamic_rose,
    chart_04_dynamic_combo, chart_05_pivot_slicer, chart_06_dynamic_jade,
    chart_07_dynamic_bead,
]


def run_all():
    return [fn() for fn in CHARTS]


if __name__ == "__main__":
    for p in run_all():
        print(p)
