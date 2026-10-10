# subcore_group_meeting - Design Spec

> Human-readable design narrative. Machine-readable contract: `spec_lock.md` (wins on divergence).

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | curryGPU subcore 流水线结构整理与 AI 生成 RTL 的启示 |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 23 |
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

- **P01 封面** (anchor)；**P02 目录** (anchor, agenda_list)：背景 / 目标结构 / 验证 / AI 生成 RTL / 用 AI 写代码：humanize / 下一步。
- **Part 1 背景**
  - P03 性能模型的结构：事件驱动，发射那一刻一次算完（候选 → 选 warp → 同一函数里算读冲突、占用、credit、写回预约、scoreboard、ready_tick）。
  - P04 为什么照它生成 RTL 会让流水线混乱：模型一个函数 vs RTL 需要的多个级；四组对照。
- **Part 2 目标结构**
  - P05 章节页 (breathing)：大流水线套小流水线。P06 结构原则。P07 目标流水线总图（图 11）。
  - P08 S0、P09 S1/S2、P10 S3、P11 S4、P12 S5、P13 SW：每页顶部一行"这一级想做什么"，左图（12–17 号 drawio），右为级内步骤与要点。
- **Part 3 验证**：P14 怎么验证整体改完的 RTL（用例、比较方法、工件、分工）；P15 目前的结果与发现。
- **Part 4 AI 生成 RTL**：P16 观察 1–4；P17 观察 5–8；P18 有效做法与研究框架。
- **Part 5 用 AI 写代码：humanize**：P19 总览与流程；P20 示例一：想法 → draft → plan；P21 示例二：一次真实的 RLCR 运行；P22 怎么用。
- **P23 下一步**：先出一版重构后的 RTL；对比手改 RTL 与性能模型生成 RTL 的差别；再讨论怎么确认这份工作可以由 AI 代替。

---

## X. Speaker Notes Requirements

- One note per page in `notes/total.md`, `#` heading per page matching SVG basename.
- Total ~22 min; conversational, conclusion-first; purpose: report + invite discussion.

## XI. Technical Constraints Reminder

viewBox `0 0 1280 720`; `<rect>` backgrounds; `<tspan>` wrapping, no `foreignObject`; no `rgba`, `mask`, `<style>`, `class`, `textPath`, `animate*`, `script`; raw Unicode, escape `& < >`; `clipPath` only on images; no `<g opacity>`; inline styles only.
