# GPU 模拟器机制归因与 Trace 压缩研究报告

## 摘要

现代 GPU 架构研究越来越依赖模拟器来回答“如果某个硬件机制改变，真实 workload 会发生什么变化”。但是，面向深度学习模型、图计算和 HPC 应用的完整 trace replay 往往代价极高：一方面，真实 kernel 序列会产生 TB 级 SASS trace；另一方面，逐周期模拟需要维护 warp 调度、访存、cache、pipeline 等大量状态，单次回放可能持续数小时甚至数天。因此，研究工作的重点不能只停留在“如何模拟”，还需要回答“如何从庞大的 workload 行为中提取可验证的机制假设”。本文结合 GPU 组会 PPT、`modern-gpu-simulator-micro-2025` 仓库以及多个 worktree 中的设计文档，梳理一条从 trace 压缩到机制归因，再到 simulator knob 处方验证的端到端路线。该路线的核心不是重新发明 GPU 模拟器，而是在已有 Accel-Sim/GPGPU-Sim 类 trace-driven simulator 的基础上，建立 `PKA evidence -> family/subtype -> regime/time weight -> simulator prescription -> validation` 的结构化桥梁。

## 一、研究背景：为什么需要从 GPU workload 出发

GPU 的优势来自大规模并行。程序员在 CUDA 中编写 kernel，运行时将 grid 划分为多个 thread block，再由硬件把 block 分配到 SM 上执行。每个 SM 内部包含 warp scheduler、dispatch unit、register file、CUDA cores、SFU、LD/ST units、shared memory 与 L1 cache。硬件真正调度的基本单位是 warp，一个 warp 通常包含 32 个线程，以 SIMT 方式执行同一条指令。当 warp 等待内存访问时，调度器可以切换到其他就绪 warp，从而用并行度隐藏延迟。

这套执行模型决定了 GPU 性能瓶颈并不总是显性的。一个 kernel 可能看起来是 compute-bound，但真正限制它的可能是 FP64/DP pipeline 的 initiation interval；另一个 kernel 可能表现为访存慢，但瓶颈可能来自 L1 miss、shared memory bank conflict、coalescing 效率或 warp divergence。真实 AI workload 更复杂，它不是一个孤立 kernel，而是一串包含 GEMM、attention、normalization、activation、data movement 等阶段的 kernel launch sequence。因此，如果只看单个 microbenchmark，我们可以解释局部硬件机制，却很难证明该机制是否主导端到端模型性能；如果只看完整模型结果，我们又能看到快慢，却难以解释为什么快或慢。

因此，本研究的出发点是：GPU 架构优化应由真实 workload 定义问题，由压缩和归因方法缩小分析范围，再由模拟器验证具体机制。换句话说，我们需要建立“workload 发现问题、机制层解释问题、simulator 验证结果”的闭环。

## 二、已有模拟器路线与核心缺口

当前主流 GPU 模拟器包括 Accel-Sim/GPGPU-Sim、gem5 GPU/GPUFS、MGPUSim 和 NaviSim 等。它们的共同价值在于提供一个可信 baseline，再围绕 cache、memory、pipeline、scheduler、SM 数量等设计点开展 architecture exploration。以 `modern-gpu-simulator-micro-2025` 为例，该仓库在 Accel-Sim 基础上加入了重新设计的 SM model、sub-core pipeline、memory pipeline、控制位解析、增强 scoreboard、WAR hazard 保护、L0 instruction cache、stream-buffer instruction prefetcher、OpenMP 并行化、AccelWattch 能耗报告，以及基于 Protocol Buffers 的 trace 存储。这说明现代 GPU 模拟器已经不仅是简单回放工具，而是复杂硬件机制的可配置实验平台。

但是，已有范式仍存在一个关键缺口：模拟器可以回答“给定某个 knob，改变它会怎样”，却较少回答“复杂 workload 中到底应该优先验证哪个 knob”。传统 case study 往往由研究者人工选择若干参数进行探索，这在小规模 benchmark 上可行，但在 AI 模型和完整应用中不够稳健。因为完整 workload 的 kernel 数量大、阶段结构复杂、热点分布会随输入 shape 和 batch size 变化，人工挑选瓶颈容易把局部结论外推到全局。

相关文档中反复强调一个判断：可信 architecture exploration 不仅依赖 simulator 精度，还依赖 workload、模型与验证之间是否形成端到端闭环。如果 baseline 不准确，设计判断会偏移；如果只填公开参数而不重新建模，结论可能错误；如果 workload 入口过度简化，模拟结果也难以外推到真实场景。因此，我们的工作不是替代已有 simulator，而是在 workload analysis 与 simulator validation 之间加入一个结构化中间层。

## 三、Trace replay 的瓶颈与压缩的必要性

trace-driven simulator 的基本流程是：先在真实 GPU 上运行 CUDA 应用，通过 NVBit tracer 采集 SASS 指令、访存地址、per-warp PC、threadblock 信息等动态行为，生成 trace；然后把同一份 trace 放入不同架构配置下回放，得到 cycle、IPC、stall、cache miss 等统计结果。这个流程的优势是可复现、可比较，同一 workload 可以在不同硬件假设下做 what-if 分析。

问题在于，完整 trace 太大。PPT 中给出的例子表明，BERT-base 一次训练可能包含约 `10^5` 次 kernel invocation，并产生约 2 TB raw SASS trace。对于 Llama 3.1 8B single step，kernel 数量更多，访存模式更复杂，存储和传输负担更重。即使 trace 能保存下来，逐周期 replay 也很慢，因为模拟器需要处理数十亿动态事件，并持续更新 warp 调度、cache、memory request、scoreboard、pipeline 等状态。若要做 10 个 knob、5 个 workload 的设计空间探索，就可能需要 50 次 replay，迭代周期从数周到数月不等。

因此，压缩不是可选优化，而是让研究闭环能够运转的前提。但压缩不能只追求文件变小。若压缩后只剩少量代表 kernel，却无法说明这些片段代表了什么硬件机制，那么它只能降低模拟成本，不能支撑机制归因和参数处方。本研究关注的正是“保留机制信息的压缩”：压缩后的对象既要足够小，又要能进入 family、subtype、regime 和 simulator knob 映射。

## 四、方法主线：从 PKA evidence 到机制处方

PPT 中采用 PKA-style representative kernel compression 作为前端锚点。这样做的原因是，PKA 的问题定义清楚：从完整 workload 中选出代表 kernel，以降低 simulation cost。我们并不把贡献放在重新发明 PKA，而是把它作为可信输入来源，继续在 compression 之后构建面向 simulator 的结构层。

在前端，PKA 使用 12 维行为特征描述 kernel，包括 coalesced global/local load/store、thread global/local/shared load/store、global atomics、instruction count、divergence efficiency 和 thread block 数量。为了让特征适合聚类，count 类特征先做 `log1p` 变换，再整体 z-score 标准化，然后通过 PCA 将 12 维空间投影到前三个主成分。PPT 中给出的解释是，前三个主成分可以保留约 95% 方差信息，这使得后续 K-means 聚类能在低维、去噪、方差集中的空间中工作。K-means 将 kernel 分为若干 cluster，每类选择代表 anchor，并保留 membership 与 weight。

但是，仅有 representative anchors 还不够。传统压缩输出回答的是“压谁”，而我们的后续方法要回答“为什么它重要、属于什么机制、该改哪个 simulator knob”。因此，B 线将 anchor 提升为 family/subtype：family 回答硬件资源大类，例如 `dense_compute`、`memory_hierarchy`、`control_flow`、`scheduler_pressure`；subtype 则进一步定位具体机制，例如 `fp64_dp_pipeline_compute`、`L1 miss`、`shared memory bank conflict`。C 线引入 regime 与 time weight，用于估计某类机制在 workload 中占多少时间，从而把局部 kernel 加速折算为 workload-level 预期收益。

最终的端到端链路可以概括为：`PKA evidence -> representative anchors -> family/subtype attribution -> regime/time weight -> subtype-to-knob map -> simulator validation`。它的价值不在于单点压缩，而在于让压缩结果变得可解释、可归因、可验证。

## 五、AI Bridge：从行为特征到机制语义

为了让归因过程具有可扩展性，PPT 中设计了 AI Bridge。它不是直接用黑盒模型输出最终答案，而是先把 PKA 12 维原始特征转换为确定性的派生特征，例如 `memory_ratio`、`compute_to_memory_ratio`、`divergence_score`、`work_per_block`、`instruction_density`、`pipeline_pressure_hint` 等，再形成 mechanism evidence signature。这个签名把 kernel 行为表示为“计算强度、访存压力、控制分歧、同步压力、occupancy 压力、pipeline 压力、shape scale”等语义维度。

在第一版实现上，可以采用 Logistic Regression 预测 family，用 rule scorer 预测 subtype。其优点是权重可解释，便于 ablation，也便于和人工规则、已知案例、sim registry 进行融合。弱监督信号主要来自三类：第一，规则引擎，例如 memory pressure 高则倾向 memory hierarchy，compute intensity 高且访存压力低则倾向 dense compute；第二，已知标注案例，例如 `bpnn_adjust_weights_cuda -> fp64_dp_pipeline_compute`；第三，sim registry，即已知 knob 到 mechanism 的映射，约束 subtype 不能脱离可验证范围。

进一步地，图层可以把 kernel、evidence、family、subtype、regime、knob 和 validation 组织为异构图。图一致性约束的意义是：如果一个 kernel 的机制标签可信，那么相似 kernel、同一 regime 或同一 subtype-to-knob 边上的节点也应受到约束。这样可以借鉴 GCL-Sampler 的图表示思想，但目标不再只是选择代表样本，而是输出可解释的机制归因、knob 排序、验证优先级和不确定性审计。

## 六、案例验证与当前边界

PPT 中的第一个案例是 Rodinia backprop。目标 kernel 为 `bpnn_adjust_weights_cuda`，B 线将其归为 `dense_compute`，subtype 为 `fp64_dp_pipeline_compute`。随后通过 subtype-to-knob map，将该机制映射到 simulator 中的 `trace_opcode_latency_initiation_dp` 参数。baseline 设置为 `24,16`，modified 设置为 `24,4`，含义是在模拟器中降低 DP pipeline 的 initiation interval，观察 FP64 相关操作更快发射后是否带来性能提升。

闭环验证结果显示，目标 kernel cycles 从 12593 降至 7106，下降 43.6%；IPC 从 234.2 提升至 415.1，提升 77.2%；local speedup 达到 1.772x，workload estimate 约为 1.403x。这个案例的重要性不在于证明真实硬件一定应该这样设计，而在于证明当前方法链路可以从 PKA evidence 出发，经过 B/C 线机制归因，落到具体 simulator knob，并在模拟器内部得到可观测响应。

第二个案例是 `ref_layer3/stage3` 的 PKA 代理验证。该序列包含 29 个 kernel invocation，PKA 选出 6 个 anchors，并形成 7 个 regime candidates。主 regime 为 `regime_ref_layer3_anchor_03_conv_compute`，time weight 约为 0.7579，代理估计 speedup 为 1.064x。这个结果说明方法可以迁移到深度学习层级 workload，但它目前仍属于 proxy/accounting 证据，而不是完整 replay 结论。因此报告中必须明确边界：Rodinia 是闭环验证，ref_layer3 是趋势代理验证；后者还需要更快的 replay、sampled simulation 或更完整的 trace validation 来支撑强结论。

## 七、下一阶段我们要做的东西

结合 worktrees 中的任务计划，下一阶段不应等待前端 compression 完全成熟后再推进后段，而应让 A/B/C 三条线并行生长。A 线负责前端锚点，目标是固定 PKA selector output 到 Representative Anchor Table 的 contract，明确 anchor、membership、weight、feature provenance 和采集状态。B 线负责中间结构层，目标是实现 decision builder，把 anchors 提升为 family、subtype、regime、lane 和 importance 对象。C 线负责后端验证，目标是实现 backend adapter，生成 run manifest、scenario matrix、baseline plan 和 writeback 结果。

具体来说，第一步应完成 anchor table、family table、regime table 和 importance template。它们必须包含可追踪字段，而不能只停留在概念描述。第二步要建立 simulator lane 映射，即每个 subtype 能进入哪个 validation lane，对应哪些可改 knob，哪些属于当前模型盲区。第三步要设计 baseline comparison，例如 random、time-only、importance-guided 三类对照，证明我们的优先级排序不是主观挑选。第四步要扩展 workload trace corpus，覆盖 Rodinia、Parboil、SHOC、CUTLASS、MLPerf-style AI workload、Gunrock/Pannotia graph workload 以及部分 HPC full applications，并按 L0 source、L1 workload registry、L2 launch metadata、L3 measured feature、L4 trace artifact、L5 training dataset 分层管理。

最终我们希望形成的最小闭环是：`Representative Anchor Table -> Family Table -> Regime Table -> Importance Scoring -> Simulator Lane -> Backend Validation`。当这条链跑通后，论文就可以从“我们能压缩 trace”升级为“我们能从压缩结果中产生可验证的架构假设”。这也是本工作的核心贡献边界：不是单独提高模拟器精度，也不是单独提出一个压缩格式，而是让 GPU workload 的结构化行为能够逐步转化为 simulator 可检验的机制处方。

## 八、结论

综上，GPU 模拟器已经是架构研究的重要工具，但在现代 AI workload 场景下，单纯依赖完整 trace replay 或人工挑选 design point 都难以支撑高效迭代。我们需要把压缩、归因、处方和验证串成一条链路。PKA 提供可信的代表样本入口，B 线和 C 线把代表样本转化为 family、subtype、regime 和 time weight，AI Bridge 用结构化特征与图一致性提升机制归因的可扩展性，simulator prescription 则把归因结果落到具体 knob 上闭环验证。

因此，本研究的主张可以概括为：面向现代 GPU workload 的 trace 压缩不应只追求数据量下降，而应保留足够的机制证据，使压缩结果能够继续服务于架构归因和模拟器验证。只有这样，GPU 模拟器才能从“被动回放工具”进一步成为“workload-driven architecture hypothesis validation backend”，帮助研究者从复杂应用中系统地产生、排序并验证硬件优化假设。

