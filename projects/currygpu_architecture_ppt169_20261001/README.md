# CurryGPU 架构图 · drawio 可编辑版

把之前生成的四张 CurryGPU 整体架构图转成 drawio 源文件，便于后续手工修改并导出到 PPT。

## 目录

```
.
├── images/     原始 JPG（参考基准，不要改）
├── sources/    drawio 源文件（在这里改）
├── exports/    导出的 SVG / PNG（见下方「导出」）
└── notes/
```

## 对应关系

| drawio 源文件 | 原图 | 内容 | 原图尺寸 |
|---|---|---|---|
| `sources/01-gpu-sm-subcore-overview.drawio` | `images/01-gpu-sm-subcore-overview.jpg` | 三层总览：GPU/SoC → SM → Subcore | 3270×1116 |
| `sources/02-its-subsystem.drawio` | `images/02-its-subsystem.jpg` | ITS 子系统：per-lane PC + splinter table + rebuild walker | 2025×1080 |
| `sources/03-lsu-subsystem.drawio` | `images/03-lsu-subsystem.jpg` | LSU 子系统：L0–L5 流水 + L1D 控制域 | 1891×1080 |
| `sources/04-rf-subsystem.drawio` | `images/04-rf-subsystem.jpg` | RF 子系统：GPR / URF / P-file | 1765×1080 |

每个文件单独一页，方便单独编辑、git diff 也干净。需要合成多页文件的话，drawio 里 `Extras → Edit Diagram` 把 `<diagram>` 节点拷进同一个 `<mxfile>` 即可。

## 导出

生成这批文件的机器上没有 drawio CLI，所以 `exports/` 目前是空的。本地导出：

```bash
# drawio desktop
drawio -x -f svg -o exports/01-gpu-sm-subcore-overview.svg sources/01-gpu-sm-subcore-overview.drawio

# 批量
for f in sources/*.drawio; do
  drawio -x -f svg --crop -o "exports/$(basename "${f%.drawio}").svg" "$f"
done
```

导出成 SVG 后就能接上本仓库既有的 `svg_output → pptx` 流程（参考 `projects/gcl_trace_compression_group_meeting_20260605_ppt169_20260605/`，该项目用的是 SVG 而非 drawio）。

## 配色约定

沿用 drawio 默认调色板，和原图的 pastel 风格对应：

| 用途 | fill | stroke |
|---|---|---|
| 调度 / 控制 FSM / CBU / 重汇合 | `#E1D5E7` | `#9673A6` |
| 存储阵列 / 寄存器堆 / cache | `#FFF2CC` | `#D6B656` |
| 数据通路 / buffer / 接口字段 | `#DAE8FC` | `#6C8EBF` |
| 共享单元 / 外部接口轨 | `#D5E8D4` | `#82B366` |
| 出错 / trap / NACK | `#F8CECC` | `#B85450` |
| 地址 / 物理页 / 进位 | `#FFE6CC` | `#D79B00` |
| 位域深蓝 / 中蓝（反白字） | `#2D5F9A` / `#5B8FD4` | 同色 |

## 已知偏差

这几版是按原图**结构**复刻的，以下地方做了简化，改图时可按需补：

1. **密集小表格**（ITS 的 splinter table 行、protection 表、LSU 的 carveout tiers、divergence example）用等宽字体的多行文本块表示，不是真正的 drawio table shape。好处是改文字方便，坏处是列对齐靠空格。
2. **ITS 的 min-PC 8-way 树**画了比较器节点和结果，但没连全部叶子到节点的连线——层级太密，连上反而看不清。
3. **堆叠效果**（SM ×N、Subcore ×4、Memory Controllers、Vector ALU）用 2–3 个偏移矩形叠出来，不是真实数量。
4. **原图里一些极小的注记文字**（9px 以下）分辨率不足，有个别词是按上下文推断的，以原图为准。

## 源数据

图中的结构和参数可在 `curryGPU` 仓库里对照：

- RTL 模块层次：`rtl/src/`（`subcore_top.v`、`its_top.v`、`exec_pipe_top.v`、`rf_bank_top.v`、`sched_top.v`）
- 功能模型：`simulator/binding/native.cpp`（`NativeWarp`）、`block_state.h`（`NativeBlock`）
- 性能模型：`simulator/binding/timing_model_event_issue_*.cpp`、`machine_config.h`、`latency_table.h`
- 讲义：`docs/design/subcore-functional-model-explained.md`、`docs/design/subcore-rtl-simulator-pipeline-explained.md`
