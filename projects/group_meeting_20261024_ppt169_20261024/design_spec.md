# group_meeting_20261024 - Design Spec

> Human-readable design narrative. Machine-readable contract: `spec_lock.md` (wins on divergence).

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | 两周工作汇报：对照 drawio 图重构 subcore RTL，以及以 FML 为中间 IR 的流程化方案 |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 22 |
| **Design Style** | B) General Consulting + clean technical（沿用 10-10 组会视觉） |
| **Target Audience** | 课题组组会：体系结构 / 硬件方向老师与同学 |
| **Use Case** | 组会汇报，约 25 分钟，结尾留讨论（v2：减少 RTL 细节，突出流程、前后对比与 FML 方案） |
| **Created Date** | 2026-10-24 |

---

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| **Format** | PPT 16:9 |
| **Dimensions** | 1280×720 |
| **viewBox** | `0 0 1280 720` |
| **Margins** | left/right 56px, top 40px, bottom 36px |
| **Content Area** | x 56–1224, y 130–668 |

---

## III. Visual Theme

### Theme Style

- **Style**: General Consulting, clean technical
- **Theme**: Light theme
- **Tone**: 严谨、工程化、结论先行；数字带出处；状态标签（完成 / 部分 / 未做）贯穿

### Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#FFFFFF` | Page background |
| **Secondary bg** | `#F4F6F9` | Card / panel background |
| **Primary** | `#1F3A5F` | Titles, header bar, key blocks |
| **Accent** | `#E07A1F` | Key numbers, "完成" emphasis |
| **Secondary accent** | `#2A7F9E` | Secondary emphasis, "部分 / 改了方案" |
| **Body text** | `#222222` | Body |
| **Secondary text** | `#666666` | Captions |
| **Tertiary text** | `#999999` | Footer, page number |
| **Border/divider** | `#D8DEE6` | Card borders, dividers |
| **Success** | `#2E7D32` | PASS / 0 不一致 |
| **Warning** | `#C62828` | Bugs, 未做, 漏掉的问题 |

---

## IV. Typography System

### Font Plan

**Typography direction**: concord — one CJK sans throughout, monospace for signals / commit hashes.

| Role | Chinese | English | Fallback tail |
| ---- | ------- | ------- | ------------- |
| **Title** | `"Microsoft YaHei", "PingFang SC"` | `Arial` | `sans-serif` |
| **Body** | `"Microsoft YaHei", "PingFang SC"` | `Arial` | `sans-serif` |
| **Emphasis** | same as Body (bold) | — | — |
| **Code** | — | `Consolas` | `monospace` |

**Per-role font stacks**:

- Title: `"Microsoft YaHei", "PingFang SC", Arial, sans-serif`
- Body: `"Microsoft YaHei", "PingFang SC", Arial, sans-serif`
- Emphasis: `"Microsoft YaHei", "PingFang SC", Arial, sans-serif`
- Code: `Consolas, monospace`

### Font Size Hierarchy

**Baseline**: body = 18px (dense).

| Purpose | Ratio | px |
| ------- | ----- | -- |
| Cover title | 2.9x | 52 |
| Chapter title | 2.2x | 40 |
| Page title | 1.67x | 30 |
| Hero number | 2x | 36 |
| Subtitle | 1.22x | 22 |
| **Body** | 1x | 18 |
| Annotation | 0.78x | 14 |
| Footer | 0.6x | 11 |

---

## V. Layout Principles

- **Header**: y 0–110. Primary vertical bar (6×36) at x 56, y 46; title 30px bold at y 74; optional takeaway line 15px `#666666` at y 102.
- **Content**: y 130–668.
- **Footer**: y 696. Left "curryGPU · 组会 · 2026-10-24" 11px `#999999`; right page number.
- **Status tags**: pill `rx=10`, h 22, 12px — 完成 (accent fill), 部分 / 改方案 (secondary accent fill), 未做 (warning outline).
- **Cards**: gap 24px, padding 20px, radius 8px, border `#D8DEE6`, fill `#F4F6F9` or white.
- Tables drawn with `<rect>` rows + `<text>`; header row primary fill with white text.

---

## VI. Icon Usage Specification

- **Library**: `tabler-outline`, stroke width 2.
- **Inventory**: cpu, stack-2, git-commit, git-compare, alert-triangle, bulb, checks, flask, robot, route, lock, clock, target, bug, ruler, timeline, help, code, terminal-2, file-text, refresh, eye, list-check, shield-check, git-branch, users, book, database, scale, arrows-split, chart-bar, notebook, message-question, search, file-code, transform, hierarchy, git-merge, player-play

---

## VII. Visualization Reference List

| Page | Template | Path | Summary-quote (verbatim from `charts_index.json`) | Usage |
| ---- | -------- | ---- | ------------------------------------------------- | ----- |
| P02 | kpi_cards | `templates/charts/kpi_cards.svg` | "Pick for 4-8 standalone numeric metrics shown as overview cards (2x2 or 1x4) — exec summary opener, dashboard headline, quarterly recap, results-at-a-glance." | 四步故事线 + 关键数字 |
| P09 | comparison_table | `templates/charts/comparison_table.svg` | "Pick for 2-4 plans/products compared across many feature rows (dense matrix)." | 重构前后 RTL 对照 |
| P19 | timeline | `templates/charts/timeline.svg` | "Pick for 3-8 milestone events on a horizontal time axis (no duration)." | FML 方案分阶段路线图 |

Runners-up considered:
- `process_flow` | rejected for P04/P13: 流程含反馈环和三路派生，自绘更准确
- `gantt_chart` | rejected for P17: 各阶段没有确定的起止日期

---

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Layout pattern | Acquire Via | Status | Reference |
| -------- | ---------- | ----- | ------- | ---- | -------------- | ----------- | ------ | --------- |
| fig11-v2.png | 2733x2459 | 1.11 | P05 目标流水线 v2 总图 | Diagram | #2 Left-third image + right text body | user | Existing | 11 号图 v2（10-21 版） |

Dense diagram → `no-crop`.

---

## IX. Content Outline

- **P01 封面** (anchor)。
- **P02 概览** (dense, kpi_cards)：四步故事线。
- **P03 章节一** (anchor)；**P04 重构流程**；**P05 目标图 v2**。
- **P06 章节二** (anchor)；**P07 一拍里发生了什么**（性能模型 process_issue → 一拍组合）；**P08 维护与验证的麻烦**；**P09 前后对照** (comparison_table)；**P10 优势**；**P11 痛点**。
- **P12 为什么要约束 AI** (dense)：长程实现会偏移——外部证据（标注阅读深度，不含 Build-A-Chip-Bench）、我们自己的证据、三类偏移与方案覆盖范围。
- **P13 章节三** (anchor)；**P14 FML 是什么**；**P15 新流程**；**P16 FML 规格写到哪一层**；**P17 S1 原型三组实验**；**P18 原型暴露的缺口**；**P19 路线图** (timeline)；**P20 和论文的关系**。
- **P21 从论文借来的做法** (dense)：SDHE、AmpereOne、Reflexion/JITTAC、LEC、Hawkeye、Spec Grounding 等，每条：读到什么 → 我们怎么用 → 状态。
- **P22 讨论与下一步** (dense)。

---

## X. Speaker Notes Requirements

- One note per page in `notes/total.md`, `#` heading per page matching SVG basename.
- Total ~25 min; conversational, conclusion-first; end with discussion questions.

---

## XI. Technical Constraints Reminder

viewBox `0 0 1280 720`; `<rect>` backgrounds; `<tspan>` wrapping, no `foreignObject`; no `rgba`, `mask`, `<style>`, `class`, `textPath`, `animate*`, `script`; raw Unicode, escape `& < >`; `clipPath` only on images; no `<g opacity>`; inline styles only.
