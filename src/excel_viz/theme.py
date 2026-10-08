# -*- coding: utf-8 -*-
"""
统一主题与通用绘图组件
====================

把原书 Excel 里的图表修饰套路沉淀成可复用的 Python 组件：

* ``setup_font``      —— 自动挑选可用的中文字体（Windows / macOS / Linux 通吃）
* ``EXCEL_PALETTE``   —— Excel 2016+ 默认主题配色，保证复现图与原书同色系
* ``gradient_bars``   —— 渐变填充柱形（对应「渐变柱形图」的渐变填充效果）
* ``rounded_bar``     —— 圆角柱形（对应「渐变圆角柱形图」）
* ``title_block``     —— 一级标题 / 二级标题 / 备注 三段式标题（原书强调的规范）
* ``style_axes``      —— 删除非必要元素：去掉默认标题、四边框、网格线重绘
* ``save``            —— 统一输出 png

原书在 P19 总结的柱形图修饰三步法：
    一、删除非必要元素  二、添加必要元素  三、修饰图表元素
本模块就是这三步法的代码化实现。
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib

# 无显示器环境（CI / 服务器）下必须切换 Agg 后端
if os.environ.get("EXCEL_VIZ_SHOW") != "1":
    matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, to_rgb  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

# --------------------------------------------------------------------------- 路径
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"

# --------------------------------------------------------------------------- 配色
# Excel 2016 及以后版本的默认「Office 主题」色板，顺序与 Excel 取色一致
EXCEL_PALETTE = [
    "#4472C4",  # 蓝
    "#ED7D31",  # 橙
    "#A5A5A5",  # 灰
    "#FFC000",  # 黄
    "#5B9BD5",  # 浅蓝
    "#70AD47",  # 绿
    "#264478",  # 深蓝
    "#9E480E",  # 深橙
    "#636363",  # 深灰
    "#997300",  # 深黄
]

# 大屏专用深色底配色
DARK_BG = "#0B1B2B"
DARK_PANEL = "#13263B"
DARK_TEXT = "#E8F1F8"
DARK_ACCENT = ["#00D2FF", "#FFB547", "#7CE38B", "#FF6B8B", "#C792EA", "#FFD166"]

INK = "#2F2F2F"      # 主文本
SUB_INK = "#6B6B6B"  # 次级文本
GRID = "#D9D9D9"     # 网格线

DPI = 150


# --------------------------------------------------------------------------- 字体
#: 按优先级尝试的中文字体；找不到就退到 matplotlib 默认字体并给出提示
CJK_CANDIDATES = [
    "Microsoft YaHei", "微软雅黑",
    "SimHei", "黑体",
    "Noto Sans CJK SC", "Source Han Sans SC", "WenQuanYi Zen Hei",
    "PingFang SC", "Hiragino Sans GB",
    "SimSun", "宋体",
]


def setup_font() -> str:
    """挑选系统里第一个可用的中文字体，返回实际使用的字体名。"""
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in CJK_CANDIDATES:
        if name in available:
            plt.rcParams["font.sans-serif"] = [name]
            break
    else:
        plt.rcParams["font.sans-serif"] = CJK_CANDIDATES[:1]
        print("[warn] 未找到中文字体，中文可能显示为方块；"
              "请安装 Microsoft YaHei / Noto Sans CJK SC 等字体。")
    # 负号必须单独处理，否则中文字体下会渲染成方块
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.size"] = 11
    plt.rcParams["axes.titlesize"] = 13
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["savefig.facecolor"] = "white"
    return plt.rcParams["font.sans-serif"][0]


setup_font()


# --------------------------------------------------------------------------- 颜色工具
def _mix(color: str, target: tuple[float, float, float], amount: float) -> tuple:
    r, g, b = to_rgb(color)
    tr, tg, tb = target
    return (r + (tr - r) * amount,
            g + (tg - g) * amount,
            b + (tb - b) * amount)


def lighten(color: str, amount: float = 0.35) -> tuple:
    """把颜色往白色方向调亮，amount 越大越亮。"""
    return _mix(color, (1.0, 1.0, 1.0), amount)


def darken(color: str, amount: float = 0.35) -> tuple:
    """把颜色往黑色方向调暗。"""
    return _mix(color, (0.0, 0.0, 0.0), amount)


def vcmap(color: str, light_amount: float = 0.55) -> LinearSegmentedColormap:
    """由单色生成竖向渐变色表（底部深色 -> 顶部浅色）。"""
    return LinearSegmentedColormap.from_list(
        "grad", [to_rgb(color), lighten(color, light_amount)])


# --------------------------------------------------------------------------- 画布
def new_axes(figsize=(9, 5.2), rect=(0.10, 0.14, 0.86, 0.72)):
    """创建「图表区」+「绘图区」双层结构，模拟 Excel 的图表区/绘图区划分。"""
    fig = plt.figure(figsize=figsize, dpi=DPI)
    ax = fig.add_axes(rect)
    return fig, ax


def style_axes(ax, *, grid: bool = True, axis: str = "y",
               spines: bool = False, tick_color: str = SUB_INK) -> None:
    """
    修饰坐标轴：去掉四边框（Excel 里去掉默认边框的做法），
    改用淡色横向网格线，让数据本身成为视觉主体。
    """
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(spines)
    ax.tick_params(colors=tick_color, labelsize=10, length=0)
    if grid:
        ax.set_axisbelow(True)
        ax.grid(axis=axis, color=GRID, linewidth=0.8, alpha=0.75)
    else:
        ax.grid(False)


def title_block(fig, ax, main: str, sub: str = "", note: str = "") -> None:
    """
    三段式标题：一级标题（主题）/ 二级标题（结论）/ 备注（口径与数据来源）。

    对应原书 P19：删除 Excel 默认标题，改用文本框补一二级标题与备注。
    """
    fig.text(ax.get_position().x0, 0.945, main,
             fontsize=17, fontweight="bold", color=INK, va="top")
    if sub:
        fig.text(ax.get_position().x0, 0.895, sub,
                 fontsize=11.5, color=SUB_INK, va="top")
    if note:
        fig.text(ax.get_position().x0, 0.035, note,
                 fontsize=9, color="#9A9A9A", va="bottom")


def save(fig, *parts: str, dpi: int = DPI) -> Path:
    """保存图片到 output/ 下的指定子目录，返回文件路径。"""
    path = OUTPUT_DIR.joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


# --------------------------------------------------------------------------- 柱形修饰
def gradient_bars(ax, bars, colors=None, light_amount: float = 0.6) -> None:
    """
    给柱形做渐变填充（Excel 的「渐变填充」效果）。

    做法：柱形本身设为透明，再在其裁剪区域内叠一张竖向往上的渐变图。
    """
    if colors is None:
        colors = [EXCEL_PALETTE[0]] * len(bars)
    if isinstance(colors, str):
        colors = [colors] * len(bars)

    for bar, color in zip(bars, colors):
        bar.set_facecolor("none")
        bar.set_edgecolor("none")
        bar.set_linewidth(0)
        x, y = bar.get_xy()
        w, h = bar.get_width(), bar.get_height()
        if h == 0:
            continue
        grad = np.linspace(0, 1, 256).reshape(-1, 1)
        im = ax.imshow(grad, extent=[x, x + w, y, y + h], aspect="auto",
                       cmap=vcmap(color, light_amount), origin="lower",
                       zorder=bar.get_zorder() + 0.1, interpolation="bicubic")
        im.set_clip_path(bar)


def rounded_bar(ax, x, y, width, height, *, radius=None, facecolor="#4472C4",
                gradient=True, light_amount=0.6, edgecolor="none", zorder=2):
    """
    圆角柱形：用 FancyBboxPatch 模拟 Excel 里「圆角矩形形状填充」的柱子。
    半径默认取柱宽的 1/4，且不会超过柱高的一半。
    """
    if radius is None:
        radius = min(width / 4, height / 2, 0.28)
    patch = FancyBboxPatch(
        (x, y), width, height,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        linewidth=0.8, edgecolor=edgecolor, facecolor="none",
        transform=ax.transData, zorder=zorder,
        mutation_aspect=1,
    )
    ax.add_patch(patch)
    if gradient and height > 0:
        grad = np.linspace(0, 1, 256).reshape(-1, 1)
        im = ax.imshow(grad, extent=[x, x + width, y, y + height], aspect="auto",
                       cmap=vcmap(facecolor, light_amount), origin="lower",
                       zorder=zorder + 0.1, interpolation="bicubic")
        im.set_clip_path(patch)
    else:
        patch.set_facecolor(facecolor)
    return patch


def value_labels(ax, bars, fmt="{:,.0f}", offset=0.02, color=INK, fontsize=10):
    """在柱顶标注数值（Excel 的「数据标签」）。"""
    yspan = ax.get_ylim()[1] - ax.get_ylim()[0]
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + yspan * offset,
                fmt.format(h), ha="center", va="bottom",
                color=color, fontsize=fontsize)


def legend_simple(ax, labels, colors, loc="upper center", ncol=None,
                  frameon=False, y=1.02):
    """轻量图例：用色块代理，避免默认图例边框破坏版面。"""
    handles = [Rectangle((0, 0), 1, 1, color=c, linewidth=0) for c in colors]
    ncol = ncol or len(labels)
    return ax.legend(handles, labels, loc=loc, ncol=ncol, frameon=frameon,
                     bbox_to_anchor=(0.5, y), fontsize=10, handlelength=1.4,
                     columnspacing=1.6)


def pct(x: float) -> str:
    """0.1234 -> '12.3%'"""
    return f"{x * 100:.1f}%"
