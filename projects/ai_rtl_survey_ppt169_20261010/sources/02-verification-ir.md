# 综述素材 2：LLM 硬件验证、断言挖掘、性能模型到 RTL 的中间表示（2026-10-10 检索）

核实方式：arXiv 摘要页 / API、项目仓库或 DOI 确认标题、ID、作者。单位多凭记忆（标"记忆"）；会议名只有 arXiv 备注中出现的算已核实。DBLP、Semantic Scholar、ACM、IEEE 当时拦截抓取，经典挖掘论文只有 HARM 通过仓库确认。

结论：2023–2026 没有工作同时做"显式结构框架（流水级、边界寄存器、状态归属、事件通道）+ 波形等价验证的重构 + 隐式时序契约"。最接近的四组：HINT 与 Representation Bottleneck（需要显式表示层）、Anvil 与 Filament（时序契约写成类型）、SeqFeed 与 DUET（LLM 看不出跨周期行为）。

## (1) LLM 做硬件验证

| 工作 | 单位 / 会议 | arXiv | 思路 | 与论点 |
|---|---|---|---|---|
| AssertLLM | HKUST-GZ（记忆）；ASP-DAC 2025（未核实） | 2402.00386 | 三个 LLM 从规格抽结构、映射信号、生成 SVA | 断言来自 NL 规格，无结构框架 |
| ChIRAAG | — | 2402.00093 | 规格先结构化再生成 SVA，仿真日志反馈 | 结构化只是输入格式 |
| FVEval | NVIDIA，2024 | 2410.23299 | NL→SVA、RTL→断言的形式验证基准 | 评测对照 |
| AutoSVA | Princeton，DAC 2021（记忆） | 2104.04003 | 从接口注解生成 FV testbench（非 LLM） | 最接近"事件通道 / 握手契约" |
| AssertionBench / AssertCoder / SANGAM / ChatSVA / AssertLLM2 | 2024–2026 | 2406.18627、2507.10338、2506.13983、2604.02811、2605.27472 | 各类 SVA 生成 | 模块黑盒，断言依附信号 |
| HierSVA | 2026 | 2606.13706 | 层次化 RTL 的 SVA 基准 | 有层次，无流水结构 |
| SVA 生成综述 | 2026 | 2607.07444 | 综述 | 相关工作可引 |
| LLM4DV | Cambridge/Imperial（记忆） | 2310.04535 | LLM 生成激励提高覆盖率 | 不涉及时序契约 |
| AutoBench / CorrectBench | 2024 | 2407.03891、2411.08510 | LLM 生成 / 自校正 testbench | 端到端 testbench 路线 |
| FVDebug | NVIDIA，2025 | 2510.15906 | FV 反例 → 因果 DAG → LLM 定位修复 | 基于波形调试 |
| VeriDebug / RTLFixer / R3A / Clover | 2023–2026 | 2504.19099、2311.16543、2511.20090、2604.17288 | 定位与修复 | RTL 修复 |
| SeqFeed | 2026 | 2608.16934 | SQL 式波形查询 + 跨周期依赖图作反馈 | LLM 看不出跨周期行为，支持论点 |
| DUET | 2025 | 2512.06247 | 智能体提假设、用仿真 / 波形 / FV 验证来理解时序 | 同上 |
| Back to the Future | 2026 | 2610.06790 | 仿真 dump 存 SQLite 供智能体查询 | 波形查询基础设施 |
| Veri-Sure | 2026 | 2601.19747 | 多智能体共享"设计契约"，时序追踪 + 断言 + 布尔等价 | 契约是接口 / 功能级，非周期级 |
| SpecLoop | 2026 | 2603.02895 | RTL→规格→RTL，等价检查反例迭代 | 等价在环 |
| SymRTLO | NeurIPS 2025 | 2504.10369 | LLM 重写 RTL 优化 PPA，等价检查兜底 | 最接近"保持行为的重构" |
| NoTB | 2026 | 2608.21962 | 多模型输出顺序等价共识代替 testbench | 等价作判据 |
| FormalRTL | 2026 | 2603.08738 | 软件参考模型作可执行规格，形式等价验 RTL | 关键对照：只对数据通路有效，控制 / 时序不在范围 |
| AutoVeriFix+ | 2026 | 2603.11489 | Python 参考模型 + concolic 周期轨迹修状态转移错 | "参考模型够用"路线代表 |

## (2) 断言与不变量挖掘

| 工作 | 单位 / 会议 | 链接 | 思路 | 与论点 |
|---|---|---|---|---|
| GoldMine | UIUC，DATE 2010（记忆，未核实） | — | 仿真轨迹决策树 + 静态分析生成断言 | 经典基线 |
| IODINE | DAC 2005（记忆，未核实） | — | Daikon 式动态不变量用于硬件 | 原型 |
| HARM | Verona，IEEE TCAD 41(11) 2022 | github.com/SamueleGerminiani/harm | 用户给模板与提示，从轨迹挖 LTL 断言 | 模板能表达"同 warp 不连续发射"，但要人先想到 |
| A-TEAM | Verona，DAC 2017 前后（记忆，未核实） | — | 模板式时序断言挖掘 | 同上 |
| Isadora | 2021、2026 | 2106.07449、2606.13860 | 信息流追踪 + 规格挖掘 | 面向安全 |
| GR1MINE | 2026 | 2608.06546 | SAT 从轨迹学 GR(1) | 时序规格学习 |
| NeuroAssertion | MLCAD 2026 | 2608.18482 | 形式探索生成轨迹 → SyGuS 挖掘 → LLM 修复 | 唯一实质结合 LLM 与轨迹挖掘；不用微架构先验 |
| FlowMiner 等 | Florida，2020–2022 | 2005.11221 | SoC 轨迹挖消息流 | 对应"事件通道" |

## (3) 性能 / 架构模型与 RTL 之间的中间表示

| 工作 | 单位 / 会议 | 链接 | 思路 | 与论点 |
|---|---|---|---|---|
| HINT | CUHK（记忆），2026 | 2608.07625 | 行为规格与 RTL 之间加可执行的硬件意图层，显式写微架构，RTL 前可检查 | 最接近、几乎同向；只到算子 / VPU 级，无流水契约与验证框架 |
| Representation Bottleneck | 2026 | 2604.17097 | 6 种 IR、202 任务：仿真通过率随 IR 3%–88%，换模型差异 < 1.25 倍 | 表示层比模型更重要 |
| AGON | ICT/CAS（记忆），2024 | 2412.20954 | nano-operator IR 驱动 LLM 设计乱序核 | 结构化 IR 用于处理器 |
| C2HLSC | NYU，LAD 2024 | 2406.09233、2412.00214 | LLM 把 C 改写成可综合 HLS C | 时序交给 HLS |
| HLSmith / Proof2Silicon | 2025–2026 | 2608.06791、2509.06239 | C→HLS；Dafny 验证后 HLS | 同上 |
| Anvil | NUS（记忆），ASPLOS 2026 | 2503.19447 | 类型系统静态排除时序冒险，模块间时序契约 | 时序契约写成类型，对应我们 G2 遇到的契约；无 LLM |
| Filament | Cornell，PLDI 2023 | 2304.10646 | timeline 类型约束信号何时可用 | 只覆盖静态调度流水线 |
| PDL | Cornell，PLDI 2022（会议名记忆） | github.com/apl-cornell/PDL | 顺序语义自动生成带 stall / 冒险处理的流水线 | 流水级一等结构；无 LLM |
| Kôika | MIT，PLDI 2020 | github.com/mit-plv/koika | 周期级调度语义的规则式 HDL，Coq 证明 | 周期级规格语言 |
| Latency-insensitive design | Carloni 等，IEEE TCAD 2001（记忆） | — | valid/ready 通道使正确性与延迟无关 | "队列是桥梁"的理论来源 |
| ReChisel / ChiseLLM / hdl2v | 2025 | 2505.19734、2504.19144、2506.04544 | LLM 生成 Chisel；HCL 翻译成 Verilog 扩数据 | 只改语法层，不给结构契约 |

## 空白

1. 没有人在流水级、边界寄存器、状态归属、事件通道这一粒度给 LLM 显式结构框架。HINT 到算子级；PDL、Kôika 是给人用的语言。
2. 没有人把隐式时序契约当 LLM 生成失败的主要原因做实证。Anvil / Filament 从类型系统解决，没研究 LLM 怎么违反。我们 G2 首轮（同 warp 连续发射，iadd3 PASS 盖住）是现成案例。
3. 没有人系统比较"只给性能 / 参考模型"与"模型 + 结构框架"。FormalRTL、AutoVeriFix+ 是参考模型路线，可作对照组。
4. 等价在环的工作几乎都是组合等价或 PPA 重写；没有人区分"逐信号波形等价"（保持行为）和"改时序的重构"（需要契约级 / 事务序列等价）。
5. 轨迹挖掘（HARM、NeuroAssertion）不用微架构先验；按流水级和事件通道约束模板空间，可自动挖出"warp 发射间隔"这类契约。
6. 现有基准没有"重构后时序契约须保持"的任务，也不检验确定性复现（lockstep）。
7. "契约类型"（Anvil）与"LLM 生成 SVA"两条线没有交叉。

## 待补核实

GoldMine、IODINE、A-TEAM、latency-insensitive design 的书目信息，PDL 的会议名。
