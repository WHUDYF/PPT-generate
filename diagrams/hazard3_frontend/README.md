# Hazard3 取指前端（F 级）内部结构

`.drawio` 是源文件，`.svg` / `.png` 由导出得到，不要手改。

- `hazard3_frontend.drawio`：源文件，由 `gen_drawio.py` 生成（`python3 gen_drawio.py hazard3_frontend.drawio`）
- `hazard3_frontend.svg`：`drawio-export hazard3_frontend.drawio hazard3_frontend.svg` 导出
- `hazard3_frontend.png`：预览，可直接放进 PPT

依据：Hazard3 v1.1.1（commit `8af9929`）`hdl/hazard3_frontend.v`，图中 `L数字` 是该文件行号；
官方流水线总图见 https://wren.wtf/hazard3/doc/#_pipeline_stages 。

内容：F 级在官方图里只是一列，内部其实是一条小流水——地址相位（和 X 同拍）→ 数据相位 → 2 项预取 FIFO →
3 个半字的指令缓冲 → 解压 → CIR。红色是同拍组合路径（cir_use 可能依赖 hready）。
编号 ①–⑥ 说明在途个数、为何 FIFO 至少 2 项、FIFO 旁路、最长同拍路径、跳转冲刷与 CIR 保留、为何没有组合环。
