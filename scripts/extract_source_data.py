# -*- coding: utf-8 -*-
"""
从原书配套 Excel 中抽取原始数据，固化为项目自带的 CSV / JSON。

用法：
    python scripts/extract_source_data.py --source-dir "C:/Users/89628/Desktop"

抽取结果写入项目的 data/ 目录，使仓库自包含，
不依赖原始 Excel 也能复现全部图表。
若原始 Excel 不存在，仓库中已保存的 data/ 快照仍可直接使用。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


# --------------------------------------------------------------------------
# 通用小工具
# --------------------------------------------------------------------------
def _read_sheet(path: Path, sheet: str, max_row: int | None = None,
                max_col: int | None = None, header: int | None = None,
                usecols: str | None = None) -> pd.DataFrame:
    """用 pandas 读取 xlsx/xlsm 的指定工作表。"""
    return pd.read_excel(path, sheet_name=sheet, header=header,
                         nrows=max_row, usecols=usecols,
                         engine="openpyxl").iloc[:, :max_col] if max_col else \
        pd.read_excel(path, sheet_name=sheet, header=header,
                      nrows=max_row, usecols=usecols, engine="openpyxl")


def _dump(df: pd.DataFrame, name: str) -> None:
    out = DATA_DIR / name
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"  -> {out.relative_to(ROOT)}  ({len(df)} 行 x {df.shape[1]} 列)")


def _anonymize(df: pd.DataFrame, *cols: str) -> pd.DataFrame:
    """对外开源前的脱敏：把编号类字段替换成顺序匿名编号。"""
    df = df.copy()
    for col in cols:
        if col in df.columns:
            prefix = {"员工编号": "E", "员工号": "E", "订单单号": "SO"}.get(col, "ID")
            df[col] = [f"{prefix}{i + 1:06d}" for i in range(len(df))]
    return df


def _dump_json(obj, name: str) -> None:
    out = DATA_DIR / name
    out.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  -> {out.relative_to(ROOT)}")


# --------------------------------------------------------------------------
# 第二章：30 张图表的数据源（每张表数据量都很小，直接按 sheet 抽取）
# --------------------------------------------------------------------------
# (源文件名, sheet 名, 读取范围, 输出文件名, 表头行)
CH2_SHEETS = [
    # ---------- 前 15 ----------
    ("第二章 图表(前15).xlsx", "1 渐变柱形图", "B2:C8", "ch2_01_gradient_bar.csv", 0),
    ("第二章 图表(前15).xlsx", "2 带均值柱形图", "B2:C8", "ch2_02_mean_bar.csv", 0),
    ("第二章 图表(前15).xlsx", "3 渐变圆角柱形图", "B2:C8", "ch2_03_rounded_bar.csv", 0),
    ("第二章 图表(前15).xlsx", "4 标注柱形图", "B2:C10", "ch2_04_annotated_bar.csv", 0),
    ("第二章 图表(前15).xlsx", "5 层叠柱形图", "B2:D8", "ch2_05_overlap_bar.csv", 0),
    ("第二章 图表(前15).xlsx", "6 蝴蝶图", "B2:F7", "ch2_06_butterfly.csv", 0),
    ("第二章 图表(前15).xlsx", "7 蝴蝶图", "B2:D7", "ch2_07_butterfly_pct.csv", 0),
    ("第二章 图表(前15).xlsx", "8 数值百分比", "B2:F8", "ch2_08_percent_bar.csv", 0),
    ("第二章 图表(前15).xlsx", "9 对比柱形图", "B2:E8", "ch2_09_compare_bar.csv", 0),
    ("第二章 图表(前15).xlsx", "10 甘特图", "B3:G10", "ch2_10_gantt.csv", 0),
    ("第二章 图表(前15).xlsx", "11 平滑折线图", "B2:D13", "ch2_11_smooth_line.csv", 0),
    ("第二章 图表(前15).xlsx", "12 菱形走势图", "B2:C10", "ch2_12_diamond_line.csv", 0),
    ("第二章 图表(前15).xlsx", "13 对比折线图", "B2:D10", "ch2_13_compare_line.csv", 0),
    ("第二章 图表(前15).xlsx", "14 单值圆环图", "B2:C3", "ch2_14_single_donut.csv", 0),
    ("第二章 图表(前15).xlsx", "15 水球图", "B2:C3", "ch2_15_liquid.csv", 0),
    # ---------- 后 15 ----------
    ("第二章 图表(后15).xlsx", "16 波浪水球图 ", "B3:C4", "ch2_16_wave_liquid.csv", 0),
    ("第二章 图表(后15).xlsx", "17 玉玦图", "B2:D6", "ch2_17_jade_ring.csv", 0),
    ("第二章 图表(后15).xlsx", "18 跑道图", "B2:D8", "ch2_18_racetrack.csv", 0),
    ("第二章 图表(后15).xlsx", "19 南丁格尔圆饼图", "B2:C8", "ch2_19_rose_pie.csv", 0),
    ("第二章 图表(后15).xlsx", "20 南丁格尔圆环图", "B2:C6", "ch2_20_rose_donut.csv", 0),
    ("第二章 图表(后15).xlsx", "20 南丁格尔（PPT）", "B2:C8", "ch2_21_rose_ppt.csv", 0),
    ("第二章 图表(后15).xlsx", "22 仪表盘图", "B2:C24", "ch2_22_gauge_scale.csv", 0),
    ("第二章 图表(后15).xlsx", "23 柱形折线图", "B2:D8", "ch2_23_bar_line.csv", 0),
    ("第二章 图表(后15).xlsx", "24 目标柱形图", "B2:D8", "ch2_24_target_bar.csv", 0),
    ("第二章 图表(后15).xlsx", "25 子弹图", "B3:G9", "ch2_25_bullet.csv", 0),
    ("第二章 图表(后15).xlsx", "26 柱形圆", "B2:E8", "ch2_26_bar_circle.csv", 0),
    ("第二章 图表(后15).xlsx", "27 簇状柱形折线图", "B2:E8", "ch2_27_cluster_bar_line.csv", 0),
    ("第二章 图表(后15).xlsx", "28 复合柱形图", "B2:D17", "ch2_28_composite_bar.csv", 0),
    ("第二章 图表(后15).xlsx", "29 滑珠图", "B2:E7", "ch2_29_sliding_bead.csv", 0),
    ("第二章 图表(后15).xlsx", "30 对比滑珠图", "B3:F8", "ch2_30_compare_bead.csv", 0),
]


def extract_ch2(source_dir: Path) -> None:
    from openpyxl import load_workbook

    print("[第二章] 抽取 30 张图表的数据源")
    cache: dict[str, object] = {}
    for fname, sheet, rng, out_name, _hdr in CH2_SHEETS:
        path = source_dir / fname
        if not path.exists():
            print(f"  !! 缺少源文件，跳过：{fname}")
            continue
        if fname not in cache:
            cache[fname] = load_workbook(path, data_only=True)
        wb = cache[fname]
        if sheet not in wb.sheetnames:
            print(f"  !! 缺少工作表，跳过：{sheet}")
            continue
        ws = wb[sheet]
        cells = ws[rng]
        rows = [[c.value for c in row] for row in cells] if isinstance(cells, tuple) \
            else [[cells.value]]
        header = [str(h).strip() if h is not None else "" for h in rows[0]]
        body = [list(r) for r in rows[1:]]
        df = pd.DataFrame(body, columns=header)
        df = df.dropna(how="all")
        _dump(df, out_name)

    # 仪表盘指针数值（散落在 K 列）
    try:
        wb = load_workbook(source_dir / "第二章 图表(后15).xlsx", data_only=True)
        ws = wb["22 仪表盘图"]
        meta = {
            "pointer_value": ws["H3"].value,
            "scale_start": 50,
            "scale_end": 150,
        }
        _dump_json(meta, "ch2_22_gauge_meta.json")
    except Exception as exc:  # noqa: BLE001
        print(f"  !! 仪表盘辅助数据抽取失败：{exc}")


# --------------------------------------------------------------------------
# 第三章：动态图表
# --------------------------------------------------------------------------
def extract_ch3(source_dir: Path) -> None:
    print("[第三章] 抽取动态图表数据源")
    path = source_dir / "第三章 动态图表.xlsm"
    if not path.exists():
        print("  !! 缺少源文件")
        return

    def _table(sheet: str, usecols: str, header_key: str, nrows: int | None = None):
        """按「首列关键字」定位表头行，避免各表前导标题行数量不一致。"""
        raw = pd.read_excel(path, sheet_name=sheet, usecols=usecols,
                            header=None, engine="openpyxl")
        first = raw.iloc[:, 0].astype(str).str.strip()
        hit = raw.index[first == header_key]
        if len(hit) == 0:
            raise ValueError(f"{sheet}: 未找到表头行（首列应为 {header_key!r}）")
        pos = hit[0]
        df = raw.iloc[pos + 1:].copy()
        df.columns = [str(x).strip() for x in raw.iloc[pos]]
        df = df.dropna(how="all")
        if nrows:
            df = df.iloc[:nrows]
        return df.reset_index(drop=True)

    # 1 动态柱形图：月份 x 6 个区域
    _dump(_table("1 动态柱形图", "B:H", "月份", 6), "ch3_01_dynamic_bar.csv")

    # 2 动态跑道图：部门 x 4 个月（末行为说明文本，剔除）
    rt = _table("2 动态跑道图", "B:F", "部门", 6)
    _dump(rt, "ch3_02_dynamic_racetrack.csv")
    _dump_json({str(r["部门"]): str(r.iloc[-1])
                for _, r in _table("2 动态跑道图", "B:F", "部门").iterrows()
                if str(r["部门"]) == "说明"},
               "ch3_02_racetrack_note.json")

    # 3 动态南丁格尔圆环图：周期 x 5 个渠道
    _dump(_table("3 动态南丁格尔圆环图", "B:G", "周期", 2), "ch3_03_dynamic_rose.csv")

    # 4 动态组合图：指标(销售额/利润/利润率) x 商品
    _dump(_table("4 动态组合图", "B:F", "类别", 3), "ch3_04_dynamic_combo.csv")

    # 5 人力资源明细（透视表切片器的数据源，1470 人）
    df = _table("5 人力资源明细", "A:G", "员工号")
    _dump(_anonymize(df, "员工号"), "ch3_05_hr_detail.csv")

    # 6 VBA 动态玉玦图：周期 x 4 个渠道
    _dump(_table("6 VBA动态玉玦图", "B:F", "周期", 2), "ch3_06_dynamic_jade.csv")

    # 7 动态滑珠图：区域 x 6 个月
    _dump(_table("7 动态滑珠图", "B:H", "区域", 6), "ch3_07_dynamic_bead.csv")


# --------------------------------------------------------------------------
# 第四章：数据大屏
# --------------------------------------------------------------------------
def extract_ch4(source_dir: Path) -> None:
    print("[第四章] 抽取看板数据源")

    hr = source_dir / "第四章 人力资源可视化看板.xlsx"
    if hr.exists():
        df = pd.read_excel(hr, sheet_name="202203人员基础信息",
                           usecols="A:H", engine="openpyxl")
        df = df.dropna(how="all")
        _dump(_anonymize(df, "员工编号"), "ch4_hr_base.csv")
    else:
        print("  !! 缺少人力资源看板源文件")

    sales = source_dir / "第四章 销售看板参考.xlsx"
    if sales.exists():
        df = pd.read_excel(sales, sheet_name="销售明细", engine="openpyxl")
        df = df.dropna(how="all")
        _dump(_anonymize(df, "订单单号"), "ch4_sales_detail.csv")

        cost = pd.read_excel(sales, sheet_name="成本明细", engine="openpyxl")
        cost = cost.dropna(how="all")
        _dump(cost, "ch4_cost_detail.csv")
    else:
        print("  !! 缺少销售看板源文件")


# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="抽取原书 Excel 数据到 data/")
    ap.add_argument("--source-dir", default=r"C:/Users/89628/Desktop",
                    help="原始 Excel 所在目录")
    args = ap.parse_args()

    source_dir = Path(args.source_dir)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not source_dir.exists():
        print(f"源目录不存在：{source_dir}")
        return 1

    extract_ch2(source_dir)
    extract_ch3(source_dir)
    extract_ch4(source_dir)
    print("\n完成。数据已写入", DATA_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
