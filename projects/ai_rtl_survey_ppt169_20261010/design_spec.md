# ai_rtl_survey - Design Spec

> Human-readable design narrative. Machine-readable contract: `spec_lock.md` (wins on divergence).

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | AI 生成 RTL：现有思路与可对比的 baseline |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 16 |
| **Design Style** | B) General Consulting + clean technical |
| **Target Audience** | 课题组组会：体系结构 / 硬件方向同学与老师 |
| **Use Case** | 组会文献综述，约 20 分钟；回应"要找能对比的 baseline" |
| **Created Date** | 2026-10-10 |

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| **Format** | PPT 16:9 |
| **Dimensions** | 1280×720 |
| **viewBox** | `0 0 1280 720` |
| **Margins** | left/right 56px, top 40px, bottom 36px |
| **Content Area** | x 56–1224, y 130–668 |

## III. Visual Theme

- **Style**: General Consulting, clean technical; light theme
- **Theme**: Light theme
- **Tone**: 严谨、结论先行；每页标题下一行写本页结论；文献统一写"名称 · 会议 年份 · arXiv 号"

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#FFFFFF` | Page background |
| **Secondary bg** | `#F4F6F9` | Card / panel background |
| **Primary** | `#1F3A5F` | Titles, header bar, key blocks |
| **Accent** | `#E07A1F` | Key numbers, "我们" 的位置 |
| **Secondary accent** | `#2A7F9E` | Secondary emphasis, route tags |
| **Body text** | `#222222` | Body |
| **Secondary text** | `#666666` | Captions, citations |
| **Tertiary text** | `#999999` | Footer, page number |
| **Border/divider** | `#D8DEE6` | Card borders, dividers |
| **Success** | `#2E7D32` | 已覆盖 / 有 |
| **Warning** | `#C62828` | 空白 / 失败数字 |

## IV. Typography System

**Typography direction**: modern CJK sans + monospace for paper IDs and signal names.

| Role | Chinese | English | Fallback tail |
| ---- | ------- | ------- | ------------- |
| **Title** | `"Microsoft YaHei", "PingFang SC"` | `Arial` | `sans-serif` |
| **Body** | `"Microsoft YaHei", "PingFang SC"` | `Arial` | `sans-serif` |
| **Emphasis** | same as Body (bold) | — | — |
| **Code** | — | `Consolas, "Courier New"` | `monospace` |

- Title: `"Microsoft YaHei", "PingFang SC", Arial, sans-serif`
- Body: same as Title
- Emphasis: same as Body
- Code: `Consolas, monospace`

**Baseline**: body = 18px (dense). Page title 30px, subtitle 22px, annotation 14px, citation 13px, cover title 52px, hero number 36px, footer 11px.

## V. Layout Principles

- **Header**: y 0–110. Primary vertical bar (6×36) at x 56, title 30px bold at y 72; one-line takeaway 15px secondary text at y 100.
- **Content**: y 130–668.
- **Footer**: y 690. Left "curryGPU · AI 生成 RTL 综述 · 2026-10" 11px tertiary; right page number.
- Route tags: pill `rect rx=10` h 22, 12px white text on secondary accent: 路线一 … 路线四 / 验证线.
- Universal: margin 56px, block gap 24–32px, icon-text gap 10px. Cards: gap 24px, padding 20px, radius 8px, border `#D8DEE6`.
- Literature cards: name bold 18px; second line 13px secondary "会议 年份 · arXiv"; then 1–2 lines 15px idea; last line "与我们" 14px accent.

## VI. Icon Usage Specification

Library `tabler-outline`, stroke width 2. Inventory: `robot`, `database`, `stack-2`, `route`, `checks`, `clock`, `search`, `chart-bar`, `alert-triangle`, `target`, `flask`, `list-check`, `bulb`, `code`, `git-compare`, `users`, `file-text`, `cpu`, `ruler`, `timeline`.

## VII. Visualization Reference List

Catalog read: 71 templates

| Page | Template | Path | Summary-quote (verbatim from `charts_index.json`) | Usage |
| ---- | -------- | ---- | ------------------------------------------------- | ----- |
| P03 | isometric_stairs | `templates/charts/isometric_stairs.svg` | "Pick for 4-7 ascending stages emphasizing growth/maturity progression visually. Skip for flat sequential steps (use numbered_steps) or formal hierarchy (use pyramid_chart)." | 中间表示层级 5 级阶梯：自然语言 → 模块拓扑 → 参考模型 / IR → 微架构意图 → 流水级 + 契约 + 验证 |
| P12 | horizontal_bar_chart | `templates/charts/horizontal_bar_chart.svg` | "Pick for ranking 5-12 items, especially with long labels. Skip if <=8 short-label items (use bar_chart)." | 各 benchmark 上最好结果（%），标注指标不同不可横比 |
| P13 | harvey_balls_table | `templates/charts/harvey_balls_table.svg` | "Pick for qualitative scoring grid using 0-100% Harvey balls (vendor/skill assessment). Skip for binary checkmarks (use feature_matrix_table) or numeric values (use basic_table)." | 代表工作 × 5 个维度的覆盖程度 |
| P14 | layered_architecture | `templates/charts/layered_architecture.svg` | "Pick for 3-4 horizontal architecture layers (presentation/service/data), 2-4 module cards per layer, each card = title + 1-line description (description required, even if source brief). Skip if no per-module descriptions (use icon_grid) or no horizontal layering (use module_composition)." | baseline 三层：benchmark / 方法 / 模型 |
| P16 | vertical_list | `templates/charts/vertical_list.svg` | "Pick for 3-6 numbered key points each with a short description — design principles, core tenets, action items, key takeaways, recommendations, executive summary points. Skip for icon-style cards (use icon_grid) or sequential steps (use numbered_steps)." | 下一步 |

**Runners-up considered**:

- `pipeline_with_stages` | rejected for P03: 中间表示是层级而非数据流，每级没有"产物"
- `feature_matrix_table` | rejected for P13: 覆盖程度是部分覆盖（HINT 有意图层但无契约），二值打勾会失真
- `comparison_table` | rejected for P14: baseline 是分层组合，不是 2–4 个产品的对比

## VIII. Image Resource List

No images. All diagrams are hand-drawn SVG.

## IX. Content Outline

### Part 1: 问题

#### Slide 01 - Cover
- **Title**: AI 生成 RTL：现有思路与可对比的 baseline
- **Subtitle**: 文献调研 · 为 curryGPU subcore 的结构框架找对照组
- **Info**: dyf · 课题组组会 · 2026-10

#### Slide 02 - 组会意见与本次目标
- **Layout**: 左 4 右 6：左侧组会意见与本次三个问题；右侧我们的论点（三层：性能模型 / 结构框架 / 验证框架）
- **Content**: 意见：需要能对比的 baseline。三个问题：别人给 LLM 什么输入？做到多大规模？怎么判定对？论点：性能模型不够，需结构框架 + 验证框架。证据 G2 首轮：同 warp 连续发射，mix 64 / control_flow 212 处错，iadd3 PASS 盖住。

#### Slide 03 - 分类总览：按给 LLM 的中间表示排一条轴
- **Visualization**: isometric_stairs
- **Content**: 5 级阶梯，每级列代表工作；另注四条路线 + 验证线；"我们"在第 5 级。

### Part 2: 四条生成路线

#### Slide 04 - 路线一：数据与模型
- **Content**: RTLCoder、CodeV、CraftRTL、OriGen、VeriReason、CodeV-R1；结论：训练数据与奖励都来自模块级 testbench；VerilogEval v2 已 89–98%，分不出结构能力。

#### Slide 05 - 路线二：agent / 多 agent 流程
- **Content**: 待第三路检索（VerilogCoder、MAGE、Spec2RTL、QiMeng 等）；结论：闭环靠 testbench / 编译器 / 波形反馈。

#### Slide 06 - 路线三：结构化中间层（最接近我们）
- **Content**: ROME、SysVCoder、VeriGraphi（RV32I）、分层 IR（Architectural Sketch + Operational Spec）、AGON（nOP IR，OoO 核）、HINT；结构只到模块拓扑 / 端口 / 算子。

#### Slide 07 - 两个关键证据：表示层比模型重要
- **Content**: Representation Bottleneck：6 种 IR × 3 个前沿模型 × 202 任务，仿真通过率 3%–88% 随 IR 变，同 IR 下换模型 < 1.25 倍。HINT：7 个算子 7/7 合规，Direct C2RTL 5/5、C2HLSC 1/5；Vortex VPU。

#### Slide 08 - 路线四：参考模型 + 形式等价（"模型够用"的对照组）
- **Content**: FormalRTL、AutoVeriFix+、C2HLSC、SymRTLO；只覆盖数据通路，控制与时序契约不在范围。正是我们要对比的条件 `model`。

### Part 3: 验证与时序

#### Slide 09 - 验证线：SVA、testbench、波形反馈
- **Content**: AssertLLM、FVEval、AutoBench/CorrectBench、FVDebug、SeqFeed、DUET、Veri-Sure；结论：LLM 看不出跨周期行为（SeqFeed/DUET）；断言依附信号不依附流水级。

#### Slide 10 - 时序契约语言：给人用，没接 LLM
- **Content**: Anvil、Filament、PDL、Kôika、Latency-insensitive；对照 G2 的"同 warp 发射间隔 ≥ 2"。

#### Slide 11 - 断言 / 不变量挖掘：没有微架构先验
- **Content**: GoldMine、IODINE、HARM、A-TEAM、GR1MINE、NeuroAssertion；按流水级和事件通道约束模板空间。

### Part 4: 评测与 baseline

#### Slide 12 - Benchmark 现状
- **Visualization**: horizontal_bar_chart
- **Content**: VerilogEval v2 最高约 98%；ArchXBench 16/30 = 53%（L4 起 0）；CVDP 生成 ≤ 34%；HWE-Bench 小核 > 90%、SoC < 65%；RTL-BenchLS 23% / 28% / 12%。指标不同，只看趋势。

#### Slide 13 - 空白汇总
- **Visualization**: harvey_balls_table
- **Content**: 行：Direct（VerilogCoder 类）、VeriGraphi / 分层 IR、HINT、FormalRTL、SeqFeed、Anvil、我们（目标）。列：流水级结构、状态归属 / 事件通道、时序契约、验证闭环、周期级判据。

#### Slide 14 - 可作 baseline 的组合
- **Visualization**: layered_architecture
- **Content**: benchmark 层：VerilogEval v2 / RTLLM v2（下限），CVDP（工业通用），ArchXBench / ChipVerilog（流水线）。方法层：Direct prompting、参考模型路线（FormalRTL 式）、结构 IR 路线（VeriGraphi / 分层 IR / HINT）。模型层：CodeV-R1、VeriReason（开源 7B）+ 商用模型。

#### Slide 15 - 我们的对比实验设计
- **Content**: 模块：`subcore_issue_hold`、`subcore_decode`（有参考实现与 0 差异比对工具）。条件：nl / model / model+style / model+style+diagram，再加 baseline 方法。指标：lint、端到端 PASS、逐信号波形等价、契约违例数、首个错误位置、人工干预轮数与 token。

#### Slide 16 - 下一步
- **Visualization**: vertical_list
- **Content**: 补核实；跑 baseline 方法在 ArchXBench L4 子集；选模块跑消融；把 G2 / PR 38 写成 D 记录；契约挖掘脚本原型。

## X. Speaker Notes Requirements

One note file per page in `notes/`, filename matches SVG name; 要点、过渡句、每页约 1–1.5 分钟。

## XI. Technical Constraints Reminder

1. viewBox `0 0 1280 720`; background via `<rect>`
2. Text wrapping via `<tspan>`; `<foreignObject>` forbidden
3. Transparency via `fill-opacity` / `stroke-opacity`; `rgba()` forbidden
4. Forbidden: `mask`, `<style>`, `class`, `textPath`, `animate*`, `script`, `<g opacity>`
5. Raw Unicode for symbols; escape `& < > " '`
6. Markers only in `<defs>` with `orient="auto"`
