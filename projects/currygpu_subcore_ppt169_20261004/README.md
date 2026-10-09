# CurryGPU subcore 流水线图 · drawio 源文件

按 `01-gpu-sm-subcore-overview` 的画法重画：用概念名（Warp Scheduler、Scoreboard、Register File）而不是 RTL 实例名，框内用小表格和槽位示意，箭头只带简短标签，反馈用虚线。RTL 模块名只出现在下表的对照列里。

## 两种视图

| 视图 | 文件 | 回答的问题 | 排布 |
|---|---|---|---|
| 架构视图 | 00–08、12（S0 取指细节）、13（S1 + S2 细节） | 有哪些模块、怎么连、各自保存什么状态 | 按功能排，反馈环往回画 |
| 流水线视图 | 09、10（现状）、11（目标） | 一条指令第几拍到哪里、寄存器边界在哪 | 按时间从左到右，竖条是时钟沿 |

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
| `sources/11-target-pipeline.drawio` | **目标结构（未实现）**：大流水线套小流水线。7 个大级（`subcore_fetch` … `subcore_wb`）及各自的小流水线（黑横条是小级寄存器；同一拍组合完成的功能用灰色虚线框框在一起、中间不画横条；S1 的 IB read + decode 为一拍，拍末写 head FIFO；S3 的 payload decode、take lane mask、route 为一拍，S2/S3 reg 只寄存 warp 号与 ITS 状态，完整指令由 S1 按寄存的 warp 号从 head FIFO 送 S3；S0 为三级：arbitrate + tag 比较 → L0I 数据 SRAM 读 → IB 写，缓存统一用 SRAM 同步读）、大级边界寄存器、流控（全流水线逐级组合握手，S2 发射 = 选中 & credit & rdy，本阶段不用 skid buffer）；写回结构：S1 head 为每 warp 2 项 FIFO（S1/S2 级间寄存器，触发器，同一 warp 可每拍发射），ITS 状态与分支/汇合序列归 S2，S3 读 S2 已寄存的 ITS 状态取 lane mask 并按延迟分流（固定延迟进 S4、变长进单元队列），S4 allocate 查读口表和按写口（B0、B1、P）分的写回拍表并预约、读级固定 3 拍，SW 固定延迟按预约拍写回、不设结果队列，变长单元在队头申请下一拍读口并有防饿死保留；S2 发射条件为显式 SB + 隐式 SB（MEMBAR、CCTL、SETMAXREG、ERRBAR、BRANCH、INIT，功能状态归执行单元，S2 只留一位）；已寄存的反向事件通道（4 条原有通道加清隐式 SB 的 `ev_*_done`，每个来源一条）、各级拥有的状态 | 规范初稿：curryGPU 本地 `document/2026-10-05-subcore-rtl-structure-spec.md` |
| `sources/12-s0-fetch.drawio` | S0 取指的**目标**三级（2026-10-08 定，未实现）：s0 选 + tag 比较（tag 在寄存器）→ s1 L0I 数据 SRAM 同步读 → s2 处理结果并写 IB；每 warp 在途位取代全局锁、IB 空位 credit 预约、L1I 不收 miss 时逐级反压（ready 须为寄存器输出）、1RW SRAM 回填写优先；IB 为 S0 → S1 的大级边界；底部为命中与反压的逐拍例子。现状两级版本见提交 `ef62769` | 讲解见 curryGPU 本地 `document/2026-10-08-s0-fetch-spec.md` 第 8 节；生成脚本 `document/tools/gen-12-s0-fetch.py` |
| `sources/13-s1-s2-issue.drawio` | S1 + S2 的**目标方案**（2026-10-08，未实现）：S1 一拍补 head（credit：现有项数 + 未处理 consumed ≤ 2，译码 + 预译码）→ 每 warp 2 项 head FIFO（S1/S2 级间寄存器，触发器，32 × 255 位 ≈ 1 KB）；S2 单拍环 ① eligible ×16 → ② pick（`sel_case`）→ ③ issue = 选中 & credit_ok & rdy_s3，不查读口 / 写口；S2 拥有的状态（生命周期与 hold 表、stall / scoreboard / credit、age、ITS 与分支 FSM）；S2/S3 reg 只含 warp 号与 ITS 状态，完整指令由 S1 按寄存的 warp 号从 head FIFO 跨过 S2 送 S3（绿线）；S3 一拍；4 条寄存的反向事件；底部为同一 warp 每拍发 1 条的逐拍例子；灰色虚线为待讨论项 | 规范 §1、§3、§11 第 5、7 条；生成脚本 curryGPU 本地 `document/tools/gen-13-s1-s2-issue.py` |
| `sources/09-cycle-timeline.drawio` | 时序图：一条 IntAdd 逐拍经过的单元与时钟沿锁存的状态、VALU 启动拍与操作数来源、换 warp 无气泡与常量未命中保持、VALU 完成拍 | `ifetch_ib.v`、`sched_cggty_select.v`、`exec_pipe_top.v`、`exec_valu.v`、`rf_sram_bank.v` |

06 到 08 的契约、不变量与待核实问题见 curryGPU 仓库 `docs/design/ai-rtl-study/scoreboard-loop-contract.md`。

## 流水线标记

全套图用同一组段号，黑色圆形徽标标在对应的框上：

| 段号 | 名称 | 出现位置 | 状态在哪里 |
|---|---|---|---|
| ① | Fetch | 00、10 | 按 warp slot（Instr Buffer） |
| ② | Decode | 00、01、09、10（子段 ②a Refill Pick、②b Decode、②c Head hold） | 按 warp slot（head ×16） |
| ③ | Schedule | 00、02、09、10（子段 ③a Eligible、③b Pick、③c Allocate、③d Issue） | 按 warp slot（stall 计数、scoreboard 计数器） |
| ④ | Group select | 00、03、09、10 | 按 warp slot（lane PC、splinter、BX） |
| ⑤ | Execute | 00、04、09、10 | 按功能单元的级 |
| ⑥ | Write back | 00、04、09、10 | 按写口仲裁 |
| ⑦ | Release | 00、06、09、10 | 按 warp slot（scoreboard 计数器） |

寄存器边界画在 10 上（粗竖条为发射路径上的时钟沿，细竖条为 VALU 级间寄存器），逐拍例子画在 09 上。这些拍数按 curryGPU `main` `73534bd2` 与 PR 38（`rtl-stevehxli-2`）的 RTL 读出，没有仿真。要点：取指授权到调度器看到 head 共 3 拍（L0I 响应寄存器、IB、head）；head 之后到功能单元入口全是组合；换 warp 没有气泡，同一 warp 每 2 拍最多发 1 条；常量未命中保持逻辑存在但 `head_const_tag_hit` 恒为 1，不会触发；VALU 读 RF 收集操作数为 +0/+1/+2 拍；VALU 6 级，IntAdd / BitLogic / Shift 的 tap 为 6，FpConvert 4（MIO 3），FpScalar / IntMul 4；scoreboard 的 release 在完成当拍即对 eligible 可见，计数器在沿上提交；每个 bank 1 个写口。curryGPU 仓库中的 `docs/design/ai-rtl-study/subcore-pipeline-from-rtl.md` 基于 2026-09-14 的旧 RTL，其中的气泡与 tap 结论已过时。

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

1. 各周期由读 RTL 推出，没有波形验证。RF 读请求在 issue 当拍是否一定被授权、SALU / SFU / Xlane / LSU / CBU 的入口与完成拍数、branch redirect 与 BSSY 等汇合指令的确切拍数，均未核实。
2. IntAdd 的 tap 6 与性能模型 `int_add = 6` 数值一致；有新鲜源时 RTL 的启动推后 1 拍以上，性能模型如何计入这部分尚未核对。
3. 03 的 slot 内部连接（lane 表、splinter 表、BX 表）按功能归纳，没有逐端口核对。
4. 07 的两个验证场景和 08 中"不经过 EXIT 的退休之后计数器是否为 0"都没有仿真结论。
5. 00 中分支重定向画为从 ITS 回到取指，分支结果由 Branch / Reconverge 产生；RTL 里这部分状态机分布在 `subcore_top`、`its_top` 和 `sm_top`，图中做了合并。
