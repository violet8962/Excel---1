# -*- coding: utf-8 -*-
"""
第四章 · 可视化看板 / 数据大屏
==============================

复现原书第四章的两个看板：

* ``hr_dashboard``    人力资源可视化看板（浅色，1470 人明细驱动）
* ``sales_dashboard`` 销售数据大屏（深色，8564 条订单明细驱动）

Excel 里靠「多图表排版 + 隐藏网格线 + 形状打底」拼出大屏；
Python 里用 GridSpec 网格布局 + 统一深色主题一次成型，
所有指标都直接从明细数据实时聚合，改数据即可复用。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge

from . import data as D
from .theme import (
    DARK_ACCENT, DARK_BG, DARK_PANEL, DARK_TEXT, OUTPUT_DIR,
)

# 浅色看板配色（人力资源看板）
LIGHT_BG = "#F4F6FA"
PANEL_BG = "white"
INK = "#2F2F2F"
SUB = "#7A7A7A"


def _fmt_wan(v: float) -> str:
    """大数缩写：1342887 -> '134.3万'。"""
    if abs(v) >= 1e8:
        return f"{v / 1e8:.2f}亿"
    if abs(v) >= 1e4:
        return f"{v / 1e4:.1f}万"
    return f"{v:,.0f}"


# ===========================================================================
# 一、人力资源可视化看板（浅色）
# ===========================================================================
def _panel(fig, spec, bg=PANEL_BG):
    ax = fig.add_subplot(spec)
    ax.set_facecolor(bg)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=SUB, labelsize=9, length=0)
    return ax


def _donut(ax, series, colors, title, *, center_top="", center_bottom="",
           label_outside=False):
    """圆环图：Excel 看板里最常用的占比表达。"""
    labels = list(series.index)
    vals = list(series.values.astype(float))
    total = sum(vals) or 1
    ax.set_aspect("equal")
    start = 90.0
    for i, v in enumerate(vals):
        sweep = -v / total * 360
        ax.add_patch(Wedge((0, 0), 1.0, start + sweep, start, width=0.34,
                           facecolor=colors[i % len(colors)],
                           edgecolor="white", linewidth=1.4))
        mid = np.deg2rad(start + sweep / 2)
        if v / total >= 0.05:
            ax.text(0.83 * np.cos(mid), 0.83 * np.sin(mid),
                    f"{v / total * 100:.0f}%", ha="center", va="center",
                    fontsize=8.5, color="white", fontweight="bold")
        if label_outside:
            ax.text(1.22 * np.cos(mid), 1.22 * np.sin(mid), labels[i],
                    ha="center", va="center", fontsize=9, color=INK)
        start += sweep
    ax.text(0, 0.12, center_top, ha="center", va="center", fontsize=17,
            color=INK, fontweight="bold")
    ax.text(0, -0.2, center_bottom, ha="center", va="center", fontsize=9,
            color=SUB)
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.3, 1.3)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=11.5, color=INK, fontweight="bold", pad=8)


def _bars(ax, series, colors, title, horizontal=False, fmt="{:,.0f}"):
    labels = list(series.index)
    vals = list(series.values.astype(float))
    y = np.arange(len(labels))
    if horizontal:
        ax.barh(y, vals, height=0.55, color=colors[0])
        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        vmax = max(vals) or 1
        ax.set_xlim(0, vmax * 1.22)
        for i, v in enumerate(vals):
            ax.text(v + vmax * 0.02, i, fmt.format(v), va="center",
                    fontsize=8.5, color=INK)
    else:
        ax.bar(y, vals, width=0.55, color=colors[0])
        ax.set_xticks(y)
        ax.set_xticklabels(labels, fontsize=8.5)
        vmax = max(vals) or 1
        ax.set_ylim(0, vmax * 1.2)
        for i, v in enumerate(vals):
            ax.text(i, v + vmax * 0.03, fmt.format(v), ha="center",
                    fontsize=8.5, color=INK)
    ax.set_title(title, fontsize=11.5, color=INK, fontweight="bold", pad=8)


def hr_dashboard() -> str:
    """人力资源可视化看板：6 个图表 + 4 个 KPI 卡片。"""
    s = D.hr_summary()
    acc = ["#4472C4", "#5B9BD5", "#8FAADC", "#B4C7E7", "#D9E2F3"]

    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor=LIGHT_BG)
    gs = fig.add_gridspec(3, 6, left=0.045, right=0.965, top=0.86,
                          bottom=0.06, wspace=0.45, hspace=0.65)

    # ---- 标题条 -----------------------------------------------------------
    fig.text(0.045, 0.955, "人力资源可视化看板", fontsize=22, color=INK,
             fontweight="bold")
    fig.text(0.045, 0.915, "数据截至 2022 年 3 月  ·  样本 1,470 人",
             fontsize=11, color=SUB)
    fig.add_artist(plt.Rectangle((0, 0.90), 1, 0.0015, transform=fig.transFigure,
                                 color="#D0D7E2"))

    # ---- KPI 卡片 ---------------------------------------------------------
    kpis = [
        ("总人数", f"{s['总人数']:,}", "人"),
        ("平均年龄", f"{s['平均年龄']}", "岁"),
        ("本月入职", f"{int(s['入转调'].get('入职', 0))}", "人"),
        ("男女比", (f"{s['性别'].get('男', 0) / max(s['性别'].get('女', 1), 1):.2f}"),
         "男 : 女"),
    ]
    for i, (name, val, unit) in enumerate(kpis):
        ax = _panel(fig, gs[0, i])
        # 用表格单元格画 KPI 卡片
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.add_patch(plt.Rectangle((0.02, 0.05), 0.96, 0.9,
                                   transform=ax.transAxes, facecolor=PANEL_BG,
                                   edgecolor="#E1E6EE", linewidth=1,
                                   zorder=0, clip_on=False))
        ax.text(0.5, 0.72, name, ha="center", fontsize=10.5, color=SUB)
        ax.text(0.5, 0.42, val, ha="center", fontsize=22, color="#2F5597",
                fontweight="bold")
        ax.text(0.5, 0.14, unit, ha="center", fontsize=9, color=SUB)
        ax.set_xticks([])
        ax.set_yticks([])

    # ---- 六个图表 ---------------------------------------------------------
    ax1 = _panel(fig, gs[1, 0:2])
    _donut(ax1, s["年龄"], acc, "年龄结构", center_top=f"{s['平均年龄']}",
           center_bottom="平均年龄(岁)", label_outside=True)

    ax2 = _panel(fig, gs[1, 2:4])
    _donut(ax2, s["婚姻状况"], ["#4472C4", "#ED7D31", "#A5A5A5"], "婚姻状况",
           center_top=f"{s['婚姻状况'].get('已婚', 0) / s['总人数'] * 100:.0f}%",
           center_bottom="已婚占比", label_outside=True)

    ax3 = _panel(fig, gs[1, 4:6])
    _donut(ax3, s["性别"], ["#5B9BD5", "#F4B183"], "性别结构",
           center_top=f"{s['性别'].get('男', 0) / s['总人数'] * 100:.0f}%",
           center_bottom="男性占比", label_outside=True)

    ax4 = _panel(fig, gs[2, 0:2])
    _bars(ax4, s["部门"], ["#4472C4"], "各部门人数", horizontal=True)

    ax5 = _panel(fig, gs[2, 2:4])
    _bars(ax5, s["学历"], ["#5B9BD5"], "学历分布", horizontal=True)

    ax6 = _panel(fig, gs[2, 4:6])
    it = s["入转调"]
    _bars(ax6, it, ["#ED7D31"], "本月入转调", horizontal=True)

    out = OUTPUT_DIR / "ch4" / "人力资源可视化看板.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor=LIGHT_BG, bbox_inches="tight")
    plt.close(fig)
    return str(out)


# ===========================================================================
# 二、销售数据大屏（深色）
# ===========================================================================
def _dark_ax(fig, spec):
    ax = fig.add_subplot(spec)
    ax.set_facecolor(DARK_PANEL)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors="#7E93A8", labelsize=8.5, length=0)
    ax.grid(axis="y", color="#1E3A55", linewidth=0.8)
    ax.set_axisbelow(True)
    return ax


def _dark_donut(ax, series, colors, title):
    labels = list(series.index)
    vals = list(series.values.astype(float))
    total = sum(vals) or 1
    ax.set_aspect("equal")
    start = 90.0
    for i, v in enumerate(vals):
        sweep = -v / total * 360
        ax.add_patch(Wedge((0, 0), 1.0, start + sweep, start, width=0.34,
                           facecolor=colors[i % len(colors)], edgecolor=DARK_PANEL,
                           linewidth=2))
        mid = np.deg2rad(start + sweep / 2)
        if v / total >= 0.04:
            ax.text(0.82 * np.cos(mid), 0.82 * np.sin(mid),
                    f"{v / total * 100:.0f}%", ha="center", va="center",
                    fontsize=8.5, color=DARK_TEXT, fontweight="bold")
        ax.text(1.26 * np.cos(mid), 1.26 * np.sin(mid), labels[i], ha="center",
                va="center", fontsize=8.5, color="#9FB3C8")
        start += sweep
    ax.text(0, 0.1, f"{total:,.0f}", ha="center", va="center", fontsize=16,
            color=DARK_TEXT, fontweight="bold")
    ax.text(0, -0.24, "合计", ha="center", va="center", fontsize=9,
            color="#7E93A8")
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.35, 1.35)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=11, color=DARK_TEXT, fontweight="bold", pad=6)


def _dark_bar(ax, series, color, title, horizontal=False, fmt="{:,.0f}",
              fmt_fn=None):
    labels = list(series.index)
    vals = list(series.values.astype(float))
    y = np.arange(len(labels))
    if horizontal:
        ax.barh(y, vals, height=0.55, color=color)
        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.grid(axis="x", color="#1E3A55", linewidth=0.8)
        ax.grid(axis="y", visible=False)
        vmax = max(vals) or 1
        ax.set_xlim(0, vmax * 1.25)
        for i, v in enumerate(vals):
            ax.text(v + vmax * 0.02, i, (fmt_fn or fmt.format)(v), va="center", fontsize=8.5,
                    color=DARK_TEXT)
        ax.invert_yaxis()
    else:
        ax.bar(y, vals, width=0.5, color=color)
        ax.set_xticks(y)
        ax.set_xticklabels(labels, fontsize=8.5)
        vmax = max(vals) or 1
        ax.set_ylim(0, vmax * 1.2)
        for i, v in enumerate(vals):
            ax.text(i, v + vmax * 0.03, (fmt_fn or fmt.format)(v), ha="center", fontsize=8.5,
                    color=DARK_TEXT)
    ax.set_title(title, fontsize=11, color=DARK_TEXT, fontweight="bold", pad=6)


def sales_dashboard() -> str:
    """销售数据大屏：KPI + 7 个图表，深色大屏风格。"""
    s = D.sales_summary()
    acc = DARK_ACCENT

    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor=DARK_BG)
    gs = fig.add_gridspec(4, 12, left=0.035, right=0.972, top=0.87,
                          bottom=0.05, wspace=0.55, hspace=0.75)

    # ---- 标题条 -----------------------------------------------------------
    fig.text(0.035, 0.955, "销 售 数 据 大 屏", fontsize=24, color=DARK_TEXT,
             fontweight="bold")
    fig.text(0.035, 0.915, f"订单 {s['订单数']:,} 条  ·  数据期间 2021-10 ~ 2022-09",
             fontsize=11, color="#7E93A8")
    fig.add_artist(plt.Rectangle((0, 0.905), 1, 0.0018,
                                 transform=fig.transFigure, color="#1E3A55"))

    # ---- KPI 行 -----------------------------------------------------------
    kpis = [
        ("销售额", _fmt_wan(s["销售额"]), "元", acc[0]),
        ("利润额", _fmt_wan(s["利润额"]), "元", acc[1]),
        ("利润率", f"{s['利润率'] * 100:.1f}%", "", acc[2]),
        ("订单数", f"{s['订单数']:,}", "单", acc[3]),
    ]
    for i, (name, val, unit, color) in enumerate(kpis):
        ax = fig.add_subplot(gs[0, i * 3:i * 3 + 3])
        ax.set_facecolor(DARK_PANEL)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.add_patch(plt.Rectangle((0.0, 0.0), 0.006, 1, transform=ax.transAxes,
                                   facecolor=color, linewidth=0, clip_on=False))
        ax.text(0.08, 0.68, name, ha="left", fontsize=10.5, color="#7E93A8")
        ax.text(0.08, 0.34, val, ha="left", fontsize=21, color=DARK_TEXT,
                fontweight="bold")
        ax.text(0.62, 0.36, unit, ha="left", fontsize=9, color="#7E93A8")

    # ---- 中部：月度销售额（面积）+ 销量环比 --------------------------------
    monthly = s["月度销售额"]
    ax_area = _dark_ax(fig, gs[1, 0:5])
    x = np.arange(len(monthly))
    ax_area.fill_between(x, monthly.values, color=acc[0], alpha=0.28)
    ax_area.plot(x, monthly.values, color=acc[0], linewidth=2, marker="o",
                 markersize=4)
    ax_area.set_xticks(x)
    ax_area.set_xticklabels(monthly.index, fontsize=8)
    ax_area.set_ylim(0, monthly.max() * 1.3)
    from matplotlib.ticker import FuncFormatter
    ax_area.yaxis.set_major_formatter(
        FuncFormatter(lambda v, _p: _fmt_wan(v)))
    for i, v in enumerate(monthly.values):
        ax_area.text(i, v + monthly.max() * 0.06, _fmt_wan(v), ha="center",
                     fontsize=7.5, color="#9FB3C8")
    ax_area.set_title("各月销售额（元）", fontsize=11, color=DARK_TEXT,
                      fontweight="bold", pad=6)

    # 销量环比 = 每月订单量的环比变化
    cnt = s["月度销售额"].copy()
    ax_mom = _dark_ax(fig, gs[1, 5:9])
    orders = D.sales_detail().groupby("月份_销售")["订单单号"].count() \
        .reindex(monthly.index).fillna(0)
    mom = orders.pct_change().fillna(0)
    colors = ["#7CE38B" if v >= 0 else "#FF6B8B" for v in mom.values]
    ax_mom.bar(x, mom.values * 100, width=0.55, color=colors)
    ax_mom.axhline(0, color="#3C5A78", lw=1)
    ax_mom.set_xticks(x)
    ax_mom.set_xticklabels(monthly.index, fontsize=8)
    ax_mom.set_ylim(-abs(mom.values * 100).max() * 1.6,
                    abs(mom.values * 100).max() * 1.7)
    ax_mom.set_title("订单量环比（%）", fontsize=11, color=DARK_TEXT,
                     fontweight="bold", pad=6)
    for i, v in enumerate(mom.values * 100):
        ax_mom.text(i, v + (2 if v >= 0 else -6), f"{v:+.0f}%", ha="center",
                    fontsize=7.5, color="#9FB3C8")

    # 利润额占比（圆环仪表）
    ax_pr = fig.add_subplot(gs[1, 9:12])
    ax_pr.set_facecolor(DARK_PANEL)
    ax_pr.set_aspect("equal")
    rate = np.clip(s["利润率"], 0, 1)
    ax_pr.add_patch(Wedge((0, 0), 1.0, 180, 0, width=0.26, facecolor="#1E3A55",
                          edgecolor=DARK_PANEL, linewidth=2))
    ax_pr.add_patch(Wedge((0, 0), 1.0, 180 - rate * 180, 180, width=0.26,
                          facecolor=acc[1], edgecolor=DARK_PANEL, linewidth=2))
    ax_pr.text(0, 0.12, f"{rate * 100:.1f}%", ha="center", va="center",
               fontsize=19, color=DARK_TEXT, fontweight="bold")
    ax_pr.text(0, -0.22, "利润率", ha="center", va="center", fontsize=9,
               color="#7E93A8")
    ax_pr.set_xlim(-1.3, 1.3)
    ax_pr.set_ylim(-0.5, 1.15)
    ax_pr.set_xticks([])
    ax_pr.set_yticks([])
    for sp in ax_pr.spines.values():
        sp.set_visible(False)
    ax_pr.set_title("利润额占比销售额", fontsize=11, color=DARK_TEXT,
                    fontweight="bold", pad=6)

    # ---- 下部：四个分布图 --------------------------------------------------
    ax_e = _dark_ax(fig, gs[2:, 0:3])
    _dark_bar(ax_e, s["快递公司销量"], acc[0], "快递公司销量")

    ax_r = _dark_ax(fig, gs[2:, 3:6])
    _dark_bar(ax_r, s["区域销售额"], acc[1], "区域销售额", fmt_fn=_fmt_wan)

    ax_c = fig.add_subplot(gs[2:, 6:9])
    ax_c.set_facecolor(DARK_PANEL)
    _dark_donut(ax_c, s["产品类别销量"], acc[:3], "产品类别销量")

    ax_t = _dark_ax(fig, gs[2:, 9:12])
    _dark_bar(ax_t, s["商品Top3"].sort_values(), acc[2], "商品销售额 Top3",
              fmt_fn=_fmt_wan)

    out = OUTPUT_DIR / "ch4" / "销售数据大屏.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor=DARK_BG, bbox_inches="tight")
    plt.close(fig)
    return str(out)


CHARTS = [hr_dashboard, sales_dashboard]


def run_all():
    return [fn() for fn in CHARTS]


if __name__ == "__main__":
    for p in run_all():
        print(p)
