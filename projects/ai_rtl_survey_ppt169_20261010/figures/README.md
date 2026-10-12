# HINT 结构图（从作者角度）

HINT: Toward an Executable Hardware-Intent Representation Layer for LLM-Driven RTL Generation，arXiv 2608.07625v2。

依据只有论文正文文字：论文的图 1–3 是图片，HINT 规范和代码要到正式发表才公开。所以框内名称用的是论文术语，不是 HINT 语法；图 2 的 AES 代码是按论文图 1 的文字描述重建的示意。

| 文件 | 内容 |
|---|---|
| `hint-01-workflow.drawio` | Stage 0–3：环境 agent 冻结测试与契约 → 生成并验收 HINT（lint、可执行验收）→ 按 lowering 义务写 RTL 并 co-sim → 综合；回边（架构要改回 Stage 1）；最小流程与完整工作流对比；关卡与缺陷类别 |
| `hint-02-ir.drawio` | 论文表 1 的五层义务；一个 unit 的构成（类型化边界、step 入口、自有状态、commit、子实例、执行模型标签、资源标注、lowering 义务）；规范形式；共享 round AES 示意 |
| `hint-03-checks.drawio` | 四道关卡与冻结后审计；形式验证只覆盖 Hif8_mul；HINT 里的"时序"= 延迟 / II；比较粒度轴（行为 / 事务 / 逐拍契约 / 信号） |
| `hint-04-vortex.drawio` | Vortex VPU：C++ oracle（48 定向 + 500 随机根事务）、按归属切 5 块（行数、面积）、逐块 co-sim 后顶层复验 |
| `hint-05-their-view.drawio` | 左：作者的设计理由（原文）；右：用 HINT 写 subcore S1 / S2 的推演（未实验） |

同名 `.png` 是 `drawio-export` 的渲染。生成脚本在 curryGPU 本地 `document/tools/gen-hint.py`（未入库）。
