# -*- coding: utf-8 -*-
"""
数据加载层
==========

所有图表都从 ``data/*.csv`` 读数据，仓库自带快照，克隆即用。
若想从原书 Excel 重新抽取，运行::

    python scripts/extract_source_data.py --source-dir <原始Excel目录>
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd

from .theme import DATA_DIR


def _csv(name: str, **kwargs) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"缺少数据文件 {path}。请先运行 scripts/extract_source_data.py "
            f"从原始 Excel 抽取数据。")
    return pd.read_csv(path, **kwargs)


def _json(name: str):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- 第二章
@lru_cache(maxsize=None)
def ch2(name: str) -> pd.DataFrame:
    """按图表编号取第二章小表，例如 ch2('01_gradient_bar')。"""
    return _csv(f"ch2_{name}.csv")


def gauge_meta() -> dict:
    """仪表盘图的刻度范围与指针值。"""
    return _json("ch2_22_gauge_meta.json")


# --------------------------------------------------------------------------- 第三章
@lru_cache(maxsize=None)
def ch3(name: str) -> pd.DataFrame:
    return _csv(f"ch3_{name}.csv")


def racetrack_note() -> dict:
    """动态跑道图每期对应的公司总人数说明。"""
    try:
        return _json("ch3_02_racetrack_note.json")
    except FileNotFoundError:
        return {}


# --------------------------------------------------------------------------- 第四章
@lru_cache(maxsize=None)
def hr_base() -> pd.DataFrame:
    """2022年3月人员基础信息（1470 人，员工编号已脱敏为 E000001 形式）。"""
    return _csv("ch4_hr_base.csv")


@lru_cache(maxsize=None)
def sales_detail() -> pd.DataFrame:
    """销售明细（8564 条订单）。"""
    df = _csv("ch4_sales_detail.csv", parse_dates=["订单日期"])
    return df


@lru_cache(maxsize=None)
def cost_detail() -> pd.DataFrame:
    """成本明细（48 行：12 个月 × 4 类成本）。"""
    return _csv("ch4_cost_detail.csv")


# --------------------------------------------------------------------------- 汇总计算
def hr_summary() -> dict:
    """
    人力资源看板需要的 6 组汇总。

    对应原工作簿里 6 张图：年龄 / 婚姻状况 / 入转调 / 性别 / 学历 / 部门。
    """
    df = hr_base()
    return {
        "总人数": len(df),
        "年龄": df["年龄段"].value_counts().reindex(
            ["18-24", "25-29", "30-34", "35-39", "40=<"]).fillna(0).astype(int),
        "婚姻状况": df["婚姻状况"].value_counts(),
        "入转调": df["本月入转调"].dropna().value_counts(),
        "性别": df["性别"].value_counts(),
        "学历": df["学历"].value_counts().reindex(
            ["专科以下", "专科", "本科", "硕士研究生", "博士研究生"]).fillna(0).astype(int),
        "部门": df["部门"].value_counts(),
        "平均年龄": round(df["年龄"].mean(), 1),
    }


def sales_summary() -> dict:
    """
    销售大屏需要的 8 组汇总。

    对应原工作簿 11 张图：快递公司销量 / 区域销量 / 销量环比 /
    各月销售额 / 产品类别销量 / 商品销售额 Top3 / 利润额占比 等。
    """
    df = sales_detail()
    cost = cost_detail()

    month_order = [f"{i}月" for i in range(1, 13)]
    monthly = df.groupby("月份_销售")["订单额"].sum().reindex(month_order).fillna(0)

    by_express = df["快递公司"].value_counts()
    by_region = df.groupby("区域")["订单额"].sum().sort_values(ascending=False)
    by_category = df["产品类别"].value_counts()
    top_product = (df.groupby("产品名称")["订单额"].sum()
                   .sort_values(ascending=False).head(3))

    profit = df["利润额"].sum()
    amount = df["订单额"].sum()

    return {
        "订单数": len(df),
        "销售额": amount,
        "利润额": profit,
        "利润率": profit / amount if amount else 0,
        "月度销售额": monthly,
        "快递公司销量": by_express,
        "区域销售额": by_region,
        "产品类别销量": by_category,
        "商品Top3": top_product,
        "成本": cost,
        "利润占比": profit / amount if amount else 0,
    }
