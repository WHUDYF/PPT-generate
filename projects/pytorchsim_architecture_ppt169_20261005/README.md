# PyTorchSim 架构 · drawio 源文件

回答两个问题：PyTorch 程序怎样一步步变成模拟器里的"指令"，以及 TOGSim 模拟的硬件长什么样。画法沿用同仓库 `currygpu_subcore_ppt169_20261004`：框内用概念名，灰字标源码位置，反馈 / 完成路径用虚线。

内容按 PyTorchSim 工作区 `33afd3c`（含未提交修改）读源码整理，没有为这些图重新跑模拟。

## 文件

| drawio 源文件 | 回答的问题 | 主要依据 |
|---|---|---|
| `sources/00-overview.drawio` | 端到端总览：PyTorch 侧 → 编译前端 → 功能 / 采样 / 建图 → TOGSim → 结果 | `torch_openreg/__init__.py`、`extension_codecache.py`、`Simulator/simulator.py` |
| `sources/01-compile-flow.drawio` | 编译链：①捕获 ②分解 ③lowering ④融合 ⑤选 tile ⑥代码生成；下面是两条降级链——功能路径（mlir-opt → llc → 链接 → Spike）和时序路径（mlir-opt + TOG pass → 采样二进制 → Gem5 → AsmParser → `tile_graph.onnx`） | `mlir_decomposition.py`、`mlir_lowering.py`、`mlir_scheduling.py`、`mlir_gemm_template.py`、`mlir_template.py`、`extension_codecache.py`、`AsmParser/tog_generator.py` |
| `sources/02-tog-to-instructions.drawio` | TOG 怎样展开成 Tile 和 tile 指令（MOVIN / MOVOUT / COMP / BAR），搬运指令怎样拆成 `mem_fetch`；"指令"一词在六个层次上的含义；addmm + ReLU 的示意指令序列 | `TileGraphParser.cc`、`TileGraph.h`、`Instruction.cc`、`DMA.cc`、`Core.cc` |
| `sources/03-hardware-system.drawio` | 系统级结构：Python TOGSimulator → Scheduler（按 partition）→ N 个 Core → 互连 → 每通道一个 L2 切片 + DRAM 通道；三个时钟域；默认 tpuv3 配置；一个读请求的完整路径 | `Simulator.cc`、`Simulator.h`、`Dram.cc`、`L2Cache.cc`、`Common.cc`、`configs/systolic_ws_128x128_c1_simple_noc_tpuv3.yml` |
| `sources/04-core-internals.drawio` | Core 内部：最多 4 个在途 Tile → 每拍发射 1 条指令 → 读写队列 / DMA / VU / SA×N / tag 表 → `finish_instruction` 解除依赖；COMP 完成时间公式；哪些东西没有逐拍建模 | `Core.cc`、`Core.h`、`DMA.h` |

建议顺序：00 → 01 → 02 回答"怎样变成指令"，03 → 04 回答"硬件长什么样"。

## 几个容易误读的点

1. 有两种"调度"：前端 `MLIRScheduling` 决定融合与实现（编译期）；TOGSim `Scheduler` 只把已生成的 Tile 交给 Core（模拟期），不会重新选 tile 大小。
2. RISC-V / 加速器机器指令只在 Spike（功能）和 Gem5（采样计算周期）中执行。TOGSim 执行的是 tile 指令，COMP 的耗时直接用 Gem5 采到的 `torchsim_cycle`。
3. 硬件参数在两处起作用：编译期（lanes、每 lane SPAD 决定哪些 tile 可行，Gem5 阵列宽高 = lanes），模拟期（核数、SA 个数、频率、互连、DRAM）。只改 YAML 后沿用旧 TOG，不等于新硬件下的完整结果。
4. SPAD 容量只在编译期选 tile 时约束；`Core::can_issue` 只检查在途 tile 数 < 4，不逐拍跟踪 SPAD 占用和 bank 冲突。
5. 异步 MOVIN 请求发完就算完成，数据到齐由 tag 表记录，BAR 在 tag 就绪前挂起；这就是搬运与计算重叠的来源。MOVOUT 在写请求全部发出时完成，写确认之后仍会回来。
6. L2 由 `l2d_type` 决定，默认 nocache 直通；datacache 只缓存属性文件 `sram_alloc` 划出的区间。L2 在 core 时钟下推进。

## 配色约定

沿用 `currygpu_architecture_ppt169_20261001`。

| 用途 | fill | stroke |
|---|---|---|
| 调度 / 控制 / 解析 | `#E1D5E7` | `#9673A6` |
| 存储 / 队列 / 表 / 配置文件 | `#FFF2CC` | `#D6B656` |
| 数据通路 / 编译步骤 / 计算单元 | `#DAE8FC` | `#6C8EBF` |
| 外部工具 / PyTorch / 上下游 | `#D5E8D4` | `#82B366` |
| DMA / 搬运 / mem_fetch | `#FFE6CC` | `#D79B00` |
| 完成 / 响应 / 反馈 | 虚线 | `#4B5563` |

## 导出

本机没有 drawio CLI，图没有用 drawio 渲染过。本地导出：

```bash
for f in sources/*.drawio; do
  drawio -x -f svg --crop -o "exports/$(basename "${f%.drawio}").svg" "$f"
done
```

## 校验范围

只做了几何检查：XML 可解析；方块不重叠（嵌套的除外）；按字号估算的文字不超出框；所有连线按显式出入口和拐点计算后是正交折线，不穿过无关方块，连线之间没有交叉。另外用简易渲染看过整体布局。没有在 drawio 里目视确认，个别标签位置不理想时手动拖动即可。

## 未核实项

1. 01 中 MLIR pass 的内部行为（`-dma-fine-grained`、`-test-pytorchsim-to-vcix`、`-test-tile-operation-graph` 等）在外部 LLVM fork 里，图中只按 pass 名和参数归纳。
2. 02 底部 addmm + ReLU 的指令序列是示意，实际指令数、顺序以及 epilogue 是否融合，要以生成的 `*_tog.py` / wrapper 为准。
3. 03 中 booksim2 互连和 SparseCore（stonne）只画了入口，内部没有展开。
4. `vpu_vector_length_bits` 在 Spike 和部分 Gem5 调用中固定为 256，图中按 256 标注。
