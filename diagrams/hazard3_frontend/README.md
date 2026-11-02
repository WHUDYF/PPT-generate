# Hazard3 F 级：一个大流水级套 5 个小级

画法照搬 curryGPU subcore 目标流水线图（`projects/currygpu_subcore_ppt169_20261004/sources/11-target-pipeline.drawio`，
「大流水线套小流水线」）：灰色级标题、彩色虚线容器、填色小级框、黑粗杠 = 时钟沿、黄色 owns、彩色反向事件通道。
`.drawio` 是源文件，`.svg` / `.png` 由导出得到，不要手改。

- `hazard3_frontend.drawio`：源文件，由 `gen_drawio.py` 生成（`python3 gen_drawio.py hazard3_frontend.drawio`）
- `hazard3_frontend.svg`：`drawio-export hazard3_frontend.drawio hazard3_frontend.svg` 导出
- `hazard3_frontend.png`：预览，可直接放进 PPT

依据：Hazard3 v1.1.1（commit `8af9929`）`hdl/hazard3_{frontend,core,decode,instr_decompress,cpu_2port}.v`，
卡片里的 `L数字` 是 `hazard3_frontend.v` 行号；官方流水线总图见 https://wren.wtf/hazard3/doc/#_pipeline_stages 。

内容：

- 大流水线 F / X / M，F 展开成 5 个小级：F0 发地址（蓝）· F1 收数据（绿，存储侧）· F2 预取 FIFO（紫，队列）·
  F3 指令缓冲 IB（紫，队列）· F4 预译码 / 解压（蓝），每级底部 owns 写它拥有的寄存器。
- 时钟沿只有两处：F0 → F1（总线地址相位 → 数据相位）和 F → X（IB 与 CIR 同沿锁存）；
  F1 → F4 在同一拍里组合完成（灰色虚线框），F2 / F3 是队列，空时旁路、不加延迟。
- 上方是存储侧接口（I 侧 AHB → 存储，以后可换成 I-cache），下方是握手 / 流控和反向事件通道
  （jump、cir_use、uop、BTB、jump_target_rdy）。
- 卡片 ①–⑥：预取与节流、跳转、分支与 BTB、取回数据的处理、IB 与 CIR、预译码 / 解压 / uop；
  以及时序对照、与 curryGPU ifetch_top 的对应、图例。
