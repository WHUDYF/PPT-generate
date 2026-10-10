# 综述素材 1：Verilog 生成 benchmark 与微调模型（2026-10-10 检索）

核实方式：arXiv export API 逐个核对 ID、标题、一作、日期；GitHub 只看了 curl 返回码。标 * 的会议 / 单位来自记忆，未在 arXiv 元数据中确认。WebSearch 当时返回空，只覆盖 arXiv。

## A. 模块级基础 benchmark

| 名称 | 机构 | 会议·年份 | arXiv | 度量 | 规模 | 作基线 |
|---|---|---|---|---|---|---|
| VeriGen-Bench | NYU | DATE 2023 | 2212.11140 | 语法、仿真 | 小题 | 否 |
| VerilogEval v1 | NVIDIA | ICCAD 2023 | 2309.07544 | pass@k | 156 道 HDLBits 题 | 下限对照 |
| VerilogEval v2 | NVIDIA/Cornell | 2024 | 2408.11053 | pass@k，spec-to-RTL | 单模块 | 社区默认报数 |
| RTLLM v1 / v2 | HKUST | ASP-DAC 2024 / ICCAD 2024 | 2308.05345 / 2503.15112 | 语法、功能、PPA | 小型多模块，v2 50 个 | 下限对照 |
| RTL-Repo | AUC* | 2024 | 2405.17378 | EM / edit-sim，不仿真 | 仓库补全 | 否 |
| ResBench | Imperial* | HEART 2025 | 2503.08823 | 功能 + LUT | 56 题 | PPA 维度 |
| CVDP | NVIDIA | 2025 | 2506.14074 | pass@1（cocotb），13 类任务，agentic / non-agentic | 783 题，模块到小子系统 | 工业通用对照；代码生成 pass@1 最高约 34% |

## B. 面向结构的 benchmark（2025–2026）

| 名称 | 会议·年份 | arXiv | 内容 | 关键结果 |
|---|---|---|---|---|
| ArchXBench | MLCAD 2025 | 2508.06047 | 30 题 6 级，组合 → 多周期 → 流水线 → 层次化 | 所有模型从 L4 起全部失败；o4-mini-high 16/30 |
| ChipVerilog | 2026 | 2607.13079 | OpenCores 64 目标（OR1200、MIPS-16、DP-FPU），多数 >1000 行 | 编译 + 等价 + 集成核仿真 |
| HWE-Bench | 2026 | 2604.14709 | 417 个真实 bug 修复（RISC-V 核、SoC、RoT） | 小核 >90%，SoC <65% |
| RTL-BenchLS | 2026 | 2606.08976 | 10K 形式验证设计；round-trip / masked / repo-issue | 23% / 28% / 12% |
| NotSoTiny | 2025 | 2512.20823 | Tiny Tapeout 设计，定期刷新防污染 | — |
| RTL-OPT | 2026 | 2601.01765 | 36 对次优 vs 优化，含流水线数据通路 | PPA |
| LLM-FSM | 2026 | 2602.07032 | 1000 道可调复杂度 FSM 题 | — |
| SysVCoder / SysVDB | APPT 2026 | 2504.20653 | 先 IR 后 RTL，60 个系统级设计 | 思路接近"结构框架" |

## C. 微调模型

| 模型 | 机构 | arXiv | 方法 | 结果 |
|---|---|---|---|---|
| VeriGen | NYU | 2308.00708 | CodeGen-16B 微调 | — |
| ChipNeMo | NVIDIA | 2311.00176 | 领域预训练 + SFT + RAG | 未开源 |
| RTLCoder | HKUST | 2312.08617 | 27K 合成数据，7B | 开源 |
| BetterV | Huawei/CUHK* | 2402.03375 | 判别器引导生成，ICML 2024 | — |
| MG-Verilog | GaTech | 2407.01910 | 多粒度描述数据 | 开源 |
| CodeV | 中科院计算所 | 2407.10424 | 多级摘要构造数据，Verilog + Chisel | 开源 |
| OriGen | PKU | 2407.16237 | 代码增强 + 编译器反馈自修正 | 开源 |
| AutoVCoder | SJTU* | 2407.18333 | 数据 + 两轮微调 + RAG | — |
| CraftRTL | NVIDIA | 2409.12993 | 构造即正确的非文本数据（K-map、FSM、波形）+ 注错修复 | 开源 |
| VeriThoughts | NYU | 2505.20302 | 推理数据，形式验证判对错 | 开源 |
| VeriReason | — | 2505.11849 | SFT + GRPO，testbench 奖励 | VerilogEval-Machine 83.1% |
| CodeV-R1 | 中科院计算所 | 2505.24183 | 蒸馏 + RLVR | VerilogEval v2 68.6%，RTLLM 72.9%（7B） |

结构化中间层相关：ROME（2407.18276，层次化提示生成处理器）、VeriGraphi（2604.14550，知识图谱层次结构，RV32I）、Hierarchical IRs + 多智能体（2608.30659）、CHIA（2606.27350，Chipyard + gem5 + FireSim 闭环）、Chip-Chat（2305.13243）。

## 空白

1. 主流 benchmark 是单模块，VerilogEval v2 已到 89–98%，分不出结构能力。
2. 到流水线 / 层次化就断崖：ArchXBench L4 起全灭，CVDP 生成 pass@1 ≤ 34%，HWE-Bench SoC < 65%。
3. 正确性只看端口 I/O 等价，不检查级边界、状态归属、握手；时序不同但结果相同的设计同样通过。
4. 没有 benchmark 把周期数 / 与性能模型一致当一等指标；CHIA 是框架不是 benchmark。
5. 结构化中间层（SysVCoder、VeriGraphi、分层 IR、ROME）只到模块拓扑 / 端口图，没有流水级、事件通道、状态归属，也缺验证闭环。
6. 模型基线的数据和奖励都来自模块级 testbench，多级流水能力基本未测。

## 建议的基线组合

- 下限：VerilogEval v2、RTLLM v2。
- 工业通用：CVDP。
- 流水线 / 层次化：ArchXBench、ChipVerilog。
- 模型：CodeV-R1、VeriReason（开源 7B）+ 一个商用模型。
