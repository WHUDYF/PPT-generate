# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## colors
- bg: #FFFFFF
- bg_secondary: #F4F6F9
- primary: #1F3A5F
- accent: #E07A1F
- secondary_accent: #2A7F9E
- text: #222222
- text_secondary: #666666
- text_tertiary: #999999
- border: #D8DEE6
- success: #2E7D32
- warning: #C62828

## typography
- font_family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif
- code_family: Consolas, monospace
- body: 18
- title: 30
- subtitle: 22
- annotation: 14
- cover_title: 52
- chapter_title: 40
- hero_number: 36
- footer: 11

## icons
- library: tabler-outline
- stroke_width: 2
- inventory: cpu, stack-2, git-commit, git-compare, alert-triangle, bulb, checks, flask, robot, route, lock, clock, target, bug, ruler, timeline, help, code, terminal-2, file-text, refresh, eye, list-check, user-check, repeat, shield-check, git-branch, users

## images
- fig11: images/fig11-target-pipeline.png | no-crop
- fig12: images/fig12-s0-fetch.png | no-crop
- fig13: images/fig13-s1-s2-issue.png | no-crop
- fig14: images/fig14-s3-dispatch.png | no-crop
- fig15: images/fig15-s4-operand.png | no-crop
- fig16: images/fig16-s5-execute.png | no-crop
- fig17: images/fig17-sw-wb.png | no-crop

## page_rhythm
- P01: anchor
- P02: anchor
- P03: dense
- P04: dense
- P05: breathing
- P06: dense
- P07: dense
- P08: dense
- P09: dense
- P10: dense
- P11: dense
- P12: dense
- P13: dense
- P14: dense
- P15: dense
- P16: dense
- P17: dense
- P18: dense
- P19: dense
- P20: dense
- P21: dense
- P22: dense
- P23: dense

## page_charts
- P02: agenda_list
- P14: vertical_list
- P22: vertical_list

## forbidden
- Mixing icon libraries
- rgba()
- `<style>`, `class`, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<script>`, `<iframe>`, `<symbol>`+`<use>`
- `<g opacity>`
- HTML named entities in text; escape XML reserved chars
