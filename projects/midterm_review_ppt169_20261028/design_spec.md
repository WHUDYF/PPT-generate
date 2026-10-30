# midterm_review - Design Spec

> Human-readable design narrative. Machine-readable execution contract: `spec_lock.md`. On divergence, `spec_lock.md` wins.

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | 硕士中期考核汇报 |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 15 |
| **Design Style** | B) General Consulting + 极简学术汇报（白底、无装饰） |
| **Target Audience** | 学院中期考核评委（导师组），背景横跨体系结构 / EDA / AI，熟悉程度不一 |
| **Use Case** | 硕士中期考核，汇报 10 分钟 + 提问 3 分钟 |
| **Created Date** | 2026-10-28 |

---

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| **Format** | PPT 16:9 |
| **Dimensions** | 1280×720 |
| **viewBox** | `0 0 1280 720` |
| **Margins** | 左右 60px，上 40px，下 40px |
| **Content Area** | x 60–1220，y 130–670（标题区 40–110，页脚 680–700） |

---

## III. Visual Theme

### Theme Style

- **Style**: 极简学术汇报，信息靠排版和留白组织，不用装饰元素、渐变、阴影
- **Theme**: Light theme（纯白底）
- **Tone**: 克制、清晰、工程化

### Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#FFFFFF` | 页面背景 |
| **Secondary bg** | `#F5F7FA` | 少量分区底色（框架层条带、表头） |
| **Primary** | `#1F3A5F` | 标题、标题下划线、框线、节点 |
| **Accent** | `#C8102E` | 关键数字与结论，每页最多 1–2 处 |
| **Secondary accent** | `#5B7BA6` | 主色的浅一级：次级框线、连线 |
| **Body text** | `#222222` | 正文 |
| **Secondary text** | `#6B7280` | 说明、注释 |
| **Tertiary text** | `#9CA3AF` | 页码、页脚 |
| **Border/divider** | `#E5E7EB` | 分隔线、浅框 |
| **Success** | `#2E7D32` | 已完成标记（仅第 12 页） |
| **Warning** | `#C8102E` | 与 Accent 共用 |

---

## IV. Typography System

### Font Plan

**Typography direction**: 统一字体（concord）——全篇微软雅黑，靠字重区分层级；模块名 / 代码用 Consolas。

| Role | Chinese | English | Fallback tail |
| ---- | ------- | ------- | ------------- |
| **Title** | `"Microsoft YaHei", "PingFang SC"` | `Arial` | `sans-serif` |
| **Body** | `"Microsoft YaHei", "PingFang SC"` | `Arial` | `sans-serif` |
| **Emphasis** | same as Body（加粗 + Accent 色） | — | — |
| **Code** | — | `Consolas, "Courier New"` | `monospace` |

**Per-role font stacks**:

- Title: `"Microsoft YaHei", "PingFang SC", Arial, sans-serif`
- Body: `"Microsoft YaHei", "PingFang SC", Arial, sans-serif`
- Emphasis: same as Body
- Code: `Consolas, monospace`

### Font Size Hierarchy

**Baseline**: Body = 20px

| Purpose | Size | Weight |
| ------- | ---- | ------ |
| Cover title | 52px | Bold |
| Page title | 32px | Bold |
| Hero number | 36–40px | Bold |
| Subtitle / 小节标题 | 24px | Bold |
| Body | 20px | Regular |
| Dense body（框内） | 16–18px | Regular |
| Annotation | 15px | Regular |
| Page number / footnote | 12px | Regular |

---

## V. Layout Principles

### Page Structure

- **Header area**: y 40–110。左上 32px 粗体标题（y≈78），下方一条 1200px 宽、2px 的 `#1F3A5F` 细线（y=100）；右上角 15px 灰色小字标注所属部分（如"一 · GPU 学习"）。
- **Content area**: y 130–670。
- **Footer area**: y 690，左侧 12px 灰字"硕士中期考核"，右侧页码。封面不加页眉页脚。

### Layout Pattern Library

使用：单列居中（封面 / 结论）、非对称分栏（图 + 要点）、分层条带（框架页）、两栏对照（项目 A/B、C/D）、横向流程（问题 → 方法）。避免满屏卡片网格；容器以细线框（1px `#E5E7EB` 或 1.5px 主色）为主，不加阴影，圆角 ≤ 4px。

### Spacing Specification

| Element | Current Project |
| ------- | --------------- |
| Safe margin | 60px |
| Content block gap | 32px |
| Icon-text gap | 10px |
| Card padding | 20px |
| Card border radius | 4px |
| Line-height | 1.5× |

---

## VI. Icon Usage Specification

### Source

- **Library**: `tabler-outline`，stroke-width 1.5，极少量使用（仅第 2 页三条线的标识和第 12 页完成标记）
- **Usage**: `<use data-icon="tabler-outline/<name>" .../>`

### Recommended Icon List

| Purpose | Icon Path | Page |
| ------- | --------- | ---- |
| GPU 学习 | `tabler-outline/cpu` | P02 |
| AI for EDA | `tabler-outline/bulb` | P02 |
| 公司学习 | `tabler-outline/building-factory-2` | P02 |
| 已完成 | `tabler-outline/check` | P12 |
| 问题 / 漏检 | `tabler-outline/alert-triangle` | P06 |
| 目标 / 后续 | `tabler-outline/target` | P12 |

---

## VII. Visualization Reference List

Catalog read: 71 templates

| Page | Template | Path | Summary-quote (verbatim from `charts_index.json`) | Usage |
| ---- | -------- | ---- | ------------------------------------------------- | ----- |
| P02 | timeline | `templates/charts/timeline.svg` | "Pick for 3-8 milestone events on a horizontal time axis (no duration). Skip for tasks with start/end ranges (use gantt_chart) or vertical layout (use roadmap_vertical)." | 一年里程碑横轴，三条线分色标在轴上下 |
| P12 | layered_architecture | `templates/charts/layered_architecture.svg` | "Pick for 3-4 horizontal architecture layers (presentation/service/data), 2-4 module cards per layer, each card = title + 1-line description (description required, even if source brief). Skip if no per-module descriptions (use icon_grid) or no horizontal layering (use module_composition)." | 六层流程条带（压缩为纵向 6 条），右侧标注项目 A–D 覆盖层 |

**Runners-up considered**:

- `gantt_chart` | rejected for P02: 早期阶段起止日期不精确，用里程碑而非时长
- `pyramid_chart` | rejected for P12: 六层是流程先后而非层级重要性
- `icon_grid` | rejected for P13: 要求极简、不用图标卡片
- `roadmap_vertical` | rejected for P14: 页面需要"已完成 / 后续"两栏对照，自由设计

---

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Layout pattern | Acquire Via | Status | Reference | text_policy | page_role |
| -------- | --------- | ----- | ------- | ---- | -------------- | ----------- | ------ | --------- | ----------- | --------- |
| 01-gpu-sm-subcore-overview.jpg | 3270×1116 | 2.93 | GPU→SM→subcore 三层架构图 | Diagram | #19 Image floating in whitespace with thin frame and caption | user | Existing | curryGPU 架构总览 | | |
| fig11-target-pipeline.png | 1964×1070 | 1.84 | subcore 目标流水线 v2 | Diagram | #19 Image floating in whitespace with thin frame and caption | user | Existing | subcore 7 级目标流水线 | | |

> Group D 说明：两张都是信息密集的架构图（no-crop），本身就是内容，不适合再叠加覆盖层；deck 风格要求极简白底，因此不使用 Group D。

---

## IX. Content Outline

> v3（2026-10-30）：以已实现内容为主，减少未实现的设想。公司项目脱敏为 A–D；FML 与 GPGPU-Sim 移植注明由合作者开发；后续计划不写日期。

- **P01 封面**
- **P02 一年工作总览**：三条线 + 时间轴
- **P03 GPU 体系结构**
- **P04 为什么重构**：旧 RTL 四个结构问题；目标结构图；前期探索（暂缓）
- **P05 subcore 实现**：7 个大级模块；S4 四张预约表；变长路径队列与 credit；级间事件通道
- **P06 重构方法与结果**
- **P07 领域现状**（简讲）
- **P08 问题的提出**：三类漏检的真实案例
- **P09 已实现的检查工具**：逐指令比对、网表结构检查、断言与验收门禁
- **P10 FML 框架结构**：模块 / 事件 / task；适合作结构规格的四点；GPGPU-Sim 移植（合作者）
- **P11 路线 B 实验**：边界规格结构（Fetch / Decode、同拍路径、偏差）；实验流程与结果；两个发现
- **P12 设计—验证五层框架**
- **P13 设计侧**：A（学习）、B（验证 scoreboard）
- **P14 验证侧**：验证环境目录结构与 tc_base 写法；C 负责的验证；D 数模混仿
- **P15 总结与后续计划**：已完成；公司流程的启发；四条后续方向

---

## X. Speaker Notes Requirements

- **Filename**: 与 SVG 同名（`01_cover.md` …）
- **Total duration**: 10 分钟；每页 40–70 秒，第 7、8、10 页略长
- **Style**: 正式、口语化书面语
- **Purpose**: report

---

## XI. Technical Constraints Reminder

1. viewBox `0 0 1280 720`；背景用 `<rect>`
2. 文本换行用 `<tspan>`，禁止 `<foreignObject>`
3. 透明度用 `fill-opacity` / `stroke-opacity`，禁止 `rgba()`
4. 禁止 `mask`、`<style>`、`class`、`textPath`、`animate*`、`script`、`<g opacity>`
5. 文本用 Unicode 原字符；XML 保留字符转义
6. `marker-end` 仅三角 / 菱形 / 圆，`<marker>` 放 `<defs>`，`orient="auto"`
7. `clipPath` 仅用于 `<image>`
