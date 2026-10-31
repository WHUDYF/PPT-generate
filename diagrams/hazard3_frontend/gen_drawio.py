import html, sys
cells = []
n = [0]
def esc(s): return html.escape(s, quote=True).replace("\n", "&#xa;")
def text(x, y, w, h, v, size=10, bold=False, align="left", color="#000000"):
    n[0] += 1
    st = f"text;html=1;fontSize={size};align={align};verticalAlign=middle;strokeColor=none;fillColor=none;fontColor={color};" + ("fontStyle=1;" if bold else "")
    cells.append(f'<mxCell id="t{n[0]}" value="{esc(v)}" style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
def box(id, x, y, w, h, v, size=10, stroke="#000000", fill="#FFFFFF", bold=False, mono=False, valign="top", dashed=False, sw=1, rounded=False):
    st = (f"rounded={1 if rounded else 0};arcSize=6;whiteSpace=wrap;html=1;fontSize={size};strokeColor={stroke};fillColor={fill};align=left;"
          f"verticalAlign={valign};spacingLeft=6;spacingTop=3;strokeWidth={sw};")
    if bold: st += "fontStyle=1;"
    if mono: st += "fontFamily=Courier New;"
    if dashed: st += "dashed=1;"
    cells.append(f'<mxCell id="{id}" value="{esc(v)}" style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
def reg(id, x, y, w, h, v, **k): box(id, x, y, w, h, v, fill=REGFILL, **k)
def comb(id, x, y, w, h, v, **k): box(id, x, y, w, h, v, rounded=True, **k)
def ext(id, x, y, w, h, v, **k): box(id, x, y, w, h, v, dashed=True, stroke="#666666", **k)
def edge(id, s, t, label="", kind="data", pts=None, ex=None, en=None):
    color = {"data": "#000000", "comb": RED, "fb": "#888888"}[kind]
    st = f"endArrow=block;endSize=5;html=1;strokeColor={color};fontSize=9;fontColor={color};labelBackgroundColor=#FFFFFF;edgeStyle=orthogonalEdgeStyle;rounded=0;"
    if kind == "fb": st += "dashed=1;dashPattern=6 4;"
    if kind == "comb": st += "strokeWidth=2.5;"
    if ex: st += f"exitX={ex[0]};exitY={ex[1]};exitDx=0;exitDy=0;"
    if en: st += f"entryX={en[0]};entryY={en[1]};entryDx=0;entryDy=0;"
    g = '<mxGeometry relative="1" as="geometry">'
    if pts: g += '<Array as="points">' + "".join(f'<mxPoint x="{a}" y="{b}"/>' for a, b in pts) + '</Array>'
    g += '</mxGeometry>'
    cells.append(f'<mxCell id="{id}" value="{esc(label)}" style="{st}" edge="1" parent="1" source="{s}" target="{t}">{g}</mxCell>')
def vline(x, y0, y1):
    n[0] += 1
    cells.append(f'<mxCell id="v{n[0]}" value="" style="endArrow=none;html=1;dashed=1;dashPattern=6 6;strokeColor=#999999;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{x}" y="{y0}" as="sourcePoint"/><mxPoint x="{x}" y="{y1}" as="targetPoint"/></mxGeometry></mxCell>')

RED = "#CC0000"
REGFILL = "#FFF2CC"

# ---------- header ----------
text(20, 20, 1800, 28, "Hazard3 取指前端 hazard3_frontend.v（F 级）内部结构", 18, True)
text(20, 54, 2200, 18, "版本 Hazard3 v1.1.1（8af9929）   以 EXTENSION_C=1、2port 为例；BRANCH_PREDICTOR / PMP / DEBUG 可选（虚线）   对外接口：I 侧 AHB、X 级（cir / cir_use / jump）、寄存器堆读地址")
text(20, 76, 2200, 18, "官方流水线图里 F 只是一列，但它内部其实是一条小流水：地址相位 → 数据相位 → 预取 FIFO → 指令缓冲 → CIR。同一时刻可以有好几个字分别处在不同位置（见 ①）")
text(20, 98, 2200, 18, "L 数字 = hazard3_frontend.v 行号；core.v / decode.v 指 hazard3_core.v / hazard3_decode.v", 10, color="#555555")

# ---------- frontend box + phase columns ----------
box("fe", 280, 130, 1600, 640, "", fill="none", sw=2)
text(1480, 134, 390, 18, "hazard3_frontend   ×1", 12, True, "right")
vline(700, 130, 770); vline(1160, 130, 770)
text(290, 150, 400, 34, "拍 n · 地址相位\n（组合逻辑，和 X 级同一拍）", 11, True, "center")
text(710, 150, 440, 34, "拍 n+1 · 数据相位\n（F 拍：总线数据回来）", 11, True, "center")
text(1170, 150, 700, 34, "拍 n+1 组合计算，末沿锁存 → 拍 n+2 交给 X\n指令缓冲 + 解压 + CIR", 11, True, "center")

# ---------- column A: address phase ----------
reg("a_fa", 295, 200, 390, 110,
    "fetch_addr / fetch_priv   寄存器   L304\n"
    "取指地址，比 PC 超前，按整字 +4（L346）\n"
    "跳转时：jump_target 对齐到字，\n"
    "    若当拍地址已被接收再 +4（L327）\n"
    "BTB 命中时：换成 btb_target（L343）")
reg("a_hold", 295, 325, 390, 75,
    "mem_addr_hold   寄存器   L434\n"
    "上一拍发出的地址没被接收（hready=0）\n"
    "→ 本拍必须原样保持；jump_target_rdy = !hold（L401）")
comb("a_stall", 295, 415, 390, 90,
    "fetch_stall   组合   L416\n"
    "= fifo_full\n"
    "|| fifo_almost_full && pending_fetches ≠ 0\n"
    "|| pending_fetches > 1        （都用寄存器，见 ②）")
comb("a_mux", 295, 520, 390, 105,
    "地址选择 mem_addr   组合   L385\n"
    "优先级：hold > jump > debug 停取\n"
    "        > !fetch_stall 发 fetch_addr > 不发\n"
    "总是 32 bit、整字对齐（L381）", bold=False)
ext("a_btb", 295, 640, 390, 60,
    "BTB 1 项（可选 BRANCH_PREDICTOR）   L254\n"
    "记住最近一次后向 taken 分支，命中则地址直接跳")

# ---------- column D: data phase ----------
reg("d_trk", 715, 200, 430, 120,
    "总线在途跟踪   寄存器   L408、L452\n"
    "pending_fetches 0..2：已发地址、还没回数据的个数\n"
    "ctr_flush_pending：跳转那一拍仍在途的个数，\n"
    "    这些数据回来后直接丢弃（L437）\n"
    "mem_data_hwvld：本字哪一半有效\n"
    "    （跳到奇数半字时，低半无效）")
ext("d_pmp", 715, 335, 430, 55,
    "PMP X 检查 / 断点比较（可选）   L500\n"
    "和数据相位并行；失败当作总线错误随数据走")
reg("d_fifo", 715, 405, 430, 130,
    "预取 FIFO   2 项 × 32 bit   寄存器   L149\n"
    "每项附带：valid_hw[1:0]  err  break  predbranch\n"
    "推入：数据回来，且没能直接进缓冲（L425）\n"
    "弹出：缓冲有空位 cir_room_for_fetch（L635）\n"
    "跳转 jump_now：全部清空（L212）")
comb("d_byp", 715, 550, 430, 75,
    "旁路选择 fetch_data   组合   L592\n"
    "FIFO 空 → 直接用总线数据（见 ③）\n"
    "否则 → 用 FIFO 头")

# ---------- column B: instruction buffer / CIR ----------
comb("b_shift", 1175, 200, 335, 85,
    "移位 buf_shifted   组合   L625\n"
    "按 cir_use（X 本拍用掉 0/1/2 个半字）\n"
    "把还没用的半字往下移")
comb("b_ovl", 1175, 300, 335, 130,
    "叠加新字 buf_shifted_plus_fetch   L637\n"
    "剩余 ≤1 个半字（新字只有半个有效时 ≤2）\n"
    "    才收新字 → cir_room_for_fetch\n"
    "跳转：清空；若 cir_flush_behind，\n"
    "    保留当前指令（L648，见 ⑤）")
comb("b_next", 1175, 445, 335, 55,
    "next_instr = 下一拍的槽 0、1   L701\n"
    "（还没锁存，组合给出）")
comb("b_pre", 1175, 515, 335, 110,
    "寄存器号预译码   组合   L734\n"
    "predecode_rs1/rs2_coarse → 寄存器堆读地址\n"
    "predecode_rs1/rs2_fine → core 的 bypass 选择\n"
    "比 X 级正式译码早一拍")
reg("b_buf", 1530, 200, 340, 150,
    "指令缓冲 buf_contents   寄存器   L589\n"
    "3 槽 × (16 bit 指令 + 4 bit 元数据)\n"
    "buf_level 0..3：有效半字数\n"
    "槽 0、1 = CIR 的原始内容（cir_raw）\n"
    "槽 2：让 CIR 可以不按字对齐（C 扩展）")
comb("b_dec", 1530, 445, 340, 80,
    "解压 hazard3_instr_decompress   L844\n"
    "16 bit → 32 bit；Zcmp push/pop 拆成 uop\n"
    "（uop 计数器在解压模块里）")
reg("b_cir", 1530, 540, 340, 120,
    "CIR   寄存器   L874\n"
    "cir（已解压的 32 bit）  cir_vld  cir_is_32bit\n"
    "uop 标志：is_uop / nonfinal / atomic\n"
    "和 buf_contents 同一个时钟沿更新\n"
    "（CIR 不是另一份指令，是槽 0、1 的解压版）")

# ---------- outside: inputs (left) ----------
ext("i_jump", 20, 200, 240, 110,
    "X 级：jal / 分支 taken\nM 级：trap 进入\n→ jump_target / jump_target_vld\n   core.v:1376")
ext("i_btb", 20, 330, 240, 70,
    "X 级：btb_set / btb_clear\n（只有开分支预测时）")

# ---------- outside: outputs (right) ----------
ext("o_rf", 1910, 680, 250, 80,
    "寄存器堆读端口（core）\n读地址 = predecode_rs*_coarse\n拍 n+2 开始 X 拿到读值")
ext("o_dec", 1910, 560, 250, 100,
    "X 级 decode（decode.v）\n读 cir / cir_vld\n算出 cir_use（decode.v:142）\n和跳转请求")

# ---------- bus (bottom) ----------
ext("ahb", 295, 800, 850, 75,
    "I 侧 AHB 总线（2port 时独立；1port 时和 load/store 仲裁）\n"
    "拍 n 地址相位：HADDR / HTRANS ← mem_addr、mem_addr_vld          拍 n+1 数据相位：HRDATA / HREADY → mem_data、mem_data_vld\n"
    "hready 拉低会插等待：地址要保持（mem_addr_hold），数据晚到；pending_fetches 最多 2", size=10)

# ---------- edges ----------
edge("e1", "i_jump", "a_mux", "", "comb", ex=(1, 0.8), en=(0, 0.4), pts=[(275, 288), (275, 562)])
edge("e2", "a_fa", "a_mux", "", "data", ex=(0.9, 1), en=(0.9, 0), pts=[(646, 512)])
edge("e3", "a_hold", "a_mux", "", "data", ex=(0.75, 1), en=(0.75, 0))
edge("e4", "a_stall", "a_mux", "", "data")
edge("e5", "a_mux", "ahb", "mem_addr", "data", ex=(0.5, 1), en=(0.15, 0))
edge("e6", "ahb", "d_byp", "mem_data", "data", ex=(0.65, 0), en=(0.3, 1))
edge("e7", "ahb", "d_fifo", "", "data", ex=(0.9, 0), en=(1, 0.88), pts=[(1060, 785), (1152, 785), (1152, 519)])
edge("e8", "d_fifo", "d_byp", "", "data", ex=(0.6, 1), en=(0.6, 0))
edge("e9", "d_byp", "b_ovl", "", "data", ex=(1, 0.5), en=(0, 0.75), pts=[(1167, 587), (1167, 397)])
edge("e10", "b_shift", "b_ovl", "", "comb")
edge("e11", "b_ovl", "b_next", "", "comb")
edge("e12", "b_next", "b_pre", "", "comb")
edge("e13", "b_next", "b_dec", "", "comb", ex=(1, 0.5), en=(0, 0.3))
edge("e14", "b_dec", "b_cir", "", "comb", ex=(0.5, 1), en=(0.5, 0))
edge("e15", "b_ovl", "b_buf", "", "data", ex=(1, 0.3), en=(0, 0.75))
edge("e16", "b_buf", "b_shift", "", "fb", ex=(0, 0.25), en=(1, 0.5), pts=[(1520, 237), (1520, 242)])
edge("e17", "b_pre", "o_rf", "rs1 / rs2", "comb", ex=(0.5, 1), en=(0, 0.5), pts=[(1342, 720)])
edge("e18", "b_cir", "o_dec", "cir", "data", ex=(1, 0.5), en=(0, 0.5))
edge("e19", "o_dec", "b_shift", "cir_use（同拍，可能依赖 hready）", "comb", ex=(0.5, 0), en=(0.045, 0), pts=[(2035, 118), (1190, 118)])
edge("e20", "b_ovl", "d_fifo", "fifo_pop", "comb", ex=(0, 0.25), en=(1, 0.35), pts=[(1150, 332), (1150, 450)])
edge("e21", "i_jump", "d_trk", "", "data", ex=(1, 0.2), en=(0, 0.3), pts=[(268, 222), (268, 192), (705, 192), (705, 236)])
text(20, 420, 245, 34, "jump_target 同拍直接驱动地址\njump_now 同时通知在途跟踪", 9, False, "right", RED)
edge("e22", "a_fa", "a_btb", "", "fb", ex=(0, 0.5), en=(0, 0.5), pts=[(287, 255), (287, 670)])
edge("e23", "i_btb", "a_btb", "", "data", ex=(0.5, 1), en=(0, 0.8), pts=[(140, 688)])

# ---------- legend ----------
box("lg", 20, 900, 250, 200,
    "图例\n\n"
    "黄底方框      寄存器（状态）\n"
    "白底圆角框    组合逻辑\n"
    "虚线框        frontend 之外，或可选\n\n"
    "红粗箭头      同拍组合路径（见 ④）\n"
    "黑细箭头      数据 / 控制\n"
    "灰虚箭头      寄存器输出（上一拍的值）", size=10)

# ---------- timeline ----------
box("tl", 290, 900, 560, 200,
    "例：jal 之后的取指（无总线等待；文档 jal = 2 拍）\n\n"
    "拍  地址相位      数据相位          X 级\n"
    "0   T（目标）     -                 jal，发跳转\n"
    "1   T+4           T → 缓冲 + CIR    气泡（缓冲被清空）\n"
    "2   T+8           T+4               执行 T\n\n"
    "jump_target 当拍就作为地址发出，\n"
    "所以只损失 1 拍。".replace(" ", "\u00a0"), size=10, mono=True)

# ---------- callouts ----------
co = [
 ("#000000", "① 隐藏的小流水",
  "同一时刻 F 里可以有：1 个地址相位 + 1 个数据相位（pending_fetches ≤ 2）、FIFO 里 2 个字、缓冲里最多 3 个半字。和 X 级「只有 0 或 1 条指令」不同，这里有好几个不同地址的字同时处在不同位置。"),
 ("#000000", "② 不让 hready 组合地影响发地址",
  "fetch_stall 用寄存器版的 pending_fetches（L413 注释）。代价：要按「最坏还有一个在途」预留空间，所以 FIFO 至少 2 项才能满速取指（L119）。"),
 ("#000000", "③ FIFO 旁路",
  "FIFO 空且缓冲有空位时，总线数据当拍直接进缓冲和 CIR，不进 FIFO（L425、L594）。无等待时：拍 n 发地址 → 拍 n+1 数据进 CIR → 拍 n+2 X 译码。"),
 (RED, "④ 最长的同拍路径（红色）",
  "hready → X 的 stall → cir_use → 移位 → 叠加 → next_instr → 预译码 → 寄存器堆读地址；以及 → 解压 → CIR、→ fifo_pop。接口注释明确允许 cir_use 依赖 hready（L54）。"),
 (RED, "⑤ 跳转与 CIR 保留",
  "jump_target 当拍驱动地址（L391），jump_now 当拍清空 FIFO 和缓冲；已发出未回来的请求由 ctr_flush_pending 记数后丢弃。X 被 stall 却发了跳转时（stall 依赖 hready，挡不住），cir_flush_behind 保留当前指令，只冲刷后面的（L648，decode.v:146）。"),
 ("#000000", "⑥ 没有组合环",
  "jump_target_rdy = !mem_addr_hold 来自寄存器（L401），X 的跳转不会反过来依赖本拍 hready。mem_addr_rdy、mem_data_vld 也不进入任何组合输出（L19 接口约定）。"),
]
for i, (c, title, body) in enumerate(co):
    col, row = i % 3, i // 3
    x, y = 870 + col * 435, 900 + row * 106
    box(f"co{i}", x, y, 425, 98, title + "\n" + body, size=10, stroke=c, sw=2 if c != "#000000" else 1)

xml = ('<mxfile host="app.diagrams.net"><diagram name="hazard3_frontend"><mxGraphModel dx="1800" dy="1000" grid="1" gridSize="10" '
       'page="1" pageWidth="2200" pageHeight="1130" math="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
       + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>\n')
open(sys.argv[1], "w").write(xml)
