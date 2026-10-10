# 组会材料源稿：subcore 流水线结构整理与 AI 生成 RTL（2026-10-10）

用途：给组会幻灯片当事实来源。每条都标了状态：**[已实现]** 指 RTL 已改并通过验证；**[已定·未实现]** 指规范里已定、RTL 还没动；**[待定]** 指还在讨论。拍数如果没写"波形确认"，就是读 RTL 推出来的。

来源：`document/` 下各讨论稿、`docs/design/ai-rtl-study/`、dyf 的 3 个提交（`13389eca5`、`73534bd2f`、`0fe1c31d4`）、分支 `subcore-pipeline-structure` 上未提交的 d1 改动、`.build/cmp-d1*` 的比对输出、PPT-generate 提交历史。

---

## 1. 背景

### 1.1 curryGPU 与 subcore 的位置

- curryGPU 是 GPU 的 RTL 加模拟器工程，包括功能模型、性能模型（`simulator/binding/`）和 Verilator SoC 模型。
- 层次：GPU → GPC → TPC → SM → 4 个 subcore。波形里 subcore 的路径是 `...g_sm[0].u_sm.g_subcore[0].u_subcore`。
- 一个 subcore 有 **16 个 warp slot**（`WarpSlotsPerSubcore = 16`；PPT 旧图写的 12 已经改掉，提交 `cefe277`）。
- 取指的归属：`ifetch_frontend`（仲裁、L0I、IB、每 warp 取指状态）是每个 subcore 一份（`ifetch_top.v:271-272`）。4 个 subcore 真正共用的只有 L1I、miss queue、TLB。

### 1.2 为什么要重新整理结构

下面几点都是读 RTL 看到的现状问题（main `73534bd2` / `0fe1c31d`）：

- **发射路径是一条很长的组合链。** head 寄存器之后，eligible → age → 选择 → allocate → ITS → exec_dispatch → RF 读地址 → VALU 入口全在同一拍完成，估计 35–45 级逻辑。发射路径上只有 IB → head 这一处寄存器边界。
- **跨级组合读取。** S2（`sched_top`）组合读 exec 内部的 `collect_fire`、`rd_busy`、`valu_wb_warps/banks`，等于把写口预约藏在了调度器里。scoreboard 在完成的同一拍组合释放（`released = counter_q - decrement`）。
- **状态散落。** 挡住发射的位（MEMBAR、CCTL、SETMAXREG、ERRBAR、分支、RF 初始化等）散在 `subcore_top`（6000 多行）里，全部与进 `sched_top.head_valid_i`（`subcore_top.v:2177`），从波形上看不出是谁挡的。
- **死逻辑与隐式约定。** `hold_for_fill` 依赖的 `head_const_tag_hit` 恒为 1，所以永远不触发。单项 head 的补充用寄存后的 valid，结果同一 warp 只能隔拍发射，单 warp 峰值 IPC 是 0.5，和性能模型 `ready_tick = tick + max(1, stall)` 对不上。保留屏障号 6 会让 warp 静默挂住，对应的 trap 没有接出来。
- **PR #38（stevehxli 的 `rtl-stevehxli-2`）只统一了写法，没有统一结构。** 它用 30 个 `tools/rtl_*.py` 脚本做格式化，比如 ANSI 端口、大写参数。哪些逻辑切成一级、级间寄存器怎么命名，它没有规定。

目标：先写一份 "架构 → 流水线 → RTL" 的结构规范，再在**行为不变**的前提下逐步把现有 RTL 整理成这个结构，同时记录 AI 生成和整理 RTL 时的经验。

---

## 2. 工作时间线

| 日期 | 做了什么 | 产出 |
|---|---|---|
| 10-04 | 建 AI 生成 RTL 的研究记录框架；写 scoreboard 依赖环契约；按旧 RTL 画 subcore 图 00–08 | 提交 `13389eca5`：README、experiment/defect 模板、`scoreboard-loop-contract.md`。PPT-generate 图 00–08 |
| 10-05 | 读 RTL 得出流水线划分；发现本地 main 落后远程 1558 个提交，同步后按新 RTL（`73534bd2`）重读；调研 PR 38；写规范初稿；画目标流水线 11 号图 | 提交 `73534bd2f`（`subcore-pipeline-from-rtl.md`）；`document/` 下 local-vs-remote、pipeline-reread、PR38、target-mapping、structure-spec；图 09、10 改为新时序，新增 11 |
| 10-06 ～ 07 | 11 号图加上逐级握手流控、allocate 写口预约、ITS 状态归 S2；搭 EDA 环境（无 root：Verilator 5.052、CUDA 13.1 pip 包、conda g++ 11.2）；跑出 iadd3 基线波形 | `2026-10-07-eda-env-setup.md`；基线 348,288 拍、kernel 89,279 拍 |
| 10-08 | 定下缓存统一用 SRAM 三级；写 S0 取指规范和 12 号图；写 11 号图讲解稿（待定 A–G）；**Phase 2：S1、S2 保持行为的整理**；写 d1/d2 计划 | 提交 `0fe1c31d4`（11 个文件，+3834/−3747）；`s0-fetch-spec`、`fig11-walkthrough`、`phase2-progress`、`s2cd-plan`；图 12、13 |
| 10-08 ～ 09 | **d1：把 hold 位搬进新模块 `subcore_issue_hold`（未提交）**；发现 SoC 仿真不确定，加 lockstep 开关；在 6 个负载上做 A/B 比对 | `rtl/src/subcore_issue_hold.v`（142 行）；`document/patches/runtime-lockstep.patch`；`model_compare.sh` |
| 10-09 | 定下 S1 head 为每 warp 2 项 FIFO（当天一度改成单项，又改回）；S2 发射条件改为"显式 SB + 隐式 SB"（作废"生命周期 + hold 表"）；定下 S2 最终检查清单、stall 与 allocate 停顿的规则、S2→S3 的指令走法；更正了 MEMBAR GPU 范围的说法 | `2026-10-09-s1-s2-issue-conditions.md`；规范 §11 第 5、7、14、15、16 条；PPT 提交 `63e69da`…`8822eed` |

---

## 3. Subcore 结构与实现

### 3.1 总原则：大流水线套小流水线 [已定·未实现]

- **大流水线：** 7 个大级每拍并行工作，各自处理不同 warp 的指令：S0 fetch → S1 decode → S2 issue → S3 dispatch → S4 operand → S5 exe_\<unit\> → SW wb。
- **小流水线：** 每个大级内部的写法照公司 DSP 设计 `DSP.v` 的任务流水线：

  | 信号 | 定义 |
  |---|---|
  | `rdy_sN` | `ena_s(N+1)` |
  | `handshake_sN` | `rdy & vld` |
  | `ena_sN` | `handshake \| ~vld` |
  | `vld_sN` | 寄存器 |
  | 数据 `x_sN` | 在上游握手时采样 |

- **与 DSP 的区别：** DSP 外层是互斥的任务 FSM，subcore 外层没有。DSP 式 FSM 只用在"一次做一件、要做多拍"的单元上，例如 SFU、XLANE、分支序列、上下文切换。
- **三条边界规则：**
  1. 向前只走寄存器（`vld` 加已寄存的 payload）。
  2. 向后只走已寄存的事件通道，目的级晚 +1 拍看到。
  3. 每份状态只有一个主人，只有主人能写。
- **S2 是唯一的单拍环。** 发射沿上更新、下一拍选 warp 就要读到的状态构成白名单，只能放在 S2：
  - head 消耗
  - stall 载入
  - SB +1
  - credit −1
  - `last_issued` / `yield`
  - 隐式 SB 置位
  - ITS 状态更新
- **一大级一模块** `subcore_<级名>`，`subcore_top` 只做连接。这样模块端口就是该级的契约，跨级组合读取在结构上写不出来。

### 3.2 各级

**S0 · 取指（`ifetch_frontend` 归 S0）**

| 项 | 现状 [读 RTL 得出] | 目标 [已定·未实现，2026-10-08] |
|---|---|---|
| 小级 | c0：仲裁（16 级串行比较链）+ 36 位地址加法 + 64 路 tag 比较 + 1024 位 64 选 1，同一拍组合完成。c1：作废 / 命中 / 未命中处理，写 IB | s0：选 warp + tag 比较（tag 留在寄存器）。s1：L0I **数据 SRAM 同步读**。s2：写 IB 或发 miss |
| 吞吐 | 全局锁 `lookup_inflight_q`（lookup_busy），**每 2 拍才查一次**，每次最多 2 条，平均每拍 ≤ 1 条，正好等于发射上限 | 在途位按 warp 设，不同 warp 每拍都能查，多 warp 时取指带宽最多每拍 2 条。同一 warp 最快每 3 拍查一次，约 0.67 条/拍 [待定：要不要补] |
| 状态 | fetch PC、epoch（2 位，每次跳转 +1）、occupied、miss_wait/pending、饿死计数（16）；L0I 64 行 × 1024 位 = 8 KB，全相联；IB 每 warp 8 项、2 个 bank，带 head 缓存 | 同左；每 warp 一个小 FSM：IDLE → RUN ⇄ MISS |
| 仲裁顺序 | 饿死 > deadline 小（IB 中 Σ(1+stall)）> IB 条数少 > warp 号小 | 不变 |
| 取指资格 | IB 至少空 2 格（`count ≤ 6`），每 4 拍最多发 1 个 miss | IB 空位用 credit 预约：现有 + 在途 + 2 ≤ 8 |
| 反压 | `miss_rsp_pending_q` 停车位 | L1I 不收 miss 时逐级反压，L1I 的 ready 必须是寄存器输出；SRAM 为 1RW，回填写优先，回填 FSM 提前一拍寄存"下一拍要写" |
| 延迟 | 取指授权到 S2 看到 head 共 3 拍 | 共 4 拍，只在分支跳转、IB 清空后显现 |
| 冲刷 | epoch 比较，已经是规范 §8 的写法 | 不变 |

S0/S1 的大级边界就是 IB：`vld = count != 0`，S1 用组合 pop 握手取队头。

**S1 · 译码 / head（`subcore_decode`）**

- 现状：每 warp 1 项 head（`head_q`、`head_valid_q`），轮转补充，每拍最多补 1 个 warp。**同一 warp 两次发射至少隔 2 拍**（波形确认：第 329,602 和 329,604 拍）。
- 目标 [已定·未实现，2026-10-09]：**每 warp 一个 2 项 head FIFO**，作为 S1/S2 级间寄存器。
  - 用触发器：S2 每拍要同时读 16 个 warp 的第 0 项，SRAM 做不到。
  - 大小：每项 255 位（`HEAD_BITS` = 251 + 4 位取指错误），16 × 2 = 32 项，8160 位 ≈ **1 KB**（现状单项 4080 位）。
  - 补充：按 `ev_head_consumed`（+1 拍）以 credit 方式补，现有项数 + 未处理事件数 ≤ 2。第 2 项盖住 2 拍的补充环，同一 warp 可以每拍发射，与性能模型一致。
  - 约束：IB 读出 + 译码必须一拍完成，否则要 3 项。
  - 预译码字段（源寄存器、写哪些写口、写回 offset、隐式 SB 种类、非法编码）在 S1 寄存好，S2 不再译码。
  - 可压缩：128 位原始指令只有 S3 用，压缩后每项约 127 位 [待定]。
- 已做 [已实现，`0fe1c31d4`]：
  - ANSI 端口，宽度用头部参数（不同于 PR 38 的字面值写法）。
  - DSP 式的分节布局。
  - 加了 `vld_s0 = refill_grant`、`rdy_s0 = 1`、`handshake_s0`，refill 选择改用 `handshake_s0`。

**S2 · 发射（`sched_*` → 目标 `subcore_issue`）**

- **发射条件 = 显式 SB + 隐式 SB** [已定，2026-10-09]。机制与原版相同，只整理归属：
  - 显式 SB：编译器分配，每 warp 6 个计数器（9 位，cap 256），后续指令按 wait mask 等待；另有 stall（4 位）、depbar、`sb_headroom`。固定延迟依赖靠 stall，不经过 SB。
  - 隐式 SB：硬件分配，每 warp 一位，挡住该 warp 后续所有指令。

    | 列 | 置位 | 清除 |
    |---|---|---|
    | MEMBAR | 发射 | 屏障完成 & (非 CTA 范围 \| drained) |
    | CCTL.IVALL | 发射 | L1 作废完成（正常挡 1 拍） |
    | SETMAXREG | 发射 | SM 调整完成 |
    | ERRBAR / CGAERRBAR | 发射，装入 29 / 92 拍 | 倒数到 0（实测值） |
    | BRANCH | 分支 FSM 启动 | FSM 回到 Idle |
    | INIT | launch | RF 清零 walker 完成 |

  - 不属于 SB 的：`slot_valid`；EXIT 要求 drained；ACQBULK 要求 `~dep_wait`；FENCE.VIEW.ASYNC.T 改为每 warp 一个在途 TMEM 计数器 [待定接法]；`its_available`；`stop_issue`。
  - 就绪条件：`eligible = slot_valid & head_valid & stall==0 & wait_mask_clear & sb_headroom & depbar_ok & 隐式SB全0 & credit_ok & its_available & grid_dep_ok & (~exit | drained)`。
  - 原则：多步的功能状态归执行该操作的单元，S2 只留一位关卡。按这条原则，原版只有 ACQBULK、ERRBAR 完全符合；MEMBAR 的 7 位协议状态、TQ/async 前门都不符合。
- **S2 发射 = 选中 & credit_ok & rdy_s3** [已定，§11 第 14 条]。原版 `sched_allocate` 各项检查的去向：

  | 检查 | 去向 |
  |---|---|
  | `rd_ok`、`wb_ok`（含 `wb_yield_q`）、`fu_ok` | 删除，移到 S4 allocate |
  | `const_ok` | 死逻辑，删除 |
  | `barrier_ok`（保留号 6） | 移到 S1 预译码，走 `head_bad` 陷入 |
  | `sb_headroom`、credit | 保留 |

- **换 warp 气泡：** 已经没有了（提交 `be606010`，`sel_valid_o = issue_ok`）。旧图上的"1 拍气泡"已改。
- **ITS 状态与分支 / 汇合序列归 S2。** 现状是整个 subcore 一个分支 FSM，16 个状态，约 1100 行，不成模块，最少约 7 拍。每 warp 分组表 8 项，BX 16 项。
- 已做 [已实现，`0fe1c31d4`]：
  - `sched_cggty_select` 的优先级只编码一次：`sel_case` ∈ HOLD/SWITCH/STICKY/OLDEST/NONE，三个输出都由它派生。原来是三处 if 链，PR 38 还复制成了三份。
  - 8 个 `sched_*` 文件改为 ANSI + 参数化 + DSP 分节。
  - lint 0 错误，少了 8 条警告。
- d1 [已实现·未提交]：新建 `rtl/src/subcore_issue_hold.v`（142 行），把 setmax / membar / cctl 的 block 位和每 warp 8 位 ERRBAR 计数原样搬进去。
  - 置位、清除、同拍优先级与原版相同：setmax、membar 同拍 done 优先；cctl 同拍 issue 优先；launch/retire 清整行。
  - `subcore_top` 里 AND 进 `head_valid_i` 的那 5 项换成 `~(issue_hold | tmem_fence_hold)`（改动 +40/−48 行，`rtl_sources.f` +1 行）。
  - MEMBAR 的 pend / wait / ok 子状态仍留在 `subcore_top`。

**S3 · 分发（`subcore_dispatch`）** [已定·未实现]

- S2/S3 reg 只寄存 `issue_valid`、warp 号和 S3 要用的 ITS 状态，不做 255 位的 16 选 1。
- 完整指令由 S1 按寄存的 warp 号在 t+1 从 head FIFO 送到 S3（向前方向，越过 S2）。
- S3 一拍完成 payload 译码、取 lane mask、按延迟分流：固定延迟进 S4，变长进单元队列。
- 现状 `exec_dispatch` 纯组合，与 S2 同拍。

**S4 · 读操作数（`subcore_operand`）** [已定·未实现]

- allocate 每拍最多放行 1 条固定延迟指令，放行前检查：
  1. 读级入口空闲；
  2. 每个 bank 一张读口表，3 拍读窗口内读口够用；
  3. 每个写口一张写回拍表（B0、B1、P，以及按需的 URF、UP），用移位寄存器实现：查 `~wb_q[t][offset]`，每拍 `>>1`；
  4. 按需加执行单元的完成拍表。
- 不通过就拉低 `rdy`。**过了 allocate，读、启动、完成、写回的拍数全部固定**，stall 一直有效，不需要结果队列。
- 和 MICRO 2025（Huerta 等）模拟器的区别：MICRO 2025 用结果队列，写回拍不确定，依赖指令可能读到旧值，所以本方案不用。
- stall 规则（§11 第 15 条）：stall 计数器只在当拍 `ena_s4_0 = 1` 时减 1，先全局冻结。还没有用例验证。
- 变长单元在队头申请下一拍的读口，加防饿死保留（阈值 N 待定）。
- 现状：2 个 bank、每 bank 每拍读 1 个、写 1 个；`collect_*_q` 一项（6 × 1024 位）；启动拍按新鲜源数为 +0 / +1 / +2。

**S5 执行 / SW 写回**

- VALU 6 级，tap 分别是：

  | 类别 | tap |
  |---|---|
  | IntAdd / BitLogic / Shift | 6 |
  | FpConvert | 4（MIO 形式 3） |
  | FpScalar / IntMul | 4 |

  IntAdd 的 6 与性能模型 `int_add = 6` 对齐。旧文档写的 4 级、tap 1 已过时。
- 每拍最多 2 个结果（wb2）；SALU 4 级；SFU 每 slot 一个 FSM（Idle → Inject → Gather → Writeback），已经接近目标写法。
- SW 目标：固定延迟结果在预约拍直接写入；写回优先级为 已预约 > uniform > 变长 > SM 共享单元；变长结果只能用当拍未被预约的写口。

### 3.3 事件通道（向后，全部寄存，+1 拍）[已定·未实现]

| 通道 | 源 → 目的 | 现状 |
|---|---|---|
| `ev_head_consumed` | S2 → S1 | 已是寄存 |
| `ev_complete` | SW → S2 | **现状同拍组合释放**，目标 +1。只影响变长依赖，代价待测 |
| `ev_credit_return` | S5 → S2 | credit pool 已寄存 |
| `ev_redirect` | S2 → S0 | 现状走 BRA 状态机 |
| `ev_membar_done`、`ev_l1_inv_done`、`ev_setmax_done`、`ev_rf_init_done`、`ev_tmem_done` | 各单元 → S2，清隐式 SB | 现状多为组合往返，例如 cctl 请求与完成同拍（`sm_top.v:1372`） |

规则：每个来源一条通道，不合并成总线；带 warp 号和 `wslot_gen`，迟到的事件丢弃。

### 3.4 缓存统一做法 [已定 2026-10-08·未实现]

- 数据阵列 ≥ 1 KB 用 SRAM（同步读、1RW、统一行为模型），小于 1 KB 留在触发器里。
- 查找分三级：s0 查 tag → s1 读数据 → s2 使用。
- 在途位按发起者设，不用全局锁。
- 回填与查找共用端口，回填提前一拍寄存"下一拍要写"。
- 适用对象：L0I（8 KB）、L0C、L1I tag（128 组 × 4 路）、peregrine_cache、gmmu_walk_cache。

### 3.5 编码规范要点 [已定]

- 命名：
  - 级前缀 `subcore_<级>`；
  - 控制信号 `vld_sN_<级>`；
  - 数据 `<级>_<名>_sN`；
  - 事件 `ev_<名>_vld`；
  - 对外端口用"源+目的"前缀，如 `IFSC_`、`SCLSU_`。
- 格式：ANSI 端口、列对齐，**端口宽度用参数**。
- 注释只保留 4 类：分节标题、每级功能编号、端口组名、编码说明。设计理由放在 `docs/design/`。
- 复位：只给 `vld`、FSM、计数器、所有权状态加复位，宽数据寄存器不复位。
- 冲刷：按 warp 的 epoch。
- 计数器：统一用 `subcore_counter`，接口照 DSP 的 counter（INC / DEC / MIN / MAX / OVERFLOW / UNDERFLOW）。

---

## 4. 验证方法与结果

### 4.1 方法

- 模型：2 SM 波形模型，构建命令 `make soc-build SOC_PROFILE=profiles/curry2.json SOC_THREADS=4 SOC_TRACE=1`，约 5 分钟。
- 负载：`test/` 下的端到端 CUDA 用例（`local_iadd3` 等），由 `run-soc-regression` 运行。
- **逐信号波形比对**（`document/tools/wave_compare.py`）：
  - 范围 `u_subcore`，约 10 万个信号，逐个比较同名信号的变化序列；
  - 改名或新增的信号单独列为 `ONLY_BASE` / `ONLY_TEST`；
  - 单次约 10 分钟。
- **A/B 拍数比对**（`document/tools/model_compare.sh`）：参考模型与被测模型并行跑同一组负载，比较每个 kernel 的 PMU 行和 PASS/FAIL。默认开 lockstep；设 `TRACE_WINDOW` 时同时抓波形。
- 只能用于"保持行为"的步骤。会改拍数的步骤（S2 到 S4 一起重构、MEMBAR 拆分、`ev_complete` +1）只用端到端用例验证，不能逐信号比。

### 4.2 iadd3 基线（10-07）

- 拍数：PASS，全程 348,288 拍，kernel 89,279 拍，共发射 288 条（每 SM 144 条），墙钟 1032 s。
- 波形确认的一条 IADD3（opcode `0x011`，发射拍记为 t = 332,851）：

  | 拍 | 发生的事 |
  |---|---|
  | t | `issue_valid`、`valu_launch`、`collect_capture`、`rd0_en`、`rd1_en` 同时为 1，说明 S2 → ITS → dispatch 全是组合 |
  | t+1 | bank 0 再读一次（两个源在同一 bank） |
  | t+2 | `collect_fire`，VALU 启动 |
  | t+3 … t+8 | 6 级 |
  | t+8 | 写 bank 0，发完成事件 |

- 同一 warp 两次发射间隔 ≥ 2 拍，与单项 head 的分析一致。
- 待查：t+9、t+11 各有一次 bank 1 写，来源不明。

### 4.3 Phase 2 结果（`0fe1c31d4`，S1 + S2-a + S2-b）

- iadd3 PASS，总拍数 348,288、kernel 89,279，都与基线相同。
- **100,158 个信号 0 差异，没有信号消失**。新增 4 个：`vld_s0`、`rdy_s0`、`handshake_s0`、`sel_case`。

### 4.4 仿真不确定性与 lockstep（10-09）

- 现象：同一个参考 `Vsoc` 二进制跑两次，会落在两条时间线之一：18770 / 89279，或 20843 / 89251。差异在第一个 kernel 之前、还没发射任何指令时就出现了。
- 原因在 `runtime/session.h`，不在 RTL：
  - backend 引擎线程（`Device::loop`）每片自己推进 4096 拍；
  - 每个 CUDA 请求之后，`scrub_freed()` 会唤醒这个线程；
  - CUDA 程序的下一个请求落在哪一片边界，取决于操作系统调度。
- 处理：加可选开关 `CURRYGPU_LOCKSTEP=1`。打开后由等待者自己推进模拟器，scrub 同步执行。
  - 补丁只留在本地，不提交：`document/patches/runtime-lockstep.patch`。
  - lockstep 下的拍数不能当性能结果用。
- 结果：iadd3 参考模型跑两次、d1 跑一次，都是**总 349,783 拍、kernel 89,228 拍**，全部 PASS。
- 附带效果：单次运行从约 35 分钟降到约 17 分钟。

### 4.5 d1 比对（`.build/cmp-d1-iadd3`、`.build/cmp-d1-ls`，lockstep）

参考模型为 `.build/soc/ref-0fe1c31d`，被测模型为 `.build/soc/d1`。

| 负载 | kernel PMU 行数 | 结果 |
|---|---|---|
| `local_iadd3` | 3 | 逐行相同，PASS（iadd3 kernel 89,228 拍） |
| `local_convergence_regions`（分支 / ITS） | 37 | 相同，PASS |
| `local_memory_order`（MEMBAR） | 55 | 相同，PASS（单次约 2 小时） |
| `local_mbarrier_hardware_probe` | 13 | 相同，PASS |
| `local_l1_store_policy` | 5 | 相同，PASS |

- 早一轮的 `.build/cmp-d1` 没开 lockstep，`memory_order` 那次不可比，正是这次比对引出了 4.4 的不确定性问题。
- 两边的 iadd3 都抓了 `trace.fst`。讨论稿里没有记录 d1 的逐信号比对结论，上会前要确认是否已经跑过 `wave_compare.py`。
- 规范要求 d1 时加跑 `rtl/regression/sm_context`（ctx 保存格式），没有看到这项的结果。

---

## 5. AI 生成 RTL 的观察与灵感

### 5.1 研究框架（`docs/design/ai-rtl-study/`，`13389eca5`）

- **实验记录**（E 编号）字段：
  - 模块、条件、重复序号、模型、prompt 版本；
  - 每轮的 RTL 提交、lint、回归结果和失败阶段；
  - 代价：轮数、token、人工干预次数和分钟数。
- **四种实验条件**，逐级叠加输入，用来做消融：
  1. `nl`：只给自然语言；
  2. `model`：加功能 / 性能模型代码；
  3. `model+style`：再加代码规范；
  4. `model+style+diagram`：再加流水线图。
- **缺陷记录**（D 编号）字段：症状、模型符号与 RTL 符号的对应、根因，以及"本应被 style guide / diagram / contract 中的哪一个挡住"。
- **根因候选类别**：`cycle-semantics`、`boundary`、`ordering`、`abstraction-gap`、`structure`、`interface`、`style`。
- 现状：目前只有模板（E000 / D000），还没有填写任何实验或缺陷实例。下面的观察来自这几天的整理过程，可以作为第一批缺陷的素材。

### 5.2 观察（带实例）

1. **性能模型缺一层结构，AI 照着它生成 RTL 就会出结构问题（`abstraction-gap` / `structure`）。**
   - 性能模型把 eligible → … → dispatch 当成一个事件，写口预约放在发射时，没有算上读冲突。
   - 按它生成的 RTL 就在 S2 组合读后级信号；写回窗口只覆盖 FpConvert / FpScalar / IntMul，IntAdd 这类 tap 6 的指令不在检查里。
   - 启示：生成 RTL 之前，要先给出"哪些逻辑在哪一级、级间寄存器是什么"这一层（11 号图加上规范）。光有模型不够。
2. **风格脚本不保证行为不变（`style` 引入功能缺陷）。**
   - PR 38 的最后一个提交 `872e78e2` 把 `ifetch_ib.v` 中 `next_deadline` 的顺序计算改成 if/else 链。
   - 结果：分支里读到未赋值的自身，形成组合环或锁存器；同拍 push + pop 时漏掉了 pop 的减法。
   - main 和 PR 38 的前 11 个提交都是对的。
   - 启示：任何"只改写法"的提交都必须做等价性检查。这正是我们逐信号比对的理由。
3. **契约要从代码里读出来，而且会推翻原计划。**
   - 写 scoreboard 契约时发现：IADD3 链的依赖完全由 stall count 保证，不产生 scoreboard 流量，所以原定的"用 IADD3 依赖链验证 SB 环"根本测不到它。验证计划因此改为 S1a–S4 分级。
   - 同时整理出 8 条不变量（I1–I8，其中 6 条已有 trap 标志），以及一个可达性待查的组合：同一指令的读写 barrier 用同一个 id 时会多释放。
4. **AI 读 RTL 的结论会随代码过时（`cycle-semantics`）。**
   - 本地 main 落后 1558 个提交时，"换 warp 有 1 拍气泡""VALU 4 级、IntAdd tap 1"这些结论都已经不成立，图和文档要全部重读。
   - 启示：每条结论都写上依据的提交号和行号，切换基准后逐项复核。所有讨论稿都在开头注明了基准提交。
5. **AI 也会讲错，需要可追溯的依据才能纠正。**
   - 讲 MEMBAR 时说 GPU 范围在 SM 层"Drain 等 load 排空"，这是错的：`sm_membar_ctl.v:121-123` 在批次含 GPU 范围时直接转 Fence，在途的 load 由其后的 ERRBAR 等待。
   - S1 head 一天之内从"2 项"改成"单项"，又改回"2 项"，原因是改动时漏看了它与性能模型 `max(1, stall)` 的关系。
   - 启示：结论要带依据（RTL 行号、模型代码行），才能快速推翻或确认。
6. **抽象层次的选择比细节更重要。**
   - 原先设计的是"两层 FSM、HOLD 带原因码"，后来改成"生命周期 + hold 表"，最后定为"显式 SB + 隐式 SB"。
   - 定稿的依据是：原版 RTL 里这些位本来就是"发射置位、事件清除"，和 scoreboard 同一个模式。用 FSM 就得照抄优先级、加互斥断言，还要复制分支 FSM 的下一状态逻辑。
   - 启示：先在现有代码里找已经存在的统一机制并命名它，不要另造一套抽象。
7. **测量基础设施本身可能不确定（验证方法）。**
   - d1 第一次比对出现差异，查下来是 runtime 线程调度引起的，与 RTL 无关（见 4.4）。
   - 启示：A/B 比对之前，先确认同一个二进制重复跑结果一致，否则拍数差异无法归因到 RTL。
8. **死逻辑和静默挂起，是读代码比跑仿真更容易发现的一类问题。**
   - 实例：`head_const_tag_hit` 恒为 1；`trap_reserved_barrier_slot_o` 接到 unused；`selection_changed_o` 悬空；`guard_capture_q` 是死寄存器。
   - 这类问题回归测试测不出来，需要"状态有没有主人"这类结构规则来暴露。

### 5.3 有效的规则 / 做法

- **小步走，保持行为，每步都有可重复的工件。** 每一步只做一件事，都留下：
  - 参考模型二进制；
  - lockstep 下的拍数；
  - 逐信号比对报告（0 差异，新增信号单独列出）。
- **把"只改写法"和"改拍数"分成不同的提交**，用不同的验证手段：前者逐信号比，后者用端到端用例。
- **用模板和结构让违例写不出来。**
  - 一大级一模块，端口只放寄存器输出和事件通道；
  - `rdy` 只能是下一级的 `ena`、常数 1 或外部寄存器输出；
  - 优先级只编码一次（`sel_case`）。
- **规范里的每条决定都写上依据和"已定 / 待定"状态**，作废的方案保留并删除线标出（例如 §11 各条），方便 AI 和人对齐上下文。
- **讨论稿和代码分开。** 讨论稿放在 git 排除的 `document/`，图放在 PPT-generate，图由脚本生成（`gen-12/13`），渲染成 PNG 目视检查后再推送。

---

## 6. 遗留问题 / 下一步

**近期（保持行为的整理）**

1. 提交 d1（`subcore_issue_hold`）：先确认逐信号比对和 `sm_context` 的结果，再做提交，并更新 `rtl/regression/assertions/subcore_top_assertions.sv` 里的层级路径。
2. d2：把分支 / CONV 序列（约 1100 行）和 `its_top` 搬进 `subcore_issue`；`fr_*` 的重定向作为 `ev_redirect` 的源头。
3. 定 ctx 保存格式：A 方案按子模块各自拼接，格式改变；B 方案保持原格式不变。建议用 A，用 `sm_context` 往返测试验证。
4. S2-e：把 payload 译码挪到 S3；端口按"源+目的"统一改名。

**会改拍数的结构改动（只用端到端用例验证）**

5. S2 到 S4 一起重构：删掉 S2 的 rd/wb/fu 检查，建 S4 allocate 的读口表和写回拍表。两者必须同时做，否则会同拍写同一写口。
6. S1 改为 2 项 head FIFO。
7. `ev_complete` 改为 +1 拍，在访存密集用例上测量代价，并同步改性能模型。
8. MEMBAR 协议位拆到访存侧，代价是放行晚 1 拍。
9. S0 改为三级、L0I 数据用 SRAM。

**待定 / 未核实**

- 11 号图讲解稿的待定 C（变长队列的主人）、E（result reg 与 SW 之间是否多一拍），以及 F：目标结构把发射到写回拉长了，stall 数要加大、单 warp 依赖链会变慢，是否接受。
- 单 warp 取指 0.67 条/拍要不要补；回填频繁时是否改用 1R1W。
- 前门（TQ、async、访存、CBU）的 credit 种类；分支 FSM 是保持整个 subcore 一个，还是每 warp 一个。
- allocate 参数：读窗口 3 拍、表长（估算 VALU 10 位、SALU 8 位）、防饿死阈值 N。新 RTL 出来后按波形逐类确认。
- 读 RTL 时留下的未核实项：P1 RF 读当拍是否一定被授权；P3 SALU / SFU / XLANE / LSU / CBU 的拍数；P6 ITS；P8 常量保持拍数；P9 性能模型如何计读口拍数。scoreboard 契约中的 O1'、O2、O6，以及 V1、V2 场景。
- AI 研究框架还没有填任何实例：要按四种条件做第一个模块的生成实验，并把第 5.2 节的实例补成 D 记录。

---

## 7. 可用图表清单

drawio 源文件目录：`/home/dyf/PPT-generate/projects/currygpu_subcore_ppt169_20261004/sources/`（索引见同级 `README.md`；最新提交 `8822eed`，2026-10-09）。

| 文件 | 内容 | 适合放在哪部分 |
|---|---|---|
| `00-subcore-overview.drawio` | subcore 总览（现状） | 背景 |
| `01-decode.drawio` … `08-slot-lifecycle.drawio` | 译码、调度器、ITS、执行、RF、scoreboard、读释放 lane、slot 生命周期（现状架构视图） | 背景 / 契约 |
| `09-cycle-timeline.drawio` | 一条 IntAdd 的逐拍时序（现状） | 背景：组合长链 |
| `10-pipeline-datapath.drawio` | 现状数据通路与寄存器边界 | 背景：为什么重构 |
| `11-target-pipeline.drawio` | **目标结构**：7 个大级、小流水线、边界寄存器、事件通道、owns | 第 3 部分主图 |
| `12-s0-fetch.drawio` | S0 目标三级取指，带逐拍例子（现状两级版本在提交 `ef62769`） | S0 |
| `13-s1-s2-issue.drawio` | S1 head FIFO 与 S2 单拍环、显式 / 隐式 SB、事件通道 | S1/S2 |

生成脚本：`/home/dyf/curryGPU/document/tools/gen-12-s0-fetch.py`、`gen-13-s1-s2-issue.py`，直接写上面的 drawio 文件。

已有的 PNG 渲染都是 `/tmp` 下的临时检查图，`exports/` 目录不存在：

| PNG | 时间 | 对应 |
|---|---|---|
| `/tmp/f11.png` | 10-09 19:04 | 11 号图最新版（另有局部图 `/tmp/f11a.png` 17:37、`/tmp/f11c.png` 19:04） |
| `/tmp/t13.png` | 10-09 19:03 | 13 号图最新版（另有 `/tmp/t13c.png` 17:20 局部、`/tmp/t13s.png` 10-08 旧版） |
| `/tmp/12-s0-fetch.png`、`/tmp/t12.png` | 10-08 15:57–15:58 | 12 号图（12 号图之后没有再改，可以直接用） |
| `/tmp/11.png`、`/tmp/11-target-pipeline.png`、`/tmp/t11.png` | 10-08 | 11 号图旧版，已过时 |

00–10 号图没有 PNG。重新渲染用 `~/.local/bin/drawio-export <in.drawio> <out.png>`。`/tmp` 下的文件可能被清掉，做幻灯片前建议重新导出一遍。
