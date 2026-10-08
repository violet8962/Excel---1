# -*- coding: utf-8 -*-
"""
第二章 · 前 15 例（渐变柱形图 → 水球图）
======================================

原书第二章前半部分的 15 个案例，逐一用 matplotlib 复现。

Excel 里的实现套路 vs Python 实现对照见 README 的「实现对照表」。
每个函数独立返回输出图片路径，可单独调用，便于逐个对照学习。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Circle, Rectangle, Wedge

from . import data as D
from .theme import (
    EXCEL_PALETTE, GRID, INK, SUB_INK, gradient_bars, legend_simple,
    new_axes, pct, rounded_bar, save, style_axes, title_block, value_labels,
    vcmap,
)
from .utils import catmull_rom, drop_lines

OUT = "ch2"


# --------------------------------------------------------------------------- 01
def chart_01_gradient_bar():
    """01 渐变柱形图：柱形改用渐变填充，替代 Excel 单调的纯色柱。"""
    df = D.ch2("01_gradient_bar")
    fig, ax = new_axes()
    labels = df["区域"].tolist()
    vals = df["销售量"].astype(float).tolist()

    bars = ax.bar(labels, vals, width=0.55, color="none", edgecolor="none")
    # 从主色向浅色渐变，视觉重心落在柱顶
    gradient_bars(ax, bars, colors=EXCEL_PALETTE[0], light_amount=0.62)

    style_axes(ax)
    ax.set_ylim(0, max(vals) * 1.18)
    value_labels(ax, bars)
    title_block(fig, ax, "各区域销售量对比",
                "东北区域销售量领先，华南区域相对薄弱",
                "数据来源：第二章 图表(前15).xlsx / 1 渐变柱形图")
    return save(fig, OUT, "01_渐变柱形图.png")


# --------------------------------------------------------------------------- 02
def chart_02_mean_bar():
    """02 带均值柱形图：加一条均值参考线，把「看数值」升级为「看偏离」。"""
    df = D.ch2("02_mean_bar")
    fig, ax = new_axes()
    labels = df["区域"].tolist()
    vals = df["销售量"].astype(float).tolist()
    mean = float(np.mean(vals))

    bars = ax.bar(labels, vals, width=0.55, color=EXCEL_PALETTE[0])
    style_axes(ax)
    ax.set_ylim(0, max(vals) * 1.2)

    # 均值线：Excel 里靠「增加辅助序列」，Python 直接 axhline 一步到位
    ax.axhline(mean, color=EXCEL_PALETTE[1], linewidth=1.6,
               linestyle=(0, (6, 3)), zorder=3)
    ax.text(len(labels) - 0.45, mean * 1.03, f"均值 {mean:,.1f}",
            color=EXCEL_PALETTE[1], fontsize=10, ha="right")

    # 高亮高于均值的柱形，强化对比
    for bar, v in zip(bars, vals):
        above = v >= mean
        bar.set_color(EXCEL_PALETTE[0] if above else EXCEL_PALETTE[2])
    value_labels(ax, bars)
    legend_simple(ax, ["高于均值", "低于均值"],
                  [EXCEL_PALETTE[0], EXCEL_PALETTE[2]], y=1.03)
    title_block(fig, ax, "各区域销售量与均值对比",
                f"公司平均销售量 {mean:,.0f}，东北、西南、西北三个区域跑赢均值",
                "数据来源：第二章 图表(前15).xlsx / 2 带均值柱形图")
    return save(fig, OUT, "02_带均值柱形图.png")


# --------------------------------------------------------------------------- 03
def chart_03_rounded_bar():
    """03 渐变圆角柱形图：圆角柱形，观感更柔和，适合对外汇报。"""
    df = D.ch2("03_rounded_bar")
    fig, ax = new_axes()
    labels = df["商品"].tolist()
    vals = df["销量"].astype(float).tolist()
    order = np.argsort(vals)[::-1]

    labels = [labels[i] for i in order]
    vals = [vals[i] for i in order]

    style_axes(ax)
    ax.set_xlim(-0.6, len(labels) - 0.4)
    ax.set_ylim(0, max(vals) * 1.18)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)

    for i, v in enumerate(vals):
        rounded_bar(ax, i - 0.28, 0, 0.56, v, facecolor=EXCEL_PALETTE[0],
                    light_amount=0.55)
        ax.text(i, v + max(vals) * 0.03, f"{v:,.0f}", ha="center",
                va="bottom", fontsize=10, color=INK)

    title_block(fig, ax, "各商品销量排名",
                "防晒霜销量最高，面膜销量暂时垫底",
                "数据来源：第二章 图表(前15).xlsx / 3 渐变圆角柱形图")
    return save(fig, OUT, "03_渐变圆角柱形图.png")


# --------------------------------------------------------------------------- 04
def chart_04_annotated_bar():
    """04 标注柱形图：对极值做强调标注，替读者先一步找出结论。"""
    df = D.ch2("04_annotated_bar")
    fig, ax = new_axes(figsize=(9.6, 5.4))
    labels = df["月份"].tolist()
    vals = df["销量"].astype(float).tolist()

    imax, imin = int(np.argmax(vals)), int(np.argmin(vals))
    colors = []
    for i in range(len(vals)):
        if i == imax:
            colors.append(EXCEL_PALETTE[0])
        elif i == imin:
            colors.append(EXCEL_PALETTE[1])
        else:
            colors.append(EXCEL_PALETTE[2])

    bars = ax.bar(labels, vals, width=0.56, color=colors)
    style_axes(ax)
    ax.set_ylim(0, max(vals) * 1.28)
    value_labels(ax, bars)

    # 极值标注：引出线 + 结论文字
    ax.annotate(f"最高 {vals[imax]:,.0f}",
                xy=(imax, vals[imax]), xytext=(imax + 0.9, vals[imax] * 1.09),
                fontsize=10, color=EXCEL_PALETTE[0], fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=EXCEL_PALETTE[0], lw=1.2))
    ax.annotate(f"最低 {vals[imin]:,.0f}",
                xy=(imin, vals[imin]), xytext=(imin - 1.6, vals[imin] * 1.55),
                fontsize=10, color=EXCEL_PALETTE[1], fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=EXCEL_PALETTE[1], lw=1.2))

    title_block(fig, ax, "各商品销量分布",
                f"口红销量最高（{vals[imax]:,.0f}），眼影最低（{vals[imin]:,.0f}），"
                f"极差 {vals[imax] - vals[imin]:,.0f}",
                "数据来源：第二章 图表(前15).xlsx / 4 标注柱形图")
    return save(fig, OUT, "04_标注柱形图.png")


# --------------------------------------------------------------------------- 05
def chart_05_overlap_bar():
    """05 层叠柱形图：销售额打底、利润额叠加，同时呈现规模与质量。"""
    df = D.ch2("05_overlap_bar")
    fig, ax = new_axes()
    labels = df["季度"].tolist()
    sales = df["销售额"].astype(float).tolist()
    profit = df["利润额"].astype(float).tolist()
    x = np.arange(len(labels))

    ax.bar(x, sales, width=0.62, color=EXCEL_PALETTE[0], label="销售额")
    ax.bar(x, profit, width=0.34, color=EXCEL_PALETTE[1], label="利润额")
    style_axes(ax)
    ax.set_ylim(0, max(sales) * 1.2)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    for i, (s, p) in enumerate(zip(sales, profit)):
        ax.text(i, s + max(sales) * 0.025, f"{s:,.0f}", ha="center",
                fontsize=9.5, color=EXCEL_PALETTE[0])
        ax.text(i, p * 0.5, f"{p:,.0f}", ha="center", fontsize=9,
                color="white", fontweight="bold")

    legend_simple(ax, ["销售额", "利润额"], EXCEL_PALETTE[:2])
    title_block(fig, ax, "各季度销售额与利润额",
                "销售额稳步上行，利润额增速略低于销售额",
                "数据来源：第二章 图表(前15).xlsx / 5 层叠柱形图")
    return save(fig, OUT, "05_层叠柱形图.png")


# --------------------------------------------------------------------------- 06
def chart_06_butterfly():
    """06 蝴蝶图（双向条形）：两个年份背靠背，一眼看出结构差异。"""
    df = D.ch2("06_butterfly")
    fig, ax = new_axes(figsize=(9.4, 5.2))
    labels = df["区域"].tolist()
    y2022 = df["2022年销量"].astype(float).tolist()
    y2021 = df["2021年销量"].astype(float).tolist()
    y = np.arange(len(labels))
    span = max(max(y2022), max(y2021)) * 1.25

    ax.barh(y, [-v for v in y2022], height=0.55, color=EXCEL_PALETTE[0])
    ax.barh(y, y2021, height=0.55, color=EXCEL_PALETTE[1])
    style_axes(ax, axis="x", grid=False)
    ax.set_ylim(-0.75, len(labels) - 0.25)
    ax.set_xlim(-span, span)
    ax.set_yticks([])
    ax.axvline(0, color="#8A8A8A", lw=1.0)

    for i, (a, b) in enumerate(zip(y2022, y2021)):
        ax.text(-a - span * 0.02, i, f"{a:,.0f}", ha="right", va="center",
                fontsize=10, color=EXCEL_PALETTE[0])
        ax.text(b + span * 0.02, i, f"{b:,.0f}", ha="left", va="center",
                fontsize=10, color=EXCEL_PALETTE[1])
        # 区域名放在中轴，形成蝴蝶的「身体」
        ax.text(0, i, labels[i], ha="center", va="center", fontsize=11,
                color=INK, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.28", fc="white",
                          ec="#CCCCCC", lw=0.8))

    ax.text(-span * 0.55, -0.52, "2022年", fontsize=11,
            color=EXCEL_PALETTE[0], fontweight="bold", ha="center")
    ax.text(span * 0.55, -0.52, "2021年", fontsize=11,
            color=EXCEL_PALETTE[1], fontweight="bold", ha="center")

    title_block(fig, ax, "各区域两年销量对比",
                "华南连续两年领先，华东规模最小且同比基本持平",
                "数据来源：第二章 图表(前15).xlsx / 6 蝴蝶图")
    return save(fig, OUT, "06_蝴蝶图.png")


# --------------------------------------------------------------------------- 07
def chart_07_butterfly_pct():
    """07 蝴蝶图（百分比版）：把绝对量换成占比，比较的是结构而非规模。"""
    df = D.ch2("07_butterfly_pct")
    fig, ax = new_axes(figsize=(9.4, 5.2))
    labels = df["区域"].tolist()
    p2022 = df["2022年"].astype(float).tolist()
    p2021 = df["2021年"].astype(float).tolist()
    y = np.arange(len(labels))
    span = max(max(p2022), max(p2021)) * 1.35

    ax.barh(y, [-v for v in p2022], height=0.55, color=EXCEL_PALETTE[0])
    ax.barh(y, p2021, height=0.55, color=EXCEL_PALETTE[1])
    style_axes(ax, axis="x", grid=False)
    ax.set_ylim(-0.75, len(labels) - 0.25)
    ax.set_xlim(-span, span)
    ax.set_yticks([])
    ax.axvline(0, color="#8A8A8A", lw=1.0)
    ax.set_xticklabels([])

    for i, (a, b) in enumerate(zip(p2022, p2021)):
        ax.text(-a - span * 0.03, i, pct(a), ha="right", va="center",
                fontsize=10.5, color=EXCEL_PALETTE[0])
        ax.text(b + span * 0.03, i, pct(b), ha="left", va="center",
                fontsize=10.5, color=EXCEL_PALETTE[1])
        ax.text(0, i, labels[i], ha="center", va="center", fontsize=11,
                color=INK, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.28", fc="white",
                          ec="#CCCCCC", lw=0.8))

    ax.text(-span * 0.55, -0.52, "2022年占比", fontsize=11,
            color=EXCEL_PALETTE[0], fontweight="bold", ha="center")
    ax.text(span * 0.55, -0.52, "2021年占比", fontsize=11,
            color=EXCEL_PALETTE[1], fontweight="bold", ha="center")

    title_block(fig, ax, "各区域销量占比两年对比",
                "华东占比由 42.0% 降至 36.0%，华南占比翻倍至 22.0%",
                "数据来源：第二章 图表(前15).xlsx / 7 蝴蝶图")
    return save(fig, OUT, "07_蝴蝶图_百分比.png")


# --------------------------------------------------------------------------- 08
def chart_08_percent_bar():
    """08 数值百分比：一条进度条同时给出「绝对数值」与「占最大值的百分比」。"""
    df = D.ch2("08_percent_bar")
    fig, ax = new_axes(figsize=(9.6, 5.4))
    labels = df["区域"].tolist()
    vals = df["销量"].astype(float).tolist()
    yoy = df["同比去年"].astype(float).tolist()
    vmax = max(vals)
    y = np.arange(len(labels))[::-1]

    # 底槽（占位1 的等价物）：浅灰色轨道表示 100%
    ax.barh(y, [vmax] * len(vals), height=0.5, color="#EDEDED", zorder=1)
    bars = ax.barh(y, vals, height=0.5, color=EXCEL_PALETTE[0], zorder=2)
    style_axes(ax, axis="x", grid=False)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, vmax * 1.02)
    ax.set_xticks(np.linspace(0, vmax, 5))
    ax.set_xticklabels([f"{pct(v / vmax)}" for v in np.linspace(0, vmax, 5)])

    for i, (v, g) in enumerate(zip(vals, yoy)):
        ax.text(v + vmax * 0.015, y[i], f"{v:,.0f}", va="center",
                fontsize=10.5, color=INK, fontweight="bold")
        color = "#C00000" if g < 0 else "#2E7D32"
        ax.text(vmax * 1.005, y[i] - 0.0, f"{'▼' if g < 0 else '▲'} {pct(abs(g))}",
                va="center", ha="left", fontsize=9.5, color=color)

    ax.set_xlim(0, vmax * 1.02)
    ax.text(vmax * 1.005, len(labels) - 0.45, "同比", fontsize=9.5,
            color=SUB_INK, ha="left")
    title_block(fig, ax, "各区域销量与同比变化",
                "六个区域销量同比全部下滑，华北降幅最小（-5.8%）",
                "数据来源：第二章 图表(前15).xlsx / 8 数值百分比")
    return save(fig, OUT, "08_数值百分比.png")


# --------------------------------------------------------------------------- 09
def chart_09_compare_bar():
    """09 对比柱形图：并排两根柱 + 差值标注，把「差多少」直接写出来。"""
    df = D.ch2("09_compare_bar")
    fig, ax = new_axes()
    labels = df["商品"].tolist()
    y2021 = df["2021销量"].astype(float).tolist()
    y2022 = df["2022销量"].astype(float).tolist()
    diff = df["差值"].astype(float).tolist()
    x = np.arange(len(labels))

    b1 = ax.bar(x - 0.19, y2021, width=0.36, color=EXCEL_PALETTE[0])
    b2 = ax.bar(x + 0.19, y2022, width=0.36, color=EXCEL_PALETTE[1])
    style_axes(ax)
    ax.set_ylim(0, max(y2021) * 1.28)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    for i in range(len(labels)):
        top = max(y2021[i], y2022[i])
        ax.annotate("", xy=(x[i] + 0.19, y2022[i]), xytext=(x[i] - 0.19, y2021[i]),
                    arrowprops=dict(arrowstyle="-", color=SUB_INK, lw=0.9,
                                    ls=(0, (3, 2))))
        ax.text(x[i], top + max(y2021) * 0.07, f"-{diff[i]:,.0f}",
                ha="center", fontsize=10, color="#C00000", fontweight="bold")

    value_labels(ax, b1, offset=0.015, fontsize=9)
    value_labels(ax, b2, offset=0.015, fontsize=9)
    legend_simple(ax, ["2021年", "2022年"], EXCEL_PALETTE[:2])
    title_block(fig, ax, "各商品两年销量对比",
                "五个商品 2022 年销量全面下滑，隔离霜降幅最大",
                "数据来源：第二章 图表(前15).xlsx / 9 对比柱形图")
    return save(fig, OUT, "09_对比柱形图.png")


# --------------------------------------------------------------------------- 10
def chart_10_gantt():
    """10 甘特图：横向条形 + 时间轴，项目排期与完成度一图表达。"""
    df = D.ch2("10_gantt").copy()
    df["开始日期"] = pd.to_datetime(df["开始日期"])
    df["结束日期"] = pd.to_datetime(df["结束日期"])
    df = df.iloc[::-1].reset_index(drop=True)  # 让第一个任务显示在顶部

    fig, ax = new_axes(figsize=(10, 5.4), rect=(0.14, 0.16, 0.82, 0.7))
    y = np.arange(len(df))
    start = df["开始日期"]
    days = df["项目天数"].astype(float)
    done = df["完成度"].astype(float)

    # 计划条：浅色；完成条：深色叠加，形成「进度条」效果
    ax.barh(y, days, left=start, height=0.45, color="#D6E4F7", zorder=2)
    ax.barh(y, days * done, left=start, height=0.45, color=EXCEL_PALETTE[0],
            zorder=3)
    style_axes(ax, axis="x", grid=True)
    ax.set_yticks(y)
    ax.set_yticklabels(df["项目名称"])
    ax.xaxis.set_major_locator(__import__("matplotlib").dates.DayLocator(interval=7))
    ax.xaxis.set_major_formatter(__import__("matplotlib").dates.DateFormatter("%m-%d"))

    for i, (s, d, p) in enumerate(zip(start, days, done)):
        ax.text(s + pd.Timedelta(days=float(d)) + pd.Timedelta(days=0.6), i,
                pct(p), va="center", fontsize=9.5, color=SUB_INK)

    legend_simple(ax, ["计划工期", "已完成"], ["#D6E4F7", EXCEL_PALETTE[0]])
    title_block(fig, ax, "项目排期甘特图",
                "第一阶段完成度最高（85%），资源调配进度最慢（21%）",
                "数据来源：第二章 图表(前15).xlsx / 10 甘特图")
    return save(fig, OUT, "10_甘特图.png")


# --------------------------------------------------------------------------- 11
def chart_11_smooth_line():
    """11 平滑折线图：Catmull-Rom 样条平滑，对应 Excel 的「平滑线」。"""
    df = D.ch2("11_smooth_line")
    xlab = [f"{y}\n{m}" for y, m in zip(df["年份"], df["月份"])]
    vals = df["销量"].astype(float).tolist()
    x = np.arange(len(vals))

    fig, ax = new_axes(figsize=(10, 5.4))
    sx, sy = catmull_rom(np.column_stack([x, vals]), samples_per_segment=60)
    ax.plot(sx, sy, color=EXCEL_PALETTE[0], linewidth=2.4, zorder=3)
    ax.scatter(x, vals, s=38, color="white", edgecolor=EXCEL_PALETTE[0],
               linewidths=1.8, zorder=4)
    ax.fill_between(sx, 0, sy, color=EXCEL_PALETTE[0], alpha=0.10, zorder=1)

    style_axes(ax)
    ax.set_ylim(0, max(vals) * 1.18)
    ax.set_xlim(-0.3, len(vals) - 0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(xlab, fontsize=8.5)

    # 跨年份处加分隔线，提示口径切换
    change = int(df["年份"].ne(df["年份"].shift()).idxmax()) if df["年份"].nunique() > 1 else None
    if change:
        ax.axvline(change - 0.5, color="#BBBBBB", lw=1.0, ls=(0, (4, 3)))
        ax.text(change - 0.5, max(vals) * 1.12, "跨年", fontsize=9,
                color=SUB_INK, ha="center")

    for i, v in enumerate(vals):
        ax.text(i, v + max(vals) * 0.035, f"{v:,.0f}", ha="center", fontsize=8.5,
                color=SUB_INK)

    title_block(fig, ax, "月度销量走势",
                "2022 年 1 月销量跳升至 3782，随后逐月回落",
                "数据来源：第二章 图表(前15).xlsx / 11 平滑折线图")
    return save(fig, OUT, "11_平滑折线图.png")


# --------------------------------------------------------------------------- 12
def chart_12_diamond_line():
    """12 菱形走势图：菱形数据标记 + 垂直线，Excel 用「线条」元素撑版面。"""
    df = D.ch2("12_diamond_line")
    labels = df["月份"].tolist()
    vals = df["完成率"].astype(float).tolist()
    x = np.arange(len(vals))
    mean = float(np.mean(vals))

    fig, ax = new_axes(figsize=(9.6, 5.2))
    drop_lines(ax, x, vals, bottom=0)  # 垂直线
    ax.plot(x, vals, color=EXCEL_PALETTE[0], linewidth=1.6, alpha=0.55, zorder=2)
    ax.scatter(x, vals, marker="D", s=70, color=EXCEL_PALETTE[0],
               edgecolor="white", linewidths=1.4, zorder=4)

    style_axes(ax)
    ax.set_ylim(0, max(vals) * 1.3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    yticks = ax.get_yticks()
    ax.set_yticks(yticks)
    ax.set_yticklabels([pct(v) for v in yticks])

    ax.axhline(mean, color=EXCEL_PALETTE[1], lw=1.4, ls=(0, (6, 3)), zorder=3)
    ax.text(len(vals) - 1, mean * 1.02, f"平均完成率 {pct(mean)}",
            fontsize=10, color=EXCEL_PALETTE[1], ha="right")

    for i, v in enumerate(vals):
        ax.text(i, v + max(vals) * 0.045, pct(v), ha="center", fontsize=9,
                color=INK)

    title_block(fig, ax, "月度目标完成率走势",
                f"4 月完成率最高（70.8%），平均完成率 {pct(mean)}",
                "数据来源：第二章 图表(前15).xlsx / 12 菱形走势图")
    return save(fig, OUT, "12_菱形走势图.png")


# --------------------------------------------------------------------------- 13
def chart_13_compare_line():
    """13 对比折线图：两条折线 + 差值填充，差异区域被显式涂出来。"""
    df = D.ch2("13_compare_line")
    labels = df["月份"].tolist()
    y2021 = df["2021年"].astype(float).tolist()
    y2022 = df["2022年"].astype(float).tolist()
    x = np.arange(len(labels))

    fig, ax = new_axes()
    ax.plot(x, y2021, marker="o", markersize=6, linewidth=2,
            color=EXCEL_PALETTE[2])
    ax.plot(x, y2022, marker="o", markersize=6, linewidth=2,
            color=EXCEL_PALETTE[0])
    # 差值填充：2022 高于 2021 用主色，低于用橙色
    ax.fill_between(x, y2021, y2022, where=np.array(y2022) >= np.array(y2021),
                    interpolate=True, color=EXCEL_PALETTE[0], alpha=0.16)
    ax.fill_between(x, y2021, y2022, where=np.array(y2022) < np.array(y2021),
                    interpolate=True, color=EXCEL_PALETTE[1], alpha=0.16)

    style_axes(ax)
    ax.set_ylim(0, max(max(y2021), max(y2022)) * 1.22)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    for i, (a, b) in enumerate(zip(y2021, y2022)):
        ax.text(i, a - max(max(y2021), max(y2022)) * 0.07, f"{a:,.0f}",
                ha="center", fontsize=9, color=EXCEL_PALETTE[2])
        ax.text(i, b + max(max(y2021), max(y2022)) * 0.03, f"{b:,.0f}",
                ha="center", fontsize=9, color=EXCEL_PALETTE[0])

    legend_simple(ax, ["2021年", "2022年"], [EXCEL_PALETTE[2], EXCEL_PALETTE[0]])
    title_block(fig, ax, "月度销量两年对比",
                "2022 年下半年明显发力，5 月起全面超过 2021 年同期",
                "数据来源：第二章 图表(前15).xlsx / 13 对比折线图")
    return save(fig, OUT, "13_对比折线图.png")


# --------------------------------------------------------------------------- 14
def chart_14_single_donut():
    """14 单值圆环图：只表达一个百分比，中心放数值，是最省版面的 KPI 图。"""
    df = D.ch2("14_single_donut")
    rate = float(df["完成率"].iloc[0])

    fig, ax = new_axes(figsize=(6.4, 5.2), rect=(0.08, 0.1, 0.84, 0.76))
    ax.set_aspect("equal")
    # 底环 + 完成弧
    ax.add_patch(Wedge((0, 0), 1.0, 90, -270, width=0.28,
                       facecolor="#E8E8E8", edgecolor="none"))
    ax.add_patch(Wedge((0, 0), 1.0, 90, 90 - rate * 360, width=0.28,
                       facecolor=EXCEL_PALETTE[0], edgecolor="none"))
    ax.text(0, 0.06, pct(rate), ha="center", va="center", fontsize=34,
            color=EXCEL_PALETTE[0], fontweight="bold")
    ax.text(0, -0.26, "完成率", ha="center", va="center", fontsize=12,
            color=SUB_INK)
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.2, 1.2)
    ax.axis("off")

    title_block(fig, ax, "年度目标完成情况",
                f"当前完成率 {pct(rate)}，接近年度目标",
                "数据来源：第二章 图表(前15).xlsx / 14 单值圆环图")
    return save(fig, OUT, "14_单值圆环图.png")


# --------------------------------------------------------------------------- 15
def chart_15_liquid():
    """15 水球图：圆形容器内按完成率注水，比圆环图更有「仪表」感。"""
    df = D.ch2("15_liquid")
    rate = float(df["完成率"].iloc[0])

    fig, ax = new_axes(figsize=(6.4, 5.4), rect=(0.08, 0.1, 0.84, 0.74))
    ax.set_aspect("equal")
    r = 1.0
    # 容器
    ax.add_patch(Circle((0, 0), r, facecolor="#F2F5F9", edgecolor=EXCEL_PALETTE[0],
                        linewidth=2.2, zorder=1))
    # 注水：用矩形与圆求交（clip_path）
    water_top = -r + 2 * r * rate
    water = Rectangle((-r, -r), 2 * r, water_top + r,
                      facecolor=EXCEL_PALETTE[0], edgecolor="none", zorder=2)
    ax.add_patch(water)
    water.set_clip_path(Circle((0, 0), r * 0.985, transform=ax.transData))

    # 水面高光
    xs = np.linspace(-r, r, 200)
    ax.plot(xs, np.full_like(xs, water_top), color="white", lw=2.0, zorder=3,
            clip_path=water.get_clip_path())

    ax.text(0, 0.04, pct(rate), ha="center", va="center", fontsize=32,
            color="white" if rate > 0.5 else EXCEL_PALETTE[0],
            fontweight="bold", zorder=5)
    ax.text(0, -0.32, "完成率", ha="center", va="center", fontsize=12,
            color="white" if rate > 0.5 else SUB_INK, zorder=5)

    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.25, 1.25)
    ax.axis("off")
    title_block(fig, ax, "目标完成进度",
                f"注水高度即完成率 {pct(rate)}，尚未过半程线以上的安全区",
                "数据来源：第二章 图表(前15).xlsx / 15 水球图")
    return save(fig, OUT, "15_水球图.png")


CHARTS = [
    chart_01_gradient_bar, chart_02_mean_bar, chart_03_rounded_bar,
    chart_04_annotated_bar, chart_05_overlap_bar, chart_06_butterfly,
    chart_07_butterfly_pct, chart_08_percent_bar, chart_09_compare_bar,
    chart_10_gantt, chart_11_smooth_line, chart_12_diamond_line,
    chart_13_compare_line, chart_14_single_donut, chart_15_liquid,
]


def run_all():
    return [fn() for fn in CHARTS]


if __name__ == "__main__":
    for p in run_all():
        print(p)
