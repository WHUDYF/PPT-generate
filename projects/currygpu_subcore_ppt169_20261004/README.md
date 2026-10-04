# CurryGPU subcore 自上而下拆解图 · drawio 源文件

按 RTL 实例层次从 `subcore_top` 向下拆解，每张图一个独立的单页 drawio 文件。

## 目录

```
.
├── README.md
└── sources/    drawio 源文件
```

## 层次与文件

| 层级 | drawio 源文件 | RTL 模块 | 内容 |
|---|---|---|---|
| L0 | `sources/00-subcore-top.drawio` | `rtl/src/subcore_top.v` | 五个子模块、glue（branch FSM、RF 初始化队列、`issue_rd_arb`、`exec_mem_issue`、`exec_cbu_issue`）、外部接口、依赖反馈与控制流反馈 |
| L1 | `sources/01-subcore-decode.drawio` | `rtl/src/subcore_decode.v` | IB refill 仲裁、decode row、head 打包、`head_q` / `head_valid_q`、trap |
| L1 | `sources/02-sched-top.drawio` | `rtl/src/sched_top.v` | lane decode → scoreboard → warp_ctrl → age_matrix → CGGTY → allocate → credit_pool |
| L1 | `sources/03-its-top.drawio` | `rtl/src/its_top.v` | 12 个 slot 的 pc / lane_state / bx / splinter / fire_retire，selected 输出，redirect |
| L1 | `sources/04-exec-pipe-top.drawio` | `rtl/src/exec_pipe_top.v` | dispatch、各执行单元、reuse cache、pending、可变写回源、`exec_wb_arb` |
| L1 | `sources/05-rf-bank-top.drawio` | `rtl/src/rf_bank_top.v` | GPR / URF / P-file / uniform predicate、两个初始化 walker、tensor URF 读 |

`rtl/src/subcore_top.v` 中的实例行号：`u_decode` 1362，`u_sched` 1461，`u_exec_pipe` 1983，`u_issue_rd_arb` 2447，`u_exec_mem_issue` 3550，`u_exec_cbu_issue` 3631，`u_its` 4055，`u_rf_bank` 4741。

## 配色约定

沿用同仓库 `currygpu_architecture_ppt169_20261001` 的约定。

| 用途 | fill | stroke |
|---|---|---|
| 调度 / 控制 FSM / 仲裁 | `#E1D5E7` | `#9673A6` |
| 存储阵列 / 寄存器堆 / 表 | `#FFF2CC` | `#D6B656` |
| 数据通路 / 译码 / 执行 | `#DAE8FC` | `#6C8EBF` |
| 外部接口 / 上下游模块 | `#D5E8D4` | `#82B366` |
| flush / trap / redirect / 事件 | `#F8CECC` | `#B85450` |
| completion event / 地址 | `#FFE6CC` | `#D79B00` |

## 导出

生成这批文件的机器上没有 drawio CLI，也没有用 drawio 渲染过，导出目录未创建。本地导出：

```bash
for f in sources/*.drawio; do
  drawio -x -f svg --crop -o "exports/$(basename "${f%.drawio}").svg" "$f"
done
```

## 校验范围

生成后只做了几何层面的检查：XML 可解析，方块无重叠，文字高度不超框，所有边的折线（按显式出入口和折点计算）不穿过无关方块。没有在 drawio 里目视过，打开后若个别连线或标签位置不理想，直接手动拖动调整即可。

## 来源与未核实项

结构来自 RTL 实例层次和 `docs/design/subcore-rtl-simulator-pipeline-explained.md`。以下几处是按端口名和讲义归纳的，没有逐信号核对：

1. L0 中 branch FSM 的输入画为 `sched_top` 的 issue（`sched_issue_valid_q / slot_q`），分支读 RF / 谓词的路径未画。
2. L0 中 `async_submit`、tensor URF 读口只在文字里说明在 `subcore_top` 层接线，没有画连线。
3. L1 `exec_pipe_top` 中 `exec_valu → fp64 / packed pipe` 画的是 VALU 源操作数行驱动并列的 fp 流水；reuse cache 的 hit / data 回到 VALU，RF 写地址用于失效，依据是 `exec_pipe_top.v:2682` 的端口连接。
4. L1 `sched_top` 中 `sched_credit_pool` 与 `warp_ctrl` / `allocate` 的连接依据讲义描述，未逐端口核对。
5. L1 `its_top` 的 slot 内部连线（pc / lane_state / bx / splinter / fire_retire 之间）按功能归纳，没有逐端口核对；`its_top` 内是否有独立的 selected-slot 选择逻辑未确认。
6. L1 `rf_bank_top` 的 `K = 4` 取自模块参数，bank 级细节（`rf_sram_bank` 内部分 bank）未展开。
