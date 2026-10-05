# CurryGPU subcore 流水线图 · drawio 源文件

按 `01-gpu-sm-subcore-overview` 的画法重画：用概念名（Warp Scheduler、Scoreboard、Register File）而不是 RTL 实例名，框内用小表格和槽位示意，箭头只带简短标签，反馈用虚线。RTL 模块名只出现在下表的对照列里。

## 两种视图

| 视图 | 文件 | 回答的问题 | 排布 |
|---|---|---|---|
| 架构视图 | 00–08 | 有哪些模块、怎么连、各自保存什么状态 | 按功能排，反馈环往回画 |
| 流水线视图 | 09、10 | 一条指令第几拍到哪里、寄存器边界在哪 | 按时间从左到右，竖条是时钟沿 |

两种视图用同一套模块名、段号和配色。段号 ①–⑦ 是逻辑步骤，不是时钟拍；拍数只在流水线视图里出现。

## 文件与对照

| drawio 源文件 | 内容 | 对应 RTL |
|---|---|---|
| `sources/00-subcore-overview.drawio` | subcore 总览：取指、译码、调度、ITS、执行、写回、寄存器堆，以及依赖反馈和分支重定向 | `subcore_top.v` |
| `sources/01-decode.drawio` | IB → Refill Pick → 128 位指令字（含 21 位控制位）→ 每 warp 一个 head | `subcore_decode.v` |
| `sources/02-warp-scheduler.drawio` | Eligible 判定 → 选一个 warp → 资源再确认 → 发射，与 Scoreboard 的加减关系 | `sched_top.v`、`sched_warp_ctrl.v` |
| `sources/03-its.drawio` | lane PC 表 → 按 PC 分组 → splinter 表 → 选最小 PC 的 group；BX 表与分支 | `its_top.v` |
| `sources/04-execute.drawio` | 分发、各功能单元及级数、写回仲裁、寄存器堆写与完成事件 | `exec_pipe_top.v`、`exec_wb_arb.v` |
| `sources/05-register-file.drawio` | 读口、写口、tensor 读、初始化 walker | `rf_bank_top.v` |
| `sources/06-scoreboard.drawio` | 计数器表、issue +1、completion −1、generation 检查、一个依赖等待的示例 | `sched_sbx_scoreboard.v`、`sched_completion_event_lane_decode.v` |
| `sources/07-read-release-lane.drawio` | 读释放通道由四个来源共用，优先级与 async 的单项挂起槽，以及两个验证场景 | `subcore_top.v:3510-3550` |
| `sources/08-slot-lifecycle.drawio` | warp slot 生命周期中计数器和 generation 的变化 | `sched_warp_ctrl.v`、`sched_sbx_scoreboard.v` |
| `sources/10-pipeline-datapath.drawio` | 流水线数据通路：IB ‖ head ‖ t 拍发射组合区（Eligible → Pick → Allocate → ITS → Dispatch → RF 读地址）‖ RF 读出与操作数收集 ‖ VALU stage 0–5 与写回 ‖ RF 阵列与 scoreboard 计数器；两条下一拍可见的反馈、常量未命中时的保持、branch redirect | `subcore_top.v`、`sched_cggty_select.v`、`exec_pipe_top.v`、`exec_valu.v`、`exec_wb_arb.v`、`rf_sram_bank.v` |
| `sources/09-cycle-timeline.drawio` | 时序图：一条 IntAdd 逐拍经过的单元与时钟沿锁存的状态、VALU 启动拍与操作数来源、换 warp 无气泡与常量未命中保持、VALU 完成拍 | `ifetch_ib.v`、`sched_cggty_select.v`、`exec_pipe_top.v`、`exec_valu.v`、`rf_sram_bank.v` |

06 到 08 的契约、不变量与待核实问题见 curryGPU 仓库 `docs/design/ai-rtl-study/scoreboard-loop-contract.md`。

## 流水线标记

全套图用同一组段号，黑色圆形徽标标在对应的框上：

| 段号 | 名称 | 出现位置 | 状态在哪里 |
|---|---|---|---|
| ① | Fetch | 00、10 | 按 warp slot（Instr Buffer） |
| ② | Decode | 00、01、09、10（子段 ②a Refill Pick、②b Decode、②c Head hold） | 按 warp slot（head ×12） |
| ③ | Schedule | 00、02、09、10（子段 ③a Eligible、③b Pick、③c Allocate、③d Issue） | 按 warp slot（stall 计数、scoreboard 计数器） |
| ④ | Group select | 00、03、09、10 | 按 warp slot（lane PC、splinter、BX） |
| ⑤ | Execute | 00、04、09、10 | 按功能单元的级 |
| ⑥ | Write back | 00、04、09、10 | 按写口仲裁 |
| ⑦ | Release | 00、06、09、10 | 按 warp slot（scoreboard 计数器） |

寄存器边界画在 10 上（粗竖条为发射路径上的时钟沿，细竖条为 VALU 级间寄存器），逐拍例子画在 09 上。这些拍数按 curryGPU `origin/main` `73534bd2` 的 RTL 读出，没有仿真。要点：发射路径上只有 IB → head 一处寄存器，head 之后到功能单元入口全是组合；换 warp 没有气泡，上一拍发射的 warp 常量未命中时最多保持 4 拍；VALU 读 RF 收集操作数为 +0/+1/+2 拍；VALU 6 级，IntAdd / BitLogic / Shift 的 tap 为 6，FpConvert 4（MIO 3），FpScalar / IntMul 4；完成事件在 t 拍则计数器在 t+1 更新。curryGPU 仓库中的 `docs/design/ai-rtl-study/subcore-pipeline-from-rtl.md` 基于 2026-09-14 的旧 RTL，其中的气泡与 tap 结论已过时。

01 底部的子段表给出 ②a/②b/②c 各自保存的状态、吞吐和延迟。02 中 ③a 到 ③d 外面的虚线框表示它们在同一拍内由寄存器状态组合得出，不是四个时钟周期。

## 配色约定

沿用同仓库 `currygpu_architecture_ppt169_20261001` 的约定。

| 用途 | fill | stroke |
|---|---|---|
| 调度 / 控制 / 仲裁 | `#E1D5E7` | `#9673A6` |
| 存储 / 寄存器堆 / 表 | `#FFF2CC` | `#D6B656` |
| 数据通路 / 译码 / 执行 | `#DAE8FC` | `#6C8EBF` |
| 外部接口 / 上下游模块 | `#D5E8D4` | `#82B366` |
| completion event / 地址 | `#FFE6CC` | `#D79B00` |
| 重定向 | 红色虚线 | `#B85450` |

## 导出

没有 drawio CLI，也没有用 drawio 渲染过。本地导出：

```bash
for f in sources/*.drawio; do
  drawio -x -f svg --crop -o "exports/$(basename "${f%.drawio}").svg" "$f"
done
```

## 校验范围

只做了几何检查：XML 可解析、方块不重叠、框内小格子都在父框内、文字不超框、所有边的折线按显式出入口计算后不穿过无关方块。没有在 drawio 里目视确认，个别连线或标签位置不理想时手动拖动即可。

## 未核实项

1. 各周期由读 RTL 推出，没有波形验证。RF 读请求在 issue 当拍是否一定被授权、SALU / SFU / Xlane / LSU / CBU 的入口与完成拍数、常量未命中保持的确切拍数，均未核实。
2. IntAdd 的 tap 6 与性能模型 `int_add = 6` 数值一致；有新鲜源时 RTL 的启动推后 1 拍以上，性能模型如何计入这部分尚未核对。
3. 03 的 slot 内部连接（lane 表、splinter 表、BX 表）按功能归纳，没有逐端口核对。
4. 07 的两个验证场景和 08 中"不经过 EXIT 的退休之后计数器是否为 0"都没有仿真结论。
5. 00 中分支重定向画为从 ITS 回到取指，分支结果由 Branch / Reconverge 产生；RTL 里这部分状态机分布在 `subcore_top`、`its_top` 和 `sm_top`，图中做了合并。
