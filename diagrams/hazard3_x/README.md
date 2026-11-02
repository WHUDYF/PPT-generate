# Hazard3 X 级：一拍里完成 译码 → 取操作数 → 执行 → 决策

画法和 `../hazard3_frontend/` 一样（参照 curryGPU subcore 目标流水线图）。
`.drawio` 是源文件，`.svg` / `.png` 由导出得到，不要手改。

- `hazard3_x.drawio`：源文件，由 `gen_drawio.py` 生成（`python3 gen_drawio.py hazard3_x.drawio`）
- `hazard3_x.svg`：`drawio-export hazard3_x.drawio hazard3_x.svg` 导出
- `hazard3_x.png`：预览，可直接放进 PPT

依据：Hazard3 v1.1.1（commit `8af9929`）`hdl/hazard3_{decode,core}.v`、`hdl/arith/hazard3_alu.v`，
卡片里的灰色小字是源码位置；周期数来自 `doc/sections/instruction_timings.adoc`。

内容：

- 大流水线 F / X / M，X 展开成同一拍里的四步：X0 译码 · X1 取操作数（RF + bypass）· X2 执行（ALU、地址加法器、
  分支比较、乘除法、CSR 并行）· X3 决策与出口（停顿、跳转、访存地址相位、异常、结果选择）。
- 颜色按通路区分：蓝 = 指令通路，橙 = 数据通路，红 = 交叉点 / 决策，紫 = 多拍单元，绿 = 存储侧。
- 时钟沿只有 F | X（CIR、RF 读数据、bypass 选择）和 X | M（xm_*）；X0 → X3 之间没有时钟沿。
- 下方：握手 / 流控、跨级事件通道，以及卡片 ①–⑥（译码、取操作数、执行、跳转 / 访存 / 异常、停顿、
  指令通路与数据通路的交叉点 C1–C6），时序对照、与 F 级对照、图例。
