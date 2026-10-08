# excel-viz-python —— 《Excel数据可视化：从图表到数据大屏》Python 实现

> 把一本 Excel 可视化教程，完整迁移成 Python（pandas + matplotlib）实现。
> 30 个基础图表 + 7 个动态图表 + 2 块数据看板，全部可一键复现。

**仓库地址**：https://github.com/violet8962/Excel---1

```bash
git clone git@github.com:violet8962/Excel---1.git
cd Excel---1
pip install -r requirements.txt
python scripts/run_all.py
```

---

## 一、项目简介

本项目以《Excel 数据可视化——从图表到数据大屏》一书及其配套实验文件为蓝本，
将书中的图表技法逐例迁移到 Python：

| 原书内容 | Excel 实现方式 | Python 实现方式 |
|---|---|---|
| 第二章 30 例图表 | 图表功能 + 形状 + 辅助占位序列 | matplotlib 一例一函数 |
| 第三章 动态图表 | 表单控件 + INDEX/VLOOKUP/OFFSET 联动、VBA 宏 | 循环重绘 + Pillow 合成 GIF |
| 第三章 切片器 | 数据透视表 + 切片器 | pandas `groupby` 透视 + 逐帧切换 |
| 第四章 看板/大屏 | 多图表排版 + 形状打底 | GridSpec 布局 + 统一主题 |

配套实验数据（原书 Excel）已抽取为 `data/` 目录下的 CSV 快照，
**克隆仓库即可运行，不依赖原始 Excel 文件**。

---

## 二、快速开始

```bash
# 1. 安装依赖（建议 Python 3.10+）
pip install -r requirements.txt

# 2. 一键生成全部图表
python scripts/run_all.py

# 或只运行某一章
python scripts/run_all.py --only ch2   # 第二章：30 例基础图表
python scripts/run_all.py --only ch3   # 第三章：动态图表（GIF）
python scripts/run_all.py --only ch4   # 第四章：看板与大屏
```

也可以单独运行任意一例：

```python
from excel_viz.ch2_part1 import chart_01_gradient_bar
chart_01_gradient_bar()   # 输出 output/ch2/01_渐变柱形图.png
```

> 若想从原始 Excel 重新抽取数据：
> `python scripts/extract_source_data.py --source-dir <原始Excel所在目录>`

---

## 三、目录结构

```
excel-viz-python
├── data/                     # 从原书 Excel 抽取的数据快照（自包含）
├── docs/                     # 各章实验说明
├── scripts/
│   ├── extract_source_data.py   # 原始 Excel → data/ CSV
│   └── run_all.py               # 一键运行全部实验
├── src/excel_viz/
│   ├── theme.py              # 主题：配色 / 字体 / 渐变 / 圆角柱 / 三段式标题
│   ├── utils.py              # Catmull-Rom 平滑、垂直线等算法
│   ├── data.py               # 数据加载与聚合层
│   ├── ch2_part1.py          # 第二章 01~15 例
│   ├── ch2_part2.py          # 第二章 16~30 例
│   ├── ch3_dynamic.py        # 第三章 7 个动态图表
│   └── ch4_dashboard.py      # 第四章 人力资源看板 + 销售大屏
└── output/                   # 运行产物（png / gif，已 gitignore）
```

---

## 四、实验内容总览

### 第二章 · 30 例基础图表（`output/ch2/`）

| # | 图表 | 关键技法 | Python 对应实现 |
|---|------|----------|-----------------|
| 01 | 渐变柱形图 | 渐变填充 | `imshow` 渐变 + 柱形裁剪 |
| 02 | 带均值柱形图 | 辅助序列画均值线 | `axhline` |
| 03 | 渐变圆角柱形图 | 圆角矩形形状填充 | `FancyBboxPatch` |
| 04 | 标注柱形图 | 极值标注 | `ax.annotate` |
| 05 | 层叠柱形图 | 双系列叠放 | 双 `ax.bar` |
| 06/07 | 蝴蝶图 | 占位序列 + 负值条形 | 正负双向 `barh` |
| 08 | 数值百分比 | 占位轨道条 | 轨道 bar + 百分比刻度 |
| 09 | 对比柱形图 | 差值标注 | 双柱 + `annotate` |
| 10 | 甘特图 | 堆积条形伪装 | `barh(left=)` |
| 11 | 平滑折线图 | 平滑线选项 | Catmull-Rom 样条 |
| 12 | 菱形走势图 | 垂直线元素 | `plot` + 垂直虚线 |
| 13 | 对比折线图 | 差异区域填充 | `fill_between` |
| 14 | 单值圆环图 | 双扇区圆环 | `Wedge` |
| 15/16 | 水球图 / 波浪水球 | 圆形裁剪 + 形状 | `Circle` 裁剪 + 正弦波面 |
| 17 | 玉玦图 | 占位凑缺口 | 扇区起止角控制 |
| 18 | 跑道图 | 多层圆环 | 嵌套 `Wedge` |
| 19~21 | 南丁格尔玫瑰（3 种） | 多层圆环复制 | 半径随数值缩放的 `Wedge` |
| 22 | 仪表盘图 | 饼图拼装 | 扇区刻度盘 + 指针 |
| 23/27 | 柱形折线组合 | 次坐标轴 | `twinx` |
| 24 | 目标柱形图 | 目标线 | 横线刻度 |
| 25 | 子弹图 | 叠加条形 | 定性背景 + 实际值条 |
| 26 | 柱形圆 | 圆形数据标记 | `scatter` |
| 28 | 复合柱形图 | 两层数据 | 宽窄双柱 |
| 29/30 | 滑珠图 / 对比滑珠图 | 散点叠条形 | 轨道 + 珠子 |

### 第三章 · 7 个动态图表（`output/ch3/*.gif`）

| # | 图表 | Excel 原理 | Python 复现 |
|---|------|-----------|-------------|
| 01 | 动态柱形图 | 组合框 + INDEX/VLOOKUP | 逐月重绘 → GIF |
| 02 | 动态跑道图 | 滚动条联动 | 逐月跑道 → GIF |
| 03 | 动态南丁格尔圆环图 | 组合框切换周期 | 逐周期玫瑰 → GIF |
| 04 | 动态组合图 | 复选框 + IF 隐藏 | 系列显隐组合 → GIF |
| 05 | 透视表切片器 | 透视表 + 切片器 | pandas 透视 + 逐部门切换 |
| 06 | VBA 动态玉玦图 | VBA 宏换源 | 循环重绘 → GIF |
| 07 | 动态滑珠图 | 滚动条选月 | 逐月滑珠 → GIF |

每张 GIF 同时在 `output/ch3/frames/` 保存了各档位的静态 PNG。

### 第四章 · 看板与大屏（`output/ch4/`）

| 产出 | 风格 | 数据 |
|------|------|------|
| 人力资源可视化看板 | 浅色商务 | 1,470 人基础信息（年龄 / 婚姻 / 性别 / 学历 / 部门 / 入转调） |
| 销售数据大屏 | 深色大屏 | 8,564 条订单明细（KPI + 月度销售额 / 环比 / 利润率 / 快递 / 区域 / 类别 / Top3） |

所有指标均由明细数据实时聚合，替换 `data/` 中的 CSV 即可复用到自己的数据。

---

## 五、原书方法论 → 代码规范的沉淀

原书强调的图表修饰三步法，已沉淀为 `theme.py` 的统一组件：

1. **删除非必要元素** → `style_axes()`：去边框、淡网格；
2. **添加必要元素** → `title_block()`：一级标题 / 二级标题（结论）/ 备注（口径来源）；
3. **修饰图表元素** → `EXCEL_PALETTE`（Office 主题色）、`gradient_bars()`、`rounded_bar()`。

> 配色遵循 Excel 2016+ 默认 Office 主题色板，保证复现图与原书同一色系；
> 中文字体自动在 微软雅黑 / 黑体 / 思源黑体 / Noto Sans CJK 等中选择可用项。

---

## 六、环境与依赖

- Python ≥ 3.10
- pandas / numpy / matplotlib / openpyxl / pillow（见 `requirements.txt`）

## 七、致谢与说明

- 图表案例与数据来源于《Excel 数据可视化——从图表到数据大屏》配套实验文件，
  本项目仅作学习与技术迁移用途。
- 数据已在 `data/` 目录做快照处理，不含任何敏感个人信息（员工编号已脱敏处理）。

## License

MIT
