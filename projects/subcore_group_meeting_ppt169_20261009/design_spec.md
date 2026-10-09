# subcore_group_meeting - Design Spec

> Human-readable design narrative. Machine-readable contract: `spec_lock.md` (wins on divergence).

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | curryGPU subcore 流水线结构整理与 AI 生成 RTL 的启示 |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 16 |
| **Design Style** | B) General Consulting + clean technical |
| **Target Audience** | 课题组组会：体系结构 / 硬件方向同学与老师 |
| **Use Case** | 组会汇报，20–25 分钟 |
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
- **Tone**: 严谨、清楚、工程化；结论先行，状态标签（已实现 / 已定·未实现 / 待定）贯穿全篇

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#FFFFFF` | Page background |
| **Secondary bg** | `#F4F6F9` | Card / panel background |
| **Primary** | `#1F3A5F` | Titles, header bar, key blocks |
| **Accent** | `#E07A1F` | Key numbers, "已实现" tag |
| **Secondary accent** | `#2A7F9E` | "已定·未实现" tag, secondary emphasis |
| **Body text** | `#222222` | Body |
| **Secondary text** | `#666666` | Captions |
| **Tertiary text** | `#999999` | Footer, page number |
| **Border/divider** | `#D8DEE6` | Card borders, dividers |
| **Success** | `#2E7D32` | PASS / 0 差异 |
| **Warning** | `#C62828` | 现状问题、待定 / 待补 |

## IV. Typography System

**Typography direction**: concord modern CJK sans + monospace for signals/code.

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

**Baseline**: body = 18px (dense). Page title 30px, subtitle 22px, annotation 14px, cover title 52px, chapter opener 40px, hero number 36px, footer 11px.

## V. Layout Principles

- **Header**: y 0–110. Left primary-color vertical bar (6×36) at x 56, title 30px bold at y 72; optional one-line takeaway 15px secondary text at y 100.
- **Content**: y 130–668.
- **Footer**: y 690. Left "curryGPU · subcore 组会 · 2026-10-10" 11px tertiary; right page number.
- Status tags: small pill `rect rx=10`, h 22, 12px text — 已实现 (accent fill), 已定·未实现 (secondary accent fill), 待定 (warning outline).
- Universal: margin 56px, block gap 24–32px, icon-text gap 10px. Cards: gap 24px, padding 20–24px, radius 8px, border `#D8DEE6`.
- Figure pages: figure in a framed panel with caption; asymmetric 7:3 split (figure : takeaways).

## VI. Icon Usage Specification

Library `tabler-outline`, stroke width 2. Inventory: `cpu`, `stack-2`, `git-commit`, `git-compare`, `alert-triangle`, `bulb`, `checks`, `flask`, `robot`, `route`, `lock`, `clock`, `target`, `bug`, `ruler`, `timeline`, `help`, `code`.

## VII. Visualization Reference List

Catalog read: 71 templates

| Page | Template | Path | Summary-quote (verbatim from `charts_index.json`) | Usage |
| ---- | -------- | ---- | ------------------------------------------------- | ----- |
| P02 | agenda_list | `templates/charts/agenda_list.svg` | "Pick for table of contents, meeting agendas, or presentation roadmap — numbered items + brief description + duration / owner per row." | 三部分议程 + 时长 |
| P04 | timeline | `templates/charts/timeline.svg` | "Pick for 3-8 milestone events on a horizontal time axis (no duration)." | 10-04 至 10-09 六个节点 |
| P12 | kpi_cards | `templates/charts/kpi_cards.svg` | "Pick for 4-8 standalone numeric metrics shown as overview cards (2x2 or 1x4) — exec summary opener, dashboard headline, quarterly recap, results-at-a-glance." | 验证结果关键数字 |
| P15 | vertical_list | `templates/charts/vertical_list.svg` | "Pick for 3-6 numbered key points each with a short description — design principles, core tenets, action items, key takeaways, recommendations, executive summary points." | 方法论要点 |

Runners-up considered:
- `roadmap_vertical` | rejected for P04: 节点无状态指示，横向更适合 16:9 并留出下方说明区
- `numbered_steps` | rejected for P15: 要点不是先后步骤，而是并列原则
- `bullet_chart` | rejected for P12: 指标没有目标基线，只是结果数字
- `layered_architecture` | rejected for P07: 已有 11 号图，直接用原图更准确

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Layout pattern | Acquire Via | Status | Reference |
| -------- | ---------- | ----- | ------- | ---- | -------------- | ----------- | ------ | --------- |
| fig10-pipeline-datapath.png | 1964x945 | 2.08 | P03 现状数据通路 | Diagram | #19 Image floating in whitespace with thin frame and caption | user | Existing | 现状流水线 |
| fig11-target-pipeline.png | 1964x1070 | 1.84 | P07 目标结构总图 | Diagram | #46 Background image + bordered "lens" rectangle highlighting a sub-region | user | Existing | 目标 7 大级 |
| fig12-s0-fetch.png | 1581x1032 | 1.53 | P08 S0 取指 | Diagram | #3 Right-third image + left text body | user | Existing | S0 三级 |
| fig13-s1-s2-issue.png | 1564x1064 | 1.47 | P09 S1/S2 发射 | Diagram | #2 Left-third image + right text body | user | Existing | S1/S2 |

All four are dense diagrams → `no-crop`. Group D coverage: P07 uses #46 (lens rectangle on S2 single-cycle loop).

## IX. Content Outline

Part 0 — 开场
- **P01 封面** (anchor): 标题"curryGPU subcore 流水线结构整理"；副标题"从读 RTL 到可验证的重构，以及 AI 生成 RTL 的启示"；汇报人 dyf · 2026-10-10。
- **P02 目录** (anchor, agenda_list): 01 背景与动机 / 02 subcore 目标结构与实现 / 03 验证 / 04 AI 生成 RTL 的观察 / 05 下一步。

Part 1 — 背景
- **P03 为什么要重新整理** (dense): 左上 subcore 位置（GPU→GPC→TPC→SM→4 subcore，16 warp slot）；fig10 现状图；四个问题卡：组合长链 35–45 级、跨级组合读、hold 位散落于 6000+ 行 subcore_top、死逻辑与隐式约定（单 warp 峰值 IPC 0.5）；底注 PR #38 只统一写法未统一结构。
- **P04 一周时间线** (dense, timeline): 10-04 研究框架 + SB 契约；10-05 读 RTL 划分流水线、同步 1558 提交、规范初稿；10-06/07 EDA 环境 + iadd3 基线；10-08 SRAM 三级、S0 规范、Phase 2 提交；10-08/09 d1 + lockstep；10-09 S1/S2 发射条件定稿。

Part 2 — subcore 结构与实现
- **P05 章节页** (breathing): "大流水线套小流水线" + 一句话：向前只走寄存器、向后只走寄存事件、每份状态一个主人。
- **P06 结构原则** (dense): 左：小级握手模板表（rdy/handshake/ena/vld）；右：三条边界规则 + S2 唯一单拍环白名单（7 项）+ 一大级一模块。
- **P07 目标流水线** (dense): fig11 大图，lens 框住 S2；底部 7 级色条 S0…SW 一行职责。
- **P08 S0 取指** (dense): 左文：现状 vs 目标对照（全局锁每 2 拍查 1 次 → 按 warp 在途位；c0 组合大锥 → tag/SRAM/写 IB 三级；延迟 3→4 拍）；右 fig12。
- **P09 S1/S2 发射** (dense): 左 fig13；右：2 项 head FIFO（32×255 位≈1 KB，同 warp 每拍发射）；发射 = 选中 & credit_ok & rdy_s3；显式 SB + 隐式 SB 表（6 列）。
- **P10 S3/S4/SW 与事件通道** (dense): 左：allocate 四项检查 → 过了 allocate 拍数全固定、无结果队列（对比 MICRO 2025）；右：事件通道表（5 行，ev_complete 现状同拍组合标红）。
- **P11 已落地的改动** (dense): 两栏：Phase 2 `0fe1c31d4`（S1 ANSI+分节、vld/rdy/handshake_s0；sel_case 一次编码；8 个 sched_* 文件；+3834/−3747；lint 少 8 警告）| d1 未提交（subcore_issue_hold.v 142 行；setmax/membar/cctl/ERRBAR 搬入；+40/−48）。

Part 3 — 验证
- **P12 验证方法与结果** (dense, kpi_cards): KPI：100,158 信号 0 差异；5/5 负载 PMU 逐行相同；35→17 分钟；348,288 基线拍数不变。下方：方法（逐信号比 vs A/B 拍数比）+ lockstep 原因一行 + 待补（d1 wave_compare、sm_context）。

Part 4 — AI 生成 RTL
- **P13 观察（上）** (dense): 4 卡：模型缺结构层；风格脚本引入组合环（872e78e2）；契约推翻验证计划（IADD3 测不到 SB）；结论随代码过时（1558 提交）。每卡：现象 + 启示。
- **P14 观察（下）** (dense): 4 卡：AI 会讲错→依据可追溯（MEMBAR 更正）；先找已有机制（FSM→hold 表→显式/隐式 SB）；测量基础设施不确定（lockstep）；死逻辑靠结构规则暴露。
- **P15 方法论与研究框架** (dense, vertical_list): 5 条做法；右侧 4 级消融条件 nl → +model → +style → +diagram，缺陷根因 7 类；状态：只有模板。

Part 5 — 收尾
- **P16 下一步与待讨论** (dense): 三栏：近期（提交 d1、d2 分支/ITS 进 S2、ctx 格式）| 改拍数的结构改动（S2–S4 一起重构、2 项 FIFO、ev_complete +1、MEMBAR 拆分、S0 三级）| 想请大家讨论（F：拉长流水线是否接受；单 warp 取指 0.67；AI 实验第一个模块选哪个）。

## X. Speaker Notes Requirements

- One note per page in `notes/total.md`, `#` heading per page matching SVG basename.
- Total ~22 min; conversational, conclusion-first; purpose: report + invite discussion.

## XI. Technical Constraints Reminder

viewBox `0 0 1280 720`; `<rect>` backgrounds; `<tspan>` wrapping, no `foreignObject`; no `rgba`, `mask`, `<style>`, `class`, `textPath`, `animate*`, `script`; raw Unicode, escape `& < >`; `clipPath` only on images; no `<g opacity>`; inline styles only.
