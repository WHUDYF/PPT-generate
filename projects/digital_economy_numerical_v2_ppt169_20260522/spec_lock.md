# Execution Lock

> Machine-readable execution contract. Executor MUST `read_file` this before every SVG page.

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## colors
- bg: #FAFAFA
- secondary_bg: #F0F4F8
- primary: #1A3A5C
- accent: #C8963E
- secondary_accent: #2E6B8F
- text: #1A1A2E
- text_secondary: #6B7280
- text_tertiary: #9CA3AF
- border: #D1D5DB
- success: #2E7D32
- warning: #C62828

## typography
- font_family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif
- title_family: Georgia, KaiTi, serif
- body_family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif
- emphasis_family: Georgia, KaiTi, serif
- code_family: Consolas, "Courier New", monospace
- body: 18
- title: 30
- subtitle: 24
- cover_title: 60
- annotation: 14
- footnote: 11
- hero_number: 32

## icons
- library: phosphor-duotone
- inventory: buildings, chart-line-up, trend-down, currency-circle-dollar, database, calculator, function, graph, table, target, link-simple, graduation-cap, check-circle, lightbulb, users

## page_rhythm
- P01: anchor
- P02: dense
- P03: dense
- P04: dense
- P05: dense
- P06: dense
- P07: dense
- P08: anchor
- P09: anchor
- P10: dense
- P11: dense
- P12: breathing

## page_charts
- P02: process_flow
- P03: basic_table
- P04: basic_table
- P05: numbered_steps
- P06: numbered_steps
- P07: pros_cons_chart
- P08: dual_axis_line_chart
- P09: dual_axis_line_chart
- P10: scatter_chart
- P11: bar_chart
- P12: vertical_list

## forbidden
- Mixing icon libraries
- rgba()
- `<style>`, `class`, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<script>`, `<iframe>`, `<symbol>`+`<use>`
- `<g opacity>` (set opacity on each child element individually)
- HTML named entities in text (`&nbsp;`, `&mdash;`, `&copy;`, `&ndash;`, `&reg;`, `&hellip;`, `&bull;` …) — write as raw Unicode (`—`, `©`, `→`, NBSP, etc.); XML reserved chars `& < > " '` must be escaped as `&amp; &lt; &gt; &quot; &apos;`
