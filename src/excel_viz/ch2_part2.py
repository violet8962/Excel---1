# -*- coding: utf-8 -*-
"""
第二章 · 后 15 例（波浪水球图 → 对比滑珠图）
==========================================

原书第二章后半部分的 15 个案例，偏「装饰性/KPI 型」图表：
水球、玉玦、跑道、南丁格尔、仪表盘、子弹图、滑珠图……

这类图在 Excel 里大多靠「圆环图 + 辅助占位序列 + 形状叠加」拼出来，
Python 里则可以直接用极坐标 / 任意形状组合绘制，实现成本低得多。
"""
from __future__ import annotations

import numpy as np
from matplotlib.patches import Circle, Rectangle, Wedge

from . import data as D
from .theme import (
    EXCEL_PALETTE, INK, SUB_INK, legend_simple, new_axes, pct, rounded_bar,
    save, style_axes, title_block, value_labels, vcmap,
)
from .utils import drop_lines

OUT = "ch2"


def _polar_axes(figsize=(6.6, 5.6), rect=(0.06, 0.1, 0.88, 0.74)):
    """画 KPI 类圆形图专用的等比画布。"""
    fig, ax = new_axes(figsize, rect)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def _rose(ax, labels, values, *, inner_r=0.0, r_scale=1.0,
          palette=None, width_gap=0.02):
    """
    南丁格尔玫瑰图的核心：每个扇区半径按数值大小缩放。

    Excel 里靠「圆环图多层复制 + 逐层设半径」实现，
    这里直接用 Wedge 一个循环搞定，半径与数值成正比。
    """
    palette = palette or EXCEL_PALETTE
    total = sum(values)
    start = 90.0
    rmax = max(values) or 1.0
    for i, (lab, v) in enumerate(zip(labels, values)):
        sweep = -v / total * 360
        r = (inner_r + (v / rmax) * (1.0 - inner_r)) * r_scale
        ax.add_patch(Wedge((0, 0), r, start + sweep, start,
                           width=(r - inner_r) * 0.98 if inner_r else None,
                           facecolor=palette[i % len(palette)],
                           edgecolor="white", linewidth=1.2))
        mid = np.deg2rad(start + sweep / 2)
        ax.text(1.16 * r * np.cos(mid), 1.16 * r * np.sin(mid), lab,
                ha="center", va="center", fontsize=10, color=INK)
        start += sweep


# --------------------------------------------------------------------------- 16
def chart_16_wave_liquid():
    """16 波浪水球图：在 15 例的基础上给水面加正弦波。"""
    df = D.ch2("16_wave_liquid")
    rate = float(df["完成率"].iloc[0])

    fig, ax = _polar_axes((6.6, 5.6))
    r = 1.0
    ax.add_patch(Circle((0, 0), r, facecolor="#F2F5F9",
                        edgecolor=EXCEL_PALETTE[0], linewidth=2.2, zorder=1))

    water_top = -r + 2 * r * rate
    xs = np.linspace(-r, r, 400)
    wave = water_top + 0.05 * np.sin(np.linspace(0, 6 * np.pi, 400))
    verts = np.column_stack([np.concatenate([xs, xs[::-1]]),
                             np.concatenate([wave, np.full_like(xs, -r)])])
    from matplotlib.patches import Polygon
    poly = Polygon(verts, closed=True, facecolor=EXCEL_PALETTE[0],
                   edgecolor="none", zorder=2)
    ax.add_patch(poly)
    poly.set_clip_path(Circle((0, 0), r * 0.985, transform=ax.transData))
    # 第二层浅色波，制造层次
    wave2 = water_top + 0.05 * np.sin(np.linspace(0, 6 * np.pi, 400) + 0.9) - 0.03
    verts2 = np.column_stack([np.concatenate([xs, xs[::-1]]),
                              np.concatenate([wave2, np.full_like(xs, -r)])])
    poly2 = Polygon(verts2, closed=True, facecolor=vcmap(EXCEL_PALETTE[0])(0.35),
                    edgecolor="none", zorder=2, alpha=0.55)
    ax.add_patch(poly2)
    poly2.set_clip_path(Circle((0, 0), r * 0.985, transform=ax.transData))

    ax.text(0, 0.02, pct(rate), ha="center", va="center", fontsize=32,
            color="white", fontweight="bold", zorder=5)
    ax.text(0, -0.3, "完成率", ha="center", va="center", fontsize=12,
            color="white", zorder=5)
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.25, 1.25)
    title_block(fig, ax, "目标完成进度（波浪水球）",
                f"完成率 {pct(rate)}，水面随时间轻微起伏，仪表感更强",
                "数据来源：第二章 图表(后15).xlsx / 16 波浪水球图")
    return save(fig, OUT, "16_波浪水球图.png")


# --------------------------------------------------------------------------- 17
def chart_17_jade_ring():
    """
    17 玉玦图：各分类沿圆环依次排开，弧长与占比成正比，段与段之间留缺口。

    「玦」即有缺口的环形玉器——Excel 原例用「占比 + 占位」两列凑出缺口，
    Python 里直接控制每个扇区的起止角即可，逻辑更直观。
    """
    df = D.ch2("17_jade_ring")
    labels = df["年龄"].tolist()
    vals = df["占比"].astype(float).tolist()

    fig, ax = _polar_axes()
    gap_deg = 8.0                                   # 每段之间的缺口
    usable = 360.0 - gap_deg * len(vals)
    total = sum(vals)
    palette = [EXCEL_PALETTE[0], EXCEL_PALETTE[4], EXCEL_PALETTE[1],
               EXCEL_PALETTE[2]]

    start = 90.0
    for i, (lab, v) in enumerate(zip(labels, vals)):
        sweep = v / total * usable
        ax.add_patch(Wedge((0, 0), 1.0, start - sweep, start, width=0.3,
                           facecolor=palette[i % len(palette)],
                           edgecolor="white", linewidth=1.4))
        mid = np.deg2rad(start - sweep / 2)
        ax.text(1.18 * np.cos(mid), 1.18 * np.sin(mid), lab, ha="center",
                va="center", fontsize=10.5, color=INK)
        ax.text(0.85 * np.cos(mid), 0.85 * np.sin(mid), pct(v), ha="center",
                va="center", fontsize=9.5, color="white", fontweight="bold")
        start -= sweep + gap_deg

    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    title_block(fig, ax, "员工年龄结构（玉玦图）",
                "30 岁以下员工占 37.5%，是公司主力；50 岁以上仅 12.5%",
                "数据来源：第二章 图表(后15).xlsx / 17 玉玦图")
    return save(fig, OUT, "17_玉玦图.png")


# --------------------------------------------------------------------------- 18
def chart_18_racetrack():
    """18 跑道图：180° 半环等长跑道，人数决定「跑」了多远。"""
    df = D.ch2("18_racetrack")
    labels = df["部门"].tolist()
    heads = df["人数"].astype(float).tolist()
    track = df["占位"].astype(float).tolist()  # 人数 + 占位 = 常量，即跑道全长

    fig, ax = _polar_axes()
    # 跑道全长 = 人数 + 占位（Excel 中为固定值 832）
    L = float(track[0] + heads[0])
    rmax, rmin = 1.0, 0.34
    n = len(labels)
    palette = [EXCEL_PALETTE[i % len(EXCEL_PALETTE)] for i in range(n)]

    # 底跑道
    for i in range(n):
        r = rmax - i * (rmax - rmin) / max(n - 1, 1)
        ax.add_patch(Wedge((0, 0), r, 180, 0, width=(rmax - rmin) / n * 0.62,
                           facecolor="#EFEFEF", edgecolor="white", linewidth=1))
    # 已跑过的弧
    for i, (lab, v) in enumerate(zip(labels, heads)):
        r = rmax - i * (rmax - rmin) / max(n - 1, 1)
        sweep = -v / L * 180
        ax.add_patch(Wedge((0, 0), r, 180, 180 + sweep,
                           width=(rmax - rmin) / n * 0.62,
                           facecolor=palette[i], edgecolor="white", linewidth=1))
        # 标签统一放在左下空白区（225° 方向），按半径依次排开，避免互相压盖
        ang = np.deg2rad(225)
        ax.text(1.24 * r * np.cos(ang), 1.24 * r * np.sin(ang),
                f"{lab}  {v:.0f}", ha="center", va="center", fontsize=10,
                color=palette[i], fontweight="bold")

    ax.text(0.92, -0.98, f"跑道全长 {L:.0f}", ha="right", fontsize=9.5,
            color=SUB_INK)
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.2, 1.25)
    title_block(fig, ax, "各部门人数跑道图",
                "销售部人数最多（451 人），人力部最少（130 人）",
                "数据来源：第二章 图表(后15).xlsx / 18 跑道图")
    return save(fig, OUT, "18_跑道图.png")


# --------------------------------------------------------------------------- 19
def chart_19_rose_pie():
    """19 南丁格尔圆饼图：扇区角度相等、半径随数值变化。"""
    df = D.ch2("19_rose_pie")
    labels = df["部门"].tolist()
    vals = df["人数占比"].astype(float).tolist()

    fig, ax = _polar_axes()
    _rose(ax, labels, vals, inner_r=0.0)
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    title_block(fig, ax, "各部门人数占比（南丁格尔圆饼图）",
                "销售部占比最高（29.2%），半径差异放大了部门间差距",
                "数据来源：第二章 图表(后15).xlsx / 19 南丁格尔圆饼图")
    return save(fig, OUT, "19_南丁格尔圆饼图.png")


# --------------------------------------------------------------------------- 20
def chart_20_rose_donut():
    """20 南丁格尔圆环图：玫瑰图 + 内圈留空，标签更透气。"""
    df = D.ch2("20_rose_donut")
    labels = df["年龄"].tolist()
    vals = df["人数占比"].astype(float).tolist()

    fig, ax = _polar_axes()
    _rose(ax, labels, vals, inner_r=0.34)
    ax.text(0, 0, "年龄结构", ha="center", va="center", fontsize=13,
            color=SUB_INK)
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    title_block(fig, ax, "员工年龄占比（南丁格尔圆环图）",
                "年龄段越年轻占比越高，30 岁以下接近四成",
                "数据来源：第二章 图表(后15).xlsx / 20 南丁格尔圆环图")
    return save(fig, OUT, "20_南丁格尔圆环图.png")


# --------------------------------------------------------------------------- 21
def chart_21_rose_ppt():
    """21 南丁格尔（PPT 版）：报告排版常用的精简玫瑰图。"""
    df = D.ch2("21_rose_ppt")
    labels = df["部门"].tolist()
    vals = df["人数占比"].astype(float).tolist()

    fig, ax = _polar_axes()
    palette = ["#2E5FA3", "#3F79C0", "#6C9BD8", "#9DBCE8", "#C6D9F1", "#E4ECF8"]
    _rose(ax, labels, vals, inner_r=0.28, palette=palette)
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    title_block(fig, ax, "各部门人数占比（PPT 配色版）",
                "同色系渐变配色，适合直接放进汇报材料",
                "数据来源：第二章 图表(后15).xlsx / 20 南丁格尔（PPT）")
    return save(fig, OUT, "21_南丁格尔_PPT.png")


# --------------------------------------------------------------------------- 22
def chart_22_gauge():
    """22 仪表盘图：半环刻度盘 + 指针，等价于 Excel 的饼图拼装仪表盘。"""
    meta = D.gauge_meta()
    value = float(meta.get("pointer_value", 76))
    lo, hi = float(meta.get("scale_start", 50)), float(meta.get("scale_end", 150))
    frac = np.clip((value - lo) / (hi - lo), 0, 1)

    fig, ax = _polar_axes()
    # 刻度盘：三段色（低 / 中 / 高）
    seg_colors = ["#E8EEF7", "#BDD3EC", EXCEL_PALETTE[0]]
    seg_bounds = [0, 0.4, 0.75, 1.0]
    for i in range(3):
        a0, a1 = 180 - seg_bounds[i] * 180, 180 - seg_bounds[i + 1] * 180
        ax.add_patch(Wedge((0, 0), 1.0, a1, a0, width=0.26,
                           facecolor=seg_colors[i], edgecolor="white",
                           linewidth=1.2))
    # 主刻度
    for i in range(0, 11):
        f = i / 10
        ang = np.deg2rad(180 - f * 180)
        ax.plot([0.74 * np.cos(ang), 0.80 * np.cos(ang)],
                [0.74 * np.sin(ang), 0.80 * np.sin(ang)],
                color="#9AA7B4", lw=1.1)
        ax.text(0.62 * np.cos(ang), 0.62 * np.sin(ang), f"{lo + f * (hi - lo):.0f}",
                ha="center", va="center", fontsize=8.5, color=SUB_INK)
    # 指针
    ang = np.deg2rad(180 - frac * 180)
    ax.annotate("", xy=(0.70 * np.cos(ang), 0.70 * np.sin(ang)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="#C0392B", lw=2.4,
                                shrinkA=0, shrinkB=0))
    ax.add_patch(Circle((0, 0), 0.055, facecolor="#C0392B",
                        edgecolor="white", linewidth=1.4, zorder=5))
    ax.text(0, -0.24, f"{value:.0f}", ha="center", va="center", fontsize=22,
            color=INK, fontweight="bold")
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-0.5, 1.2)
    title_block(fig, ax, "综合经营指标仪表盘",
                f"指针值 {value:.0f}，落在中高区间，尚未进入预警区",
                "数据来源：第二章 图表(后15).xlsx / 22 仪表盘图")
    return save(fig, OUT, "22_仪表盘图.png")


# --------------------------------------------------------------------------- 23
def chart_23_bar_line():
    """23 柱形折线图：柱表规模、线表增速，双轴组合的经典用法。"""
    df = D.ch2("23_bar_line")
    years = df["年份"].astype(int).astype(str).tolist()
    sales = df["销售量"].astype(float).tolist()
    yoy = df["同比"].astype(float).tolist()
    x = np.arange(len(years))

    fig, ax = new_axes()
    bars = ax.bar(x, sales, width=0.5, color=EXCEL_PALETTE[0])
    style_axes(ax)
    ax.set_ylim(0, max(sales) * 1.25)
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    value_labels(ax, bars)

    ax2 = ax.twinx()
    ax2.plot(x, yoy, marker="o", markersize=6, linewidth=2,
             color=EXCEL_PALETTE[1])
    ax2.set_ylim(0, max(yoy) * 1.6)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.tick_params(colors=SUB_INK, labelsize=10, length=0)
    ax2.set_yticklabels([pct(v) for v in ax2.get_yticks()])

    for i, v in enumerate(yoy):
        ax2.text(i, v + max(yoy) * 0.07, pct(v), ha="center", fontsize=9.5,
                 color=EXCEL_PALETTE[1])

    ax.text(0.01, 1.06, "销售量", transform=ax.transAxes, fontsize=10.5,
            color=EXCEL_PALETTE[0], fontweight="bold")
    ax.text(0.08, 1.06, "同比增速", transform=ax.transAxes, fontsize=10.5,
            color=EXCEL_PALETTE[1], fontweight="bold")
    title_block(fig, ax, "历年销售量与同比增速",
                "销售量连年增长，但增速自 2020 年起逐年放缓",
                "数据来源：第二章 图表(后15).xlsx / 23 柱形折线图")
    return save(fig, OUT, "23_柱形折线图.png")


# --------------------------------------------------------------------------- 24
def chart_24_target_bar():
    """24 目标柱形图：实际柱 + 目标刻度线，偏差一目了然。"""
    df = D.ch2("24_target_bar")
    labels = df["商品"].tolist()
    actual = df["实际销量"].astype(float).tolist()
    target = df["目标销量"].astype(float).tolist()
    x = np.arange(len(labels))

    fig, ax = new_axes()
    bars = ax.bar(x, actual, width=0.5, color=EXCEL_PALETTE[0])
    style_axes(ax)
    ax.set_ylim(0, max(max(actual), max(target)) * 1.25)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    for i, (a, t) in enumerate(zip(actual, target)):
        ok = a >= t
        ax.plot([i - 0.3, i + 0.3], [t, t],
                color="#C0392B" if not ok else "#2E7D32", lw=2.6, zorder=4)
        ax.text(i + 0.34, t, f"目标 {t}", fontsize=8.5, va="center",
                color="#C0392B" if not ok else "#2E7D32")
    value_labels(ax, bars, offset=0.03)

    legend_simple(ax, ["实际销量", "目标线"], [EXCEL_PALETTE[0], "#C0392B"])
    title_block(fig, ax, "各商品实际销量与目标对比",
                "面膜、隔离、面霜完成目标，口红、防晒、精华未达标",
                "数据来源：第二章 图表(后15).xlsx / 24 目标柱形图")
    return save(fig, OUT, "24_目标柱形图.png")


# --------------------------------------------------------------------------- 25
def chart_25_bullet():
    """25 子弹图：定性区间背景 + 实际值条 + 目标刻度，信息密度极高。"""
    df = D.ch2("25_bullet")
    labels = df["商品"].tolist()
    actual = df["实际"].astype(float).tolist()
    target = df["目标"].astype(float).tolist()
    ok = df["及格"].astype(float).tolist()
    good = df["良好"].astype(float).tolist()
    great = df["优秀"].astype(float).tolist()
    y = np.arange(len(labels))[::-1]
    span = (np.array(ok) + np.array(good) + np.array(great))

    fig, ax = new_axes(figsize=(10, 5.6), rect=(0.13, 0.14, 0.84, 0.72))
    # 三段定性背景
    ax.barh(y, ok, height=0.55, color="#E9EEF5", zorder=1)
    ax.barh(y, good, left=ok, height=0.55, color="#D3DEEC", zorder=1)
    ax.barh(y, great, left=np.array(ok) + np.array(good), height=0.55,
            color="#B7C9E4", zorder=1)
    # 实际值
    ax.barh(y, actual, height=0.24, color=EXCEL_PALETTE[0], zorder=3)
    # 目标刻度
    for i, (t, a) in enumerate(zip(target, actual)):
        ax.plot([t, t], [y[i] - 0.3, y[i] + 0.3], color=INK, lw=2.2, zorder=4)
        ax.text(a + 12, y[i], f"{a:,.0f}", va="center", fontsize=9.5,
                color=EXCEL_PALETTE[0], fontweight="bold")

    style_axes(ax, axis="x", grid=False)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, float(span.max()) * 1.02)
    legend_simple(ax, ["及格", "良好", "优秀", "实际值", "目标线"],
                  ["#E9EEF5", "#D3DEEC", "#B7C9E4", EXCEL_PALETTE[0], INK],
                  y=1.04, ncol=5)
    title_block(fig, ax, "各商品销量子弹图",
                "防晒进入优秀区间，面膜仍停留在及格区间",
                "数据来源：第二章 图表(后15).xlsx / 25 子弹图")
    return save(fig, OUT, "25_子弹图.png")


# --------------------------------------------------------------------------- 26
def chart_26_bar_circle():
    """26 柱形圆：柱形 + 顶部圆形端点，同比信息以圆内百分比呈现。"""
    df = D.ch2("26_bar_circle")
    labels = df["区域"].tolist()
    vals = df["销量"].astype(float).tolist()
    yoy = df["同比去年"].astype(float).tolist()
    x = np.arange(len(labels))

    fig, ax = new_axes(figsize=(9.8, 5.4))
    for i, v in enumerate(vals):
        rounded_bar(ax, i - 0.28, 0, 0.56, v, facecolor=EXCEL_PALETTE[0],
                    light_amount=0.6)
    style_axes(ax)
    ax.set_xlim(-0.7, len(labels) - 0.3)
    ax.set_ylim(0, max(vals) * 1.3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    for i, (v, g) in enumerate(zip(vals, yoy)):
        ax.scatter(i, v, s=560, color=EXCEL_PALETTE[1], edgecolor="white",
                   linewidths=2, zorder=4)
        ax.text(i, v, pct(g), ha="center", va="center", fontsize=9,
                color="white", fontweight="bold", zorder=5)
        ax.text(i, v * 0.5, f"{v:,.0f}", ha="center", va="center",
                fontsize=10.5, color="white", zorder=3)

    title_block(fig, ax, "各区域销量及同比",
                "圆内数字为同比增速，华东增速最高（25%）",
                "数据来源：第二章 图表(后15).xlsx / 26 柱形圆")
    return save(fig, OUT, "26_柱形圆.png")


# --------------------------------------------------------------------------- 27
def chart_27_cluster_bar_line():
    """27 簇状柱形折线图：两年销量并排柱 + 同比折线（副轴）。"""
    df = D.ch2("27_cluster_bar_line")
    labels = df["区域"].tolist()
    y2022 = df["2022销量"].astype(float).tolist()
    y2021 = df["2021销量"].astype(float).tolist()
    yoy = df["同比去年"].astype(float).tolist()
    x = np.arange(len(labels))

    fig, ax = new_axes()
    ax.bar(x - 0.19, y2022, width=0.36, color=EXCEL_PALETTE[0])
    ax.bar(x + 0.19, y2021, width=0.36, color=EXCEL_PALETTE[2])
    style_axes(ax)
    ax.set_ylim(0, max(max(y2022), max(y2021)) * 1.28)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax2 = ax.twinx()
    ax2.plot(x, yoy, marker="o", markersize=6, linewidth=2,
             color=EXCEL_PALETTE[1])
    ax2.set_ylim(0, max(yoy) * 2.2)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.tick_params(colors=SUB_INK, labelsize=10, length=0)
    ax2.set_yticks(ax2.get_yticks())
    ax2.set_yticklabels([pct(v) for v in ax2.get_yticks()])
    for i, v in enumerate(yoy):
        ax2.text(i, v + max(yoy) * 0.09, pct(v), ha="center", fontsize=9.5,
                 color=EXCEL_PALETTE[1])

    legend_simple(ax, ["2022年销量", "2021年销量", "同比增速"],
                  [EXCEL_PALETTE[0], EXCEL_PALETTE[2], EXCEL_PALETTE[1]],
                  y=1.04, ncol=3)
    title_block(fig, ax, "各区域销量两年对比与同比增速",
                "华南同比增速最高（22.0%），东北增速最低（10.0%）",
                "数据来源：第二章 图表(后15).xlsx / 27 簇状柱形折线图")
    return save(fig, OUT, "27_簇状柱形折线图.png")


# --------------------------------------------------------------------------- 28
def chart_28_composite_bar():
    """28 复合柱形图：月度柱 + 季度底柱，粒度不同的两层数据同图呈现。"""
    df = D.ch2("28_composite_bar")
    labels = df["月份"].tolist()
    month = df["月度销量"].astype(float).tolist()
    quarter = df["季度销量"].astype(float).tolist()
    x = np.arange(len(labels))

    fig, ax = new_axes(figsize=(10, 5.4))
    ax.bar(x, quarter, width=0.72, color="#DCE6F4", zorder=1)
    ax.bar(x, month, width=0.46, color=EXCEL_PALETTE[0], zorder=2)
    style_axes(ax)
    ax.set_ylim(0, max(quarter) * 1.22)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    for i in range(len(labels)):
        if i == 0 or quarter[i] != quarter[i - 1]:
            ax.text(i, quarter[i] + max(quarter) * 0.03, f"Q{i // 3 + 1} 合计 {quarter[i]:,.0f}",
                    ha="left", fontsize=9, color=SUB_INK)

    legend_simple(ax, ["季度销量", "月度销量"], ["#DCE6F4", EXCEL_PALETTE[0]],
                  y=1.04, ncol=2)
    title_block(fig, ax, "月度销量与季度销量复合对比",
                "三季度合计 9673 为全年最高，9 月单月 3621 亦为月度峰值",
                "数据来源：第二章 图表(后15).xlsx / 28 复合柱形图")
    return save(fig, OUT, "28_复合柱形图.png")


# --------------------------------------------------------------------------- 29
def chart_29_sliding_bead():
    """29 滑珠图：轨道条上放一颗「珠子」，位置即完成率。"""
    df = D.ch2("29_sliding_bead")
    labels = df["区域"].tolist()
    rate = df["完成率"].astype(float).tolist()
    y = np.arange(len(labels))[::-1]

    fig, ax = new_axes(figsize=(9.4, 5.2), rect=(0.12, 0.14, 0.84, 0.72))
    ax.barh(y, [1.0] * len(rate), height=0.16, color="#E6E6E6", zorder=1)
    ax.barh(y, rate, height=0.16, color="#F5F5F5", zorder=2)
    ax.scatter(rate, y, s=420, color=EXCEL_PALETTE[0], edgecolor="white",
               linewidths=2, zorder=4)
    style_axes(ax, axis="x", grid=False)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 1.02)
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.set_xticklabels([pct(v) for v in np.linspace(0, 1, 6)])

    for i, v in enumerate(rate):
        ax.text(v, y[i] + 0.26, pct(v), ha="center", fontsize=10,
                color=EXCEL_PALETTE[0], fontweight="bold")

    title_block(fig, ax, "各区域完成率滑珠图",
                "华南完成率 86.0% 最高，华东 35.0% 最低",
                "数据来源：第二章 图表(后15).xlsx / 29 滑珠图")
    return save(fig, OUT, "29_滑珠图.png")


# --------------------------------------------------------------------------- 30
def chart_30_compare_bead():
    """30 对比滑珠图：一条轨道放两颗珠子，直接比较两年完成率。"""
    df = D.ch2("30_compare_bead")
    labels = df["区域"].tolist()
    r22 = df["2022完成率"].astype(float).tolist()
    r21 = df["2021完成率"].astype(float).tolist()
    y = np.arange(len(labels))[::-1]

    fig, ax = new_axes(figsize=(9.6, 5.4), rect=(0.12, 0.14, 0.84, 0.72))
    ax.barh(y, [1.0] * len(r22), height=0.2, color="#E6E6E6", zorder=1)
    ax.barh(y, r22, height=0.2, color="#EDF2F9", zorder=2)
    ax.scatter(r21, y, s=340, color="#BFBFBF", edgecolor="white", linewidths=2,
               zorder=4, label="2021年")
    ax.scatter(r22, y, s=340, color=EXCEL_PALETTE[0], edgecolor="white",
               linewidths=2, zorder=5, label="2022年")
    style_axes(ax, axis="x", grid=False)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 1.02)
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.set_xticklabels([pct(v) for v in np.linspace(0, 1, 6)])

    for i, (a, b) in enumerate(zip(r21, r22)):
        ax.text(a, y[i] + 0.3, pct(a), ha="center", fontsize=9, color="#8C8C8C")
        ax.text(b, y[i] - 0.32, pct(b), ha="center", fontsize=9,
                color=EXCEL_PALETTE[0], fontweight="bold")

    legend_simple(ax, ["2021年", "2022年"], ["#BFBFBF", EXCEL_PALETTE[0]],
                  y=1.04, ncol=2)
    title_block(fig, ax, "各区域两年完成率对比滑珠图",
                "华南、西北、东北、华北 2022 年提升，华东出现回落",
                "数据来源：第二章 图表(后15).xlsx / 30 对比滑珠图")
    return save(fig, OUT, "30_对比滑珠图.png")


CHARTS = [
    chart_16_wave_liquid, chart_17_jade_ring, chart_18_racetrack,
    chart_19_rose_pie, chart_20_rose_donut, chart_21_rose_ppt,
    chart_22_gauge, chart_23_bar_line, chart_24_target_bar,
    chart_25_bullet, chart_26_bar_circle, chart_27_cluster_bar_line,
    chart_28_composite_bar, chart_29_sliding_bead, chart_30_compare_bead,
]


def run_all():
    return [fn() for fn in CHARTS]


if __name__ == "__main__":
    for p in run_all():
        print(p)
