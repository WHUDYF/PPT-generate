# 硕士中期考核汇报源稿（2026-10）

约束：考核 13 分钟，其中汇报 10 分钟 → 约 12 页。风格：白底、极简、无多余装饰。
公司项目全部脱敏：只写"项目 A–D + 芯片类型"，不写型号、公司名、客户名、个人信息；只说"学习了公司的设计—验证流程"，不讲截图重建方法。

## 0. 一年工作总览

三条线，前后衔接：
1. GPU 学习：从体系结构到模拟器、性能模型，再到 RTL（curryGPU）
2. AI for EDA 思路构建：调研 AI 生成 RTL → 发现空白 → 提出"以结构 IR 作为需求规格，验收 AI 生成的大规模 RTL"
3. 公司学习：通过 4 个真实芯片项目，学习成熟的"规格 → 设计 → 验证 → DFT → 量产"流程

三者关系：GPU 是研究对象；公司流程提供"成熟工程里规格和验证怎么组织"的参照；AI for EDA 要解决的正是 AI 写 RTL 时缺的那一层规格与验收。

## 1. GPU 学习

### 1.1 GPU 体系结构（curryGPU）
- curryGPU：GPU 的 RTL + 模拟器工程（功能模型 ISS、性能模型、Verilator SoC 模型）
- 层次：GPU → GPC → TPC → SM → 4 个 subcore；每个 subcore 16 个 warp slot
- subcore 流水线：取指（L0I / IB）→ 译码 → warp 调度 → ITS（独立线程调度）→ scoreboard → 寄存器堆读 → 执行 → 写回
- 学习产出：整机 / SM / subcore 架构图、ITS / LSU / RF 子系统图、subcore 7 级目标流水线图（S0–SW）
- 可用图：currygpu_architecture/images/01-gpu-sm-subcore-overview.jpg

### 1.2 模拟器与性能建模
- PyTorchSim：PyTorch 程序如何经 MLIR 编译成 tile 指令（MOVIN / MOVOUT / COMP / BAR），TOGSim 如何模拟 Core / 互连 / L2 / DRAM
- Workload trace 压缩（2026-06）：PKA 基线（12 维 kernel 特征 → log1p + z-score → PCA top-3 → K-means → 代表 kernel 和权重），降低完整 trace replay 成本；下一步提出 GCL（图对比学习），把 kernel 相似性、时序邻接、机制 family 放进同一个图，让压缩结果和机制归因互相校验

### 1.3 RTL 实践：subcore 流水线重构（2026-10）
- 问题：发射路径一条长组合链（估计 35–45 级逻辑）；跨级组合读取；挡发射的状态散落在 6000 多行的顶层
- 做法：先写"架构 → 流水线 → RTL"结构规范（目标流水线图 v2），再在行为不变前提下按级拆分
- 结果：130 个提交；subcore_top 6169 → 3486 行（−43%）；新建 16 个模块；每个提交用 VCS 跑完整验收（约 80 次），sm_kernel 用例 10 → 14 个，断言文件 17 → 50 个全部启用

## 2. AI for EDA 思路构建

### 2.1 领域现状（2026-10 调研）
- 四条路线：数据与微调模型（RTLCoder、CodeV-R1、VeriReason）；agent 流程（VerilogCoder、MAGE）；结构化中间层（ROME、SysVCoder、HINT）；参考模型 + 形式等价（FormalRTL）
- benchmark 断崖：模块级已饱和（VerilogEval v2 89–98%）；到流水线 / 层次化就失败（ArchXBench L4 起全灭，CVDP pass@1 ≤ 34%，HWE-Bench SoC < 65%）
- 关键规律：表示比模型更重要（换表示 3% → 88%，换更强模型 < 1.25 倍）；组合是共同瓶颈；时序是盲区
- 空白：正确性只看端口 I/O 等价，不检查级边界、状态归属、握手和时序

### 2.2 问题的提出：功能全过，问题照样漏
观察对象：一个由 agent 编写、约 10.8 万行 Verilog 的 GPU subcore，正在逐步重构。在功能验证全过的提交里仍漏掉三类问题：
- 结构偏离：S4 allocate 搬家自称"行为不变"，功能 0 mismatch，但逻辑落到错误的级
- 时序回归：两次 6–8% 的变慢（WARPSYNC 每次 6 拍 → 9 拍；访存响应拍挡住全部发射），落在性能模型误差之内
- 验证手段本身失效：旧验收脚本判 PASS 但实际有 SM fault；断言文件静默失效

### 2.3 核心思路：以结构 IR 作为需求规格，验收 AI 生成的 RTL
- 每条需求带：分级来源（实卡测量 > 厂商资料 > 人确认的设计决策 > …）、三种状态（done / target / deviation）、绑定的检查（写不出检查的单列"未覆盖"）
- 封闭世界：网表里有、IR 没认领的触发器和连线一律报"未登记"；已有项进基线，门禁只拦新增
- 三类检查：逐指令比对（功能）、网表结构检查（结构）、事务间时序契约（时序）
- 主贡献：逃逸分析——每层检查各抓住了什么，只用功能测试会漏多少

### 2.4 原型与初步结果
- 一份结构数据同时派生：流水线图、给 AI 的约束清单、网表检查器
- 注入实验：6 类 RTL 变异 + 10 类规格篡改，全部按预期拦下
- 首次在真实 RTL 上：发现 5 处功能测试看不见的结构分歧，其中一处正是上面的"S4 搬家"
- 六级（S1–SW）全部接入门禁

### 2.5 后续计划
- 系统整理真实逃逸案例 + 注入缺陷集，做三种条件对比（只有功能测试 / 加结构检查 / 三类检查全上）
- 实现发射时序比对工具，补齐时序契约
- 外部案例验证（如 XiangShan + difftest）
- 撰写论文

## 3. 公司学习：成熟的 EDA 设计—验证流程

### 3.1 统一框架（从 4 个项目归纳）
① 规格层：系统设计说明、寄存器表（带复位值和读写 mask）、DSP 指令集表、数模接口表、时序图 —— 表格化，唯一来源，设计和验证都从这里派生
② 设计层：RTL 按 IP 分目录、每个 IP 一份 filelist；第三方 IP 直接集成（RISC-V 核、ARM 总线、I3C、foundry Flash）；工艺相关单元和公司通用 IP 单独放；模拟模块用 real 型 SV 行为模型
③ 验证层：testbench + env（VIP、寄存器访问层、低功耗 UPF）→ tc_base 基类 → 一个目录一个 case（SV 激励检查 + CPU C 固件）→ caselist → 回归脚本 → 集群
④ 多模式：同一套环境靠 filelist 和 Makefile 开关切换：RTL 前仿 / SDF 门级后仿（func、scan × ss/ff/tt）/ 数模混仿
⑤ 可测性：MBIST、Flash BIST、bypass 通路、ATPG pattern（stuck-at、Iddq）、trim 写 Flash
⑥ 签核与量产：Design Review、仿真检查表 → CP/FT 测试计划（32-site）→ 实验室测试 → 客户测试

### 3.2 项目 A：RISC-V MCU SoC（重点：SoC 集成与 IP 组织）
- RISC-V 核 + 协处理器接口（含 DSP 流水线、CORDIC）、AHB matrix + APB、Flash（ECC/CRC）、ROM/RAM、SPI/I2C/GPIO/DMA、模拟控制、PWM、脉动阵列加速器
- 约 160 个 RTL 文件、约 10 万行（量级）
- 学到：按 IP 分目录 + 每 IP 一份 filelist；第三方 IP 复用；工艺单元与公司基础 IP（时钟门控、同步器）分层；RTL 里预留 MBIST 和 bypass

### 3.3 项目 B：光学位移传感器图像 DSP（重点：单模块设计规范）
- 16×16 像素阵列；NCC 模板匹配、亚像素定位、自动曝光 / 自动帧率、唤醒 / 休眠检测
- 控制：41 个状态的 FSM，按 4-bit opcode 分派 9 类任务；每个工作态配一个等待态；按状态做时钟门控
- 数据通路：valid/ready 握手的多级流水；复用参数化计数器
- 接口命名：源模块+目标模块_信号（如 CCUDSP_*、DSPGLB_*），看名字就知道边界
- 学到：设计风格高度模板化，便于验证和复用

### 3.4 项目 C：混合信号光感芯片（重点：规格驱动验证与回归）
- 多通道 ALS + Flicker 检测、红外 LED 驱动、温度传感器、OTP、FIFO（SRAM + MBIST）、I2C；由前代芯片派生
- 寄存器表 → 设计侧 reg_map；验证侧 reg_define（复位值 / 读写 mask 宏）→ 通用寄存器检查自动暴露规格与 RTL 偏差
- tc_base 统一驱动、检查和 PASS/FAIL 报告；case 按功能分 11 组；回归脚本批量生成命令投集群
- 数模接口单独验证：数模接口表 + connection 白名单 + 模拟行为模型
- 参与：前代 case 迁移（寄存器层先对齐再迁 case）、寄存器定义修正、case 调试

### 3.5 项目 D：潜望式 OIS 驱动 SoC（重点：全流程闭环）
- RISC-V CPU（FPU + DSP 扩展）+ 独立 DSP；40nm eFlash；双通道 Hall/TMR 位置检测 → PID 闭环 → H 桥驱动音圈马达；PGA + SDM ADC
- 软硬件协同验证：每个 case = SV 激励检查 + CPU C 固件；约 160 组 case，覆盖 flash / i2c / dma / 模拟控制 / 时钟 / 低功耗
- 同一 testbench 跑 RTL 前仿、网表后仿、数模混仿（模拟行为模型 ↔ 晶体管网表切换）
- DFT：ATPG（stuck-at / Iddq）+ ROM/RAM/Flash BIST；仿真阶段就跑 trim、FT 固件，与 CP/FT 测试计划一一对应

### 3.6 收获
1. 规格表格化、唯一来源，设计和验证同时从规格派生
2. 验证分层：环境 → 基类 → case → 回归，case 只写配置和流程
3. 同一环境覆盖多种模式（前仿 / 后仿 / 混仿 / 多 corner）
4. 为量产而设计：DFT、BIST、trim 在仿真阶段就闭环
5. 结论绑定版本：调试结论要对应实际编译的 filelist 和源码版本
→ 与研究的联系：成熟流程靠"人写的规格 + 分层验证"保证质量；AI 写 RTL 时恰恰缺这层规格和验收，这就是第二部分要补的东西

## 4. 总结与后续计划
- 已完成：GPU 体系结构与模拟器学习；subcore RTL 重构实践；AI 生成 RTL 领域调研；研究问题收敛与原型；公司完整设计—验证流程学习
- 后续：补齐逃逸案例与注入实验 → 时序契约检查 → 外部案例 → 论文撰写与投稿 → 学位论文
