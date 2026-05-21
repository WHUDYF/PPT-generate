# 数字经济博物馆数值分析 - Design Spec

> Human-readable design narrative. Machine-readable execution contract: `spec_lock.md`.

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | 数字经济博物馆增长与文旅复苏数值分析 |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 12 |
| **Design Style** | B) General Consulting + 学术答辩 |
| **Target Audience** | 数值技术课程教师与同学 |
| **Use Case** | 课程结课答辩汇报（5 分钟） |
| **Created Date** | 2026-05-22 |

---

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| **Format** | PPT 16:9 |
| **Dimensions** | 1280×720 |
| **viewBox** | `0 0 1280 720` |
| **Margins** | left/right 60px, top/bottom 50px |
| **Content Area** | 1160×620 (safe area within margins) |

---

## III. Visual Theme

### Theme Style

- **Style**: B) General Consulting + 学术答辩
- **Theme**: Light theme
- **Tone**: 数据理性、学术严谨、文化遗产温度

### Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#FAFAFA` | 页面基础背景 |
| **Secondary bg** | `#F0F4F8` | 卡片/区块底色 |
| **Primary** | `#1A3A5C` | 标题装饰、关键区块、图标主色 |
| **Accent** | `#C8963E` | 数据高亮、关键数字强调 |
| **Secondary accent** | `#2E6B8F` | 次要强调、图表辅助色 |
| **Body text** | `#1A1A2E` | 正文文字 |
| **Secondary text** | `#6B7280` | 注释、图例、来源标注 |
| **Tertiary text** | `#9CA3AF` | 页脚、页码 |
| **Border/divider** | `#D1D5DB` | 卡片边框、分割线 |
| **Success** | `#2E7D32` | 正向趋势/增长 |
| **Warning** | `#C62828` | 冲击标注/下降 |

### AI Image Strategy

(Not applicable — no AI-generated images in this deck)

### Gradient Scheme

```xml
<!-- Title accent gradient -->
<linearGradient id="titleAccent" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="#1A3A5C"/>
  <stop offset="100%" stop-color="#2E6B8F"/>
</linearGradient>

<!-- Background decorative gradient -->
<radialGradient id="bgDecor" cx="85%" cy="15%" r="45%">
  <stop offset="0%" stop-color="#1A3A5C" stop-opacity="0.06"/>
  <stop offset="100%" stop-color="#1A3A5C" stop-opacity="0"/>
</radialGradient>

<!-- Warm accent gradient (for key numbers) -->
<linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="#C8963E"/>
  <stop offset="100%" stop-color="#D4A857"/>
</linearGradient>
```

---

## IV. Typography System

### Font Plan

**Typography direction**: 中文学术答辩 — KaiTi 标题 × Microsoft YaHei 正文（Contrast 方案）

Two views on the same decisions — keep both consistent:

| Role | Chinese | English | Fallback tail |
| ---- | ------- | ------- | ------------- |
| **Title** | `KaiTi` | `Georgia` | `serif` |
| **Body** | `"Microsoft YaHei", "PingFang SC"` | `Arial` | `sans-serif` |
| **Emphasis** | `KaiTi` | `Georgia` | `serif` |
| **Code** | — | `Consolas, "Courier New"` | `monospace` |

**Per-role font stacks** (CSS `font-family` strings):

- Title: `Georgia, KaiTi, serif`
- Body: `"Microsoft YaHei", "PingFang SC", Arial, sans-serif`
- Emphasis: `Georgia, KaiTi, serif`
- Code: `Consolas, "Courier New", monospace`

> Stack ordering: Latin-led (Georgia first) — Latin in elegant serif, CJK falls through to KaiTi. Academic documents benefit from serif typography in titles while data tables need sans-serif clarity.

### Font Size Hierarchy

**Baseline**: Body font size = `18px` (dense data-report baseline)

| Purpose | Ratio to body | Value @ body=18 | Weight |
| ------- | ------------- | --------------- | ------ |
| Cover title (hero headline) | 2.5-5x | 45-90px | Bold |
| Chapter / section opener | 2-2.5x | 36-45px | Bold |
| Page title | 1.5-2x | 27-36px | Bold |
| Hero number (consulting KPIs) | 1.5-2x | 27-36px | Bold |
| Subtitle | 1.2-1.5x | 22-27px | SemiBold |
| **Body content** | **1x** | **18px** | Regular |
| Annotation / caption | 0.7-0.85x | 13-15px | Regular |
| Page number / footnote | 0.5-0.65x | 9-12px | Regular |

---

## V. Layout Principles

### Page Structure

- **Header area**: Top 80px — page title zone with left accent bar (4px × 36px, primary color)
- **Content area**: 80px to 670px — main content zone (590px height)
- **Footer area**: 670px to 720px — page number + source annotation

### Layout Pattern Library

| Pattern | Suitable Scenarios |
| ------- | ----------------- |
| **Single column centered** | P01 Cover, P12 Conclusion |
| **Asymmetric split (3:7)** | Chart-heavy pages (P08, P09) — chart left 70%, annotations right 30% |
| **Top-bottom split** | Data table + commentary (P04, P11) |
| **Three-column cards** | P02 framework, P03 indicators |
| **Z-pattern / waterfall** | P05 process flow, P06-P07 algorithm explanation |

### Spacing Specification

**Universal**:

| Element | Value |
| ------- | ----- |
| Safe margin from canvas edge | 60px |
| Content block gap | 32px |
| Icon-text gap | 12px |

**Card-based layouts**:

| Element | Value |
| ------- | ----- |
| Card gap | 24px |
| Card padding | 24px |
| Card border radius | 10px |
| Single-row card height | 540px |

---

## VI. Icon Usage Specification

### Source

- **Built-in icon library**: `phosphor-duotone` — duotone layered style, main shape + 20% opacity backplate, medium weight, contemporary academic feel
- **Usage method**: SVG placeholder `<use data-icon="phosphor-duotone/icon-name" .../>`

### Recommended Icon Inventory

| Purpose | Icon Path | Used On |
| ------- | --------- | ------- |
| 博物馆/文化设施 | `phosphor-duotone/buildings` | P01, P02, P08 |
| 增长趋势 | `phosphor-duotone/chart-line-up` | P01, P08 |
| 下降/冲击 | `phosphor-duotone/trend-down` | P09 |
| 旅游花费 | `phosphor-duotone/currency-circle-dollar` | P02, P08 |
| 数据来源 | `phosphor-duotone/database` | P03, P04 |
| 数值计算 | `phosphor-duotone/calculator` | P05, P06 |
| 数学函数 | `phosphor-duotone/function` | P06, P07 |
| 模型分析 | `phosphor-duotone/graph` | P07, P10 |
| 数据表 | `phosphor-duotone/table` | P03, P04 |
| 反事实基准 | `phosphor-duotone/target` | P07, P11 |
| 数字化连接 | `phosphor-duotone/link-simple` | P02, P05 |
| 学术 | `phosphor-duotone/graduation-cap` | P01, P12 |
| 结论 | `phosphor-duotone/check-circle` | P10, P12 |
| 关键洞见 | `phosphor-duotone/lightbulb` | P12 |
| 游客/用户 | `phosphor-duotone/users` | P02, P09 |

---

## VII. Visualization Reference List

Catalog read: 71 templates

| Page | Template | Path | Summary-quote (verbatim from `charts_index.json`) | Usage |
| ---- | -------- | ---- | ------------------------------------------------- | ----- |
| P02 | process_flow | `templates/charts/process_flow.svg` | "Pick for 3-8 sequential steps connected by simple arrows — approval workflows, customer onboarding, request handling, lifecycle stages." | 三层递进框架：供给层→数字化连接层→转化层 |
| P03 | basic_table | `templates/charts/basic_table.svg` | "Pick for plain tabular text/number grid, 3-8 columns." | 三指标口径表：指标/单位/社会含义/处理链路 |
| P04 | basic_table | `templates/charts/basic_table.svg` | "Pick for plain tabular text/number grid, 3-8 columns." | 2014-2023 原始数据表 10行×5列 |
| P05 | numbered_steps | `templates/charts/numbered_steps.svg` | "Pick for 3-6 horizontal sequential steps with numeric emphasis — how-it-works section, getting-started guide, methodology overview, implementation phases." | 五步处理链路：统一口径→指数化→转化指标→阶段标注→模型输入 |
| P06 | numbered_steps | `templates/charts/numbered_steps.svg` | "Pick for 3-6 horizontal sequential steps with numeric emphasis — how-it-works section, getting-started guide, methodology overview, implementation phases." | 四点差分计算流程 |
| P07 | pros_cons_chart | `templates/charts/pros_cons_chart.svg` | "Pick for bilateral pros/cons list, 2-5 items per side." | 全周期模型 vs 分段模型优缺点对比 |
| P08 | dual_axis_line_chart | `templates/charts/dual_axis_line_chart.svg` | "Pick when 2 metrics with different units/scales must be compared over time." | 博物馆数量（个）+ 旅游总花费（亿元）双轴趋势 |
| P09 | dual_axis_line_chart | `templates/charts/dual_axis_line_chart.svg` | "Pick when 2 metrics with different units/scales must be compared over time." | 博物馆年度增量 + 游客年度变化率双轴 |
| P10 | scatter_chart | `templates/charts/scatter_chart.svg` | "Pick for x-y correlation, cluster, or outlier scan." | 博物馆数 vs 游客散点图（分阶段着色） |
| P11 | bar_chart | `templates/charts/bar_chart.svg` | "Pick for single-series category value comparison, 3-8 categories." | 2020/2023 反事实缺口对比柱状图 |
| P12 | vertical_list | `templates/charts/vertical_list.svg` | "Pick for 3-6 numbered key points each with a short description — design principles, core tenets, action items, key takeaways, recommendations, executive summary points." | 三结论要点：数据结论/算法结论/政策结论 |

**Runners-up considered** (3 entries minimum):

- `pipeline_with_stages` | rejected for P02: 三层之间是递进箭头关系、非产出物管道
- `kpi_cards` | rejected for P03: 此页是规格表非 KPI 卡片
- `comparison_table` | rejected for P07: 仅两个模型对比，非多行特性矩阵
- `line_chart` | rejected for P08: 两指标不同单位和尺度，单轴无法同时展示
- `grouped_bar_chart` | rejected for P09: 变化率更适合用折线连续性展示方向

---

## VIII. Image Resource List

(Not applicable — Option A: No images. This is a pure data report deck.)

---

## IX. Content Outline

### Part 1: 封面与背景 (P01-P03)

#### P01 - Cover

- **Layout**: Single column centered — 封面居中布局
- **Rhythm**: `anchor`
- **Title**: 数值技术课程结课汇报
- **Subtitle**: 数字经济背景下 博物馆增长与文旅复苏
- **Tagline**: 文化供给、数字化连接与消费转化的数值分析
- **Info block**: 研究对象: 2014-2023 年度序列 | 核心指标: 3 个国家统计指标 | 汇报时间: 5 分钟以内
- **Source**: 数据来源：国家统计局国家数据与《中国统计年鉴》公开指标
- **Visualization**: None (pure cover)
- **Icons**: buildings, chart-line-up, graduation-cap

#### P02 - 选题价值：数字经济连接文化供给与文旅消费

- **Layout**: Top-bottom split — 上部框架图 + 下部三层递进流程
- **Rhythm**: `dense`
- **Title**: 选题价值：数字经济连接文化供给与文旅消费
- **Visualization**: process_flow
- **Content**:
  - 核心命题（顶部突出）：博物馆是文化资源入口，数字化连接决定其向游客流量和文旅消费的转化效率
  - 三支柱：国家战略 / 民生改善 / 数值方法适配（并列卡片）
  - 三层递进流程箭头链：供给层（博物馆数量增长）→ 数字化连接层（预约/导览/展陈/文创）→ 转化层（游客恢复+消费支出）
  - 研究问题（底部）：数字经济背景下，文化供给扩张能否重新转化为游客恢复和文旅消费？
- **Source**: 国家统计局国家数据、中国统计年鉴；团队计算

#### P03 - 数据来源与指标口径

- **Layout**: Top-bottom split — 上部说明文字 + 下部三指标规格表
- **Rhythm**: `dense`
- **Title**: 数据来源与指标口径：构造 2014-2023 年离散点集
- **Visualization**: basic_table
- **Content**:
  - 统一口径说明（顶部一行）
  - 三指标规格表：指标 / 单位 / 社会含义 / 处理链路
  - 建模选择提示：对年度离散点直接做数值微分和拟合，不人为插入月度数据
- **Source**: 国家统计局国家数据、中国统计年鉴；团队整理

### Part 2: 数据与处理 (P04-P05)

#### P04 - 原始数据表

- **Layout**: Top-bottom split — 表格主体 + 底部注释
- **Rhythm**: `dense`
- **Title**: 原始数据表：三个指标形成可计算时间序列
- **Visualization**: basic_table
- **Content**:
  - 10 年 × 5 列数据表：年份 / 博物馆数量（个） / 国内游客（百万人次） / 旅游总花费（亿元） / 阶段
  - 阶段标注：增长期（蓝）/ 高点（深蓝）/ 冲击（红）/ 修复（橙）/ 波动（灰）/ 恢复（绿）
  - 底部注释：单位说明与数据来源
- **Source**: 国家统计局国家数据、中国统计年鉴；团队整理

#### P05 - 数据处理：从原始指标到可计算特征

- **Layout**: Top-bottom split — 上部流程步骤 + 下部派生指标卡片
- **Rhythm**: `dense`
- **Title**: 数据处理：从原始指标到可计算特征
- **Visualization**: numbered_steps
- **Content**:
  - 引导语：原始数据虽少，但可通过口径统一、指数化和转化效率指标形成可计算时间序列
  - 五步处理链路：统一口径 → 指数化 → 转化指标 → 阶段标注 → 模型输入
  - 派生指标卡片（三列）：
    - 单馆游客量：1.170 → 0.716（2019→2023，百万人次/馆）
    - 人均旅游消费：953.2 → 1004.6（2019→2023，元/人）
    - 博物馆指数：100 → 186.8（2014→2023，2014=100）
  - 底部：预处理原则 + 输出文件列表
- **Source**: 团队预处理规则与 Python 计算

### Part 3: 数值方法 (P06-P07)

#### P06 - 算法一：三点差分

- **Layout**: Asymmetric split (4:6) — 左侧公式 + 右侧计算流程
- **Rhythm**: `dense`
- **Title**: 算法一：三点公式把"趋势"转化为年度边际变化
- **Visualization**: numbered_steps
- **Content**:
  - 核心公式（左侧突出）：f'(x_i) ≈ [f(x_{i+1}) - f(x_{i-1})] / 2h
  - 端点公式：f'(x_0) ≈ f(x_1)-f(x_0)；f'(x_n) ≈ f(x_n)-f(x_{n-1})
  - 四步计算流程（右侧）：读取年度序列 → 内部点中心差分 → 首尾单侧差分 → 比较变化率、定位拐点
  - 物理解释：差分值越大，说明该指标在该年度附近扩张或恢复越快
- **Source**: 课程数值微分公式；团队 Python 实现

#### P07 - 算法二：分段最小二乘

- **Layout**: Asymmetric split (5:5) — 左侧全周期模型 + 右侧分段模型
- **Rhythm**: `dense`
- **Title**: 算法二：分段最小二乘避免冲击期扭曲
- **Visualization**: pros_cons_chart
- **Content**:
  - 目标公式（顶部居中）：最小化 S = Σ[y_i - (a x_i + b)]²
  - 全周期线性/二次（左侧）：y = a x + b；优点公式简单，缺点混入冲击
  - 分段低次模型（右侧）：2014-2019 平稳段 + 2020-2023 恢复段分别拟合
  - 误差意识框：二次模型样本内略好但留一误差更差 → 不采用高阶外推
  - 应用说明：平稳趋势同时构造反事实基准；2024-2026 短期外推仅看方向
- **Source**: 最小二乘法；团队 Python 实现

### Part 4: 实证结果 (P08-P11)

#### P08 - 规模趋势

- **Layout**: Asymmetric split (7:3) — 左侧双轴图 + 右侧读图结论
- **Rhythm**: `anchor`
- **Title**: 规模趋势：文化供给持续增长，旅游消费冲击后修复
- **Visualization**: dual_axis_line_chart
- **Content**:
  - 双轴折线图：左轴 博物馆数量（个，柱状或面积），右轴 旅游总花费（亿元，折线）
  - 2020 冲击竖线标注
  - 右侧三个读图结论卡片：
    - +86.8%：2014-2023 年博物馆数量增长
    - 2019 年旅游消费高点 57251 亿元
    - 2023 年需求侧明显修复至 49133.1 亿元
- **Source**: 国家统计局国家数据、中国统计年鉴；团队计算

#### P09 - 变化率

- **Layout**: Asymmetric split (7:3) — 左侧双轴变化率图 + 右侧关键读数
- **Rhythm**: `anchor`
- **Title**: 变化率：2020 年冲击与 2023 年修复被差分清晰捕捉
- **Visualization**: dual_axis_line_chart
- **Content**:
  - 双轴变化率图：博物馆年度增量（柱）+ 游客年度变化率（折线）
  - 标注最低点和最高点
  - 右侧关键读数卡片：
    - -1380：2020 年附近游客变化率（百万人次/年）
    - +2361：2023 年游客变化率
  - 一句话解释：供给侧持续扩张，需求侧受外生冲击后快速修复
- **Source**: 团队三点差分计算

#### P10 - 模型比较

- **Layout**: Top-bottom split — 上部误差比较表 + 下部散点图
- **Rhythm**: `dense`
- **Title**: 模型比较：分段最小二乘更适合冲击型社会数据
- **Visualization**: scatter_chart
- **Content**:
  - 误差比较表（上部）：RMSE 对比 — 分段最小二乘 vs 全周期线性
  - 散点图（下部）：横轴 博物馆数量，纵轴 国内游客，分 2014-2019（蓝色）和 2020-2023（红色）着色
  - 相关系数标注：r = 0.988（平稳期）
  - 解释要点框：课程对应函数逼近+分段低次；相关≠因果但高度同向说明共同增长背景
- **Source**: 团队 Pearson 相关系数计算

#### P11 - 反事实缺口

- **Layout**: Top-bottom split — 上部缺口柱状图 + 下部预测表
- **Rhythm**: `dense`
- **Title**: 反事实缺口：衡量文旅需求相对正常趋势的恢复程度
- **Visualization**: bar_chart
- **Content**:
  - 反事实缺口柱状图（上部）：2020/2023 实际值 vs 平稳趋势基准（游客、消费各两组柱）
  - 缺口数值标注：游客 2020 缺口 -3602.5 百万人次(44.4%)；消费 2020 缺口 -39949.8 亿元(35.8%)
  - 2024-2026 预测表（下部）：博物馆数/游客/消费三行
  - 误差边界说明框：年度采样间隔+模型误差+外生冲击限制
  - 结论：分段拟合用于解释结构变化，反事实缺口用于衡量恢复程度
- **Source**: 团队最小二乘拟合与误差分析

### Part 5: 结论 (P12)

#### P12 - 结论

- **Layout**: Single column centered — 上部标题 + 三列结论卡片
- **Rhythm**: `breathing`
- **Title**: 结论：数字经济提升文化供给的消费转化效率
- **Visualization**: vertical_list
- **Content**:
  - 引导语：博物馆数量增长提供供给基础，数字化连接决定转化效率
  - 三大结论（垂直卡片）：
    - 数据结论：博物馆数量 2014-2023 年增长 86.8%，供给侧保持长期扩张
    - 算法结论：三点差分识别冲击，分段最小二乘比较模型，反事实缺口衡量恢复
    - 政策结论：线上预约、智慧导览与数字展陈提升连接效率，推动消费转化
  - 底部亮点总结：用数值方法解释"文化供给扩张—数字化连接—文旅消费转化"的链条
- **Source**: 团队综合分析

---

## X. Speaker Notes Requirements

- **Filename**: match SVG name (e.g., `01_cover.md`)
- **Total duration**: 5 minutes (12 pages, ~25 seconds per page average)
- **Style**: 正式学术汇报 — 结论先行，数据支撑
- **Content**: 每页核心要点 + 过渡语句 + 关键数字复述
- **Split rule**: one `.md` file per page in `notes/`

---

## XI. Technical Constraints Reminder

### SVG Generation Must Follow:

1. viewBox: `0 0 1280 720`
2. Background uses `<rect>` elements
3. Text wrapping uses `<tspan>` (`<foreignObject>` FORBIDDEN)
4. Transparency uses `fill-opacity` / `stroke-opacity`; `rgba()` FORBIDDEN
5. FORBIDDEN: `mask`, `<style>`, `class`, `foreignObject`
6. FORBIDDEN: `textPath`, `animate*`, `script`
7. Text characters: write typography & symbols as raw Unicode (em dash `—`, en dash `–`, `©`, `®`, `→`, NBSP, etc.); HTML named entities (`&nbsp;`, `&mdash;`, `&copy;`, `&reg;`, `&hellip;`, `&bull;` …) are FORBIDDEN. XML reserved chars in text MUST be escaped as `&amp;` `&lt;` `&gt;` `&quot;` `&apos;`
8. `marker-start` / `marker-end` conditionally allowed: `<marker>` must be in `<defs>`, `orient="auto"`, shape must be triangle / diamond / circle
9. `clipPath` conditionally allowed **only on `<image>` elements**

### PPT Compatibility Rules:

- `<g opacity="...">` FORBIDDEN (group opacity); set on each child element individually
- Image transparency uses overlay mask layer (`<rect fill="bg-color" opacity="0.x"/>`)
- Inline styles only; external CSS and `@font-face` FORBIDDEN
