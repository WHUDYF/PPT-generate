# curryGPU 取指子系统 → FML 模块与 task 切分（草案）

画法沿用 curryGPU `docs/design/uarch/`：`.drawio` 是源文件，`.svg` / `.png` 由导出得到，不要手改。

- `fml_ifetch_partition.drawio`：源文件，由 `gen_drawio.py` 生成（`python3 gen_drawio.py fml_ifetch_partition.drawio`）
- `fml_ifetch_partition.svg`：`drawio -x -f svg --embed-svg-fonts false` 导出
- `fml_ifetch_partition.png`：预览，可直接放进 PPT

内容：ifetch_top 拆成 FML 模块 Frontend ×4、Ib ×4、L1i ×1。列表示由访问模式（`&` / `&'latest` / `&mut`）推导出的一个时钟沿内的先后层次。编号 ①–⑥ 是 RTL 结构映射到 FML 时需要注意的点，其中 ⑤（launch / retire / exit 的时序）尚待核对。
