# 综述 PPT 大纲草稿：AI 生成 RTL 的现有思路与可对比的 baseline（2026-10-10）

素材：`01-benchmarks-models.md`、`02-verification-ir.md`、`03-agentic-flows.md`（待第三路检索返回）。
核实：重点引用的 20 篇已用 arXiv API 确认标题、一作、日期（2026-10-10）。

## 主线

现有工作按"给 LLM 的中间表示"从低到高排一条轴：
自然语言 → 模块拓扑 / 端口图 → 软件参考模型 / IR → 微架构意图层 → （我们）流水级 + 状态归属 + 时序契约 + 验证框架。
每往上一层，能做的设计就更大；但到"流水线 + 隐式时序"这一层，目前没有人同时给结构和验证。

## 页序（约 16 页）

1. 封面：AI 生成 RTL：现有思路与 baseline 调研
2. 组会意见与本次目标：找可对比的 baseline；我们的论点（性能模型不够，需结构框架 + 验证框架）
3. 分类总览：四条路线 + 一条轴（中间表示层级）
4. 路线一：数据与模型（RTLCoder、CodeV、CraftRTL、CodeV-R1、VeriReason）——模块级 testbench 训练
5. 路线二：agent / 多 agent 流程（待第三路：VerilogCoder、MAGE、Spec2RTL 等）
6. 路线三：结构化中间层（ROME、SysVCoder、VeriGraphi、分层 IR、AGON、HINT）——最接近我们
7. HINT 与 Representation Bottleneck 细看：IR 比模型重要（3%–88% vs < 1.25 倍）
8. 路线四：参考模型 + 形式等价（FormalRTL、AutoVeriFix+、C2HLSC）——"模型够用"的对照组，只覆盖数据通路
9. 验证线：SVA 生成、testbench 生成、波形反馈（SeqFeed、DUET、FVDebug）
10. 时序契约线：Anvil、Filament、PDL、Kôika、latency-insensitive——给人用的语言，没接 LLM
11. 断言挖掘线：GoldMine、HARM、NeuroAssertion——没有微架构先验
12. Benchmark 现状：模块级饱和；ArchXBench L4 全灭、CVDP ≤ 34%、HWE-Bench SoC < 65%
13. 空白汇总（与我们的案例对应：G2 同 warp 连续发射、PR 38 next_deadline）
14. 可作 baseline 的组合：方法 / 模型 / benchmark 三层
15. 我们的对比实验设计：四种条件消融 + baseline 方法跑同一 subcore 模块，指标
16. 下一步与待核实项

## 待定

- 第 5 页内容等第三路检索。
- 第 15 页实验设计：选哪个模块（S1 `subcore_decode` / `subcore_issue_hold`），指标（lint、端到端、波形等价、契约违例、人工干预）。
