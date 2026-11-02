# Hazard3 取指前端（F 级）微架构图

画法照搬 curryGPU `docs/design/uarch/ifetch_top.drawio`：`.drawio` 是源文件，`.svg` / `.png` 由导出得到，不要手改。

- `hazard3_frontend.drawio`：源文件，由 `gen_drawio.py` 生成（`python3 gen_drawio.py hazard3_frontend.drawio`）
- `hazard3_frontend.svg`：`drawio-export hazard3_frontend.drawio hazard3_frontend.svg` 导出
- `hazard3_frontend.png`：预览，可直接放进 PPT

依据：Hazard3 v1.1.1（commit `8af9929`）`hdl/hazard3_{frontend,core,decode,instr_decompress,cpu_2port}.v`，
图中 `L数字` 是 `hazard3_frontend.v` 行号；官方流水线总图见 https://wren.wtf/hazard3/doc/#_pipeline_stages 。

内容：

- 上半部分：hazard3_frontend 按一个字在 F 内经过的小级分成 5 列
  STAGE_F0 地址相位 → F1 数据相位 / 在途跟踪 → F2 预取 FIFO → F3 指令缓冲 IB → F4 预译码 / 解压 / CIR，
  每列列出寄存器（带位宽）和组合逻辑；左右是 core / decode / 寄存器堆接口，下方是 I 侧 AHB 和 PMP。
  蓝色粗箭头是同拍组合路径（读本拍的值），灰色虚箭头是寄存器输出。
- 下半部分：说明 ① 预取与节流、② 跳转、③ 分支与 BTB、④ 取回数据的处理、⑤ IB 与 CIR、⑥ 预译码 / 解压 / uop，
  以及时序对照（来自官方文档）和与 curryGPU ifetch_top 的对应关系。

Hazard3 RTL 结构完整，本图没有补齐或新增结构（curryGPU 图中的蓝框 / 红框约定在这里不出现）。
