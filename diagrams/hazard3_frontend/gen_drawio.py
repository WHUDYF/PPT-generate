import html, math, sys
cells = []
n = [0]
def esc(s): return html.escape(s, quote=True).replace("\n", "&#xa;")
def nid(p):
    n[0] += 1
    return f"{p}{n[0]}"
def text(x, y, w, h, v, size=9, bold=False, align="left", color="#000000", valign="middle"):
    st = f"text;html=1;fontSize={size};align={align};verticalAlign={valign};strokeColor=none;fillColor=none;fontColor={color};" + ("fontStyle=1;" if bold else "")
    cells.append(f'<mxCell id="{nid("t")}" value="{esc(v)}" style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
def box(id, x, y, w, h, v, size=9, stroke="#000000", sw=1, dashed=False, top=False, align="center", shape=None):
    st = f"rounded=0;whiteSpace=wrap;html=1;fontSize={size};strokeColor={stroke};fillColor=none;align={align};"
    if sw != 1: st += f"strokeWidth={sw};"
    if dashed: st += "dashed=1;dashPattern=8 6;"
    if top: st += "verticalAlign=top;spacingTop=3;"
    if shape == "trap": st = f"shape=trapezoid;perimeter=trapezoidPerimeter;whiteSpace=wrap;html=1;fontSize={size};direction=south;strokeColor={stroke};fillColor=none;"
    cells.append(f'<mxCell id="{id or nid("b")}" value="{esc(v)}" style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
def edge(s, t, label="", kind="data", pts=None, ex=None, en=None):
    color = {"data": "#000000", "comb": BLUE, "reg": "#888888"}[kind]
    st = f"endArrow=block;endSize=4;html=1;strokeColor={color};fontSize=8;fontColor={color};labelBackgroundColor=#FFFFFF;edgeStyle=orthogonalEdgeStyle;rounded=0;"
    if kind == "comb": st += "strokeWidth=2;"
    if kind == "reg": st += "dashed=1;dashPattern=6 4;"
    if ex: st += f"exitX={ex[0]};exitY={ex[1]};exitDx=0;exitDy=0;"
    if en: st += f"entryX={en[0]};entryY={en[1]};entryDx=0;entryDy=0;"
    g = '<mxGeometry relative="1" as="geometry">'
    if pts: g += '<Array as="points">' + "".join(f'<mxPoint x="{a}" y="{b}"/>' for a, b in pts) + '</Array>'
    g += '</mxGeometry>'
    cells.append(f'<mxCell id="{nid("e")}" value="{esc(label)}" style="{st}" edge="1" parent="1" source="{s}" target="{t}">{g}</mxCell>')
def vline(x, y0, y1):
    cells.append(f'<mxCell id="{nid("v")}" value="" style="endArrow=none;html=1;dashed=1;dashPattern=6 6;strokeColor=#999999;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{x}" y="{y0}" as="sourcePoint"/><mxPoint x="{x}" y="{y1}" as="targetPoint"/></mxGeometry></mxCell>')

BLUE = "#0066CC"
GREY = "#777777"

def tw(s):  # rough text width, in 9pt CJK characters
    return sum(1.0 if ord(c) > 0x2E80 else 0.56 for c in s)
def rowh(v, w, size=9):
    per = (w - 12) / (size + 0.6)
    lines = sum(max(1, math.ceil(tw(l) / per)) for l in v.split("\n"))
    return 6 + lines * (size + 3)

def column(x, y, w, items):
    """Stack rows inside one module column; returns the bottom y.
    items: ("row", text[, id[, dashed]]) | ("group", title, [rows], "group"|"opt", id) | ("trap", text)"""
    cy = y + 30
    for it in items:
        k = it[0]
        if k == "row":
            v = it[1]; h = rowh(v, w - 22)
            box(it[2] if len(it) > 2 else None, x + 11, cy, w - 22, h, v, dashed=len(it) > 3 and it[3])
            cy += h + 6
        elif k == "trap":
            box(None, x + w / 2 - 55, cy, 110, 28, it[1], shape="trap")
            cy += 34
        else:
            _, gt, rows, style, gid = it
            inner = cy + 22
            for r in rows:
                h = rowh(r, w - 42)
                box(None, x + 21, inner, w - 42, h, r)
                inner += h + 3
            stroke, sw, dashed = {"group": ("#000000", 2, False), "opt": (GREY, 1.5, True)}[style]
            box(gid, x + 11, cy, w - 22, inner - cy + 4, gt, stroke=stroke, sw=sw, dashed=dashed, top=True)
            cy = inner + 10
    return cy

# ---------- header ----------
text(20, 30, 1600, 26, "Hazard3 微架构   —   取指前端 hazard3_frontend（F 级）", 17, True)
text(20, 66, 2500, 16, "参数   Hazard3 v1.1.1（8af9929）   取指总线 32 bit / 拍   FIFO_DEPTH=2 字   IB=3 半字槽   在途 ≤2   以 EXTENSION_C=1、2port 为例；BRANCH_PREDICTOR / PMP / DEBUG / Zcmp 可选（虚线）")
text(20, 86, 2500, 16, "层次   hazard3_cpu_2port → hazard3_core → hazard3_frontend ×1（906 行）+ hazard3_instr_decompress ×1；单线程，F / X / M 三级，地址相位逻辑上在 X 拍、数据相位在 F 拍")
text(20, 106, 2500, 16, "画法   按 curryGPU ifetch_top 的方式重排：列 = 一个字在 F 内依次经过的小级（STAGE_F0..F4）；Hazard3 RTL 结构完整，本图没有补齐或新增；L 数字 = hazard3_frontend.v 行号")

# ---------- big box ----------
BX, BY, BW = 245, 150, 2050

COLW = 360
COLX = [265, 665, 1065, 1465, 1865]
MY = 235
MID = ["m_fa", "m_trk", "m_fifo", "m_ib", "m_cir"]

bottoms = [
column(COLX[0], MY, COLW, [
    ("row", "fetch_addr_q[32]   fetch_priv_q\n顺序取指地址，按字对齐，比 PC 超前\n地址被总线接收 → +4   L346", "fa"),
    ("row", "跳转被接受（jump_now）\nfetch_addr ← {target[31:2], 00} + (当拍已接收 ? 4 : 0)   L327"),
    ("row", "mem_addr_hold_q   上拍地址没被接收（hready=0）\n→ 本拍必须原样保持   jump_target_rdy = !hold   L401 L434", "hold"),
    ("group", "fetch_stall   预取节流   ①", [
        "fifo_full",
        "|| fifo_almost_full && pending_fetches ≠ 0",
        "|| pending_fetches > 1",
        "只看寄存器，不看本拍 hready   L413-418"], "group", "stall"),
    ("group", "BTB   1 项（BRANCH_PREDICTOR）   ③", [
        "btb_src_addr_q[32]  btb_src_size_q  btb_target_addr_q[32]  btb_valid_q",
        "fetch_addr 落在 btb_src 所在字 → 下一个地址换成 btb_target   L343",
        "set：X 中 taken 的后向条件分支   clear：预测错 / trap / fence.i"], "opt", "btb"),
    ("row", "reset_holdoff_q   复位后（上电协商完成前）不发   L355"),
    ("trap", "地址选择"),
    ("row", "优先级   hold > jump > debug 停取 > !fetch_stall 发 fetch_addr > 不发\nmem_addr 总是 32 bit、按字对齐   L385-399", "amux"),
]),
column(COLX[1], MY, COLW, [
    ("row", "pending_fetches_q[2]   已发地址、未回数据   0..2\n+1 新发地址（非保持）   −1 mem_data_vld   L411", "pend"),
    ("row", "ctr_flush_pending_q[2]   跳转那拍仍在途的个数\n之后每回来一个就丢一个、减 1   L436-439   ②", "flush"),
    ("row", "mem_aph_hwvld_q[2] → mem_data_hwvld_q[2]\n本字哪一半有效：跳到奇数半字 → 低半无效   L452-466"),
    ("row", "mem_data_predbranch_q[2]   本字哪一半属于预测 taken 的分支   L482-489"),
    ("group", "数据去向   ④", [
        "ctr_flush_pending ≠ 0   →   丢弃（跳转前的旧请求）",
        "FIFO 空 且 IB 有空位   →   旁路，当拍进 IB   L594",
        "否则   →   推入 FIFO（fifo_push）   L425"], "group", "steer"),
    ("row", "check_addr_dph_q[32]   PMP X 检查 / 断点比较\n与数据相位并行；失败记为总线错误，随数据走   L500-563", "pmpchk", True),
]),
column(COLX[2], MY, COLW, [
    ("row", "fifo_mem[2][32]   2 项 × 32 bit，按字对齐", "fifo"),
    ("row", "每项元数据   valid_hw[2]   err   break_any[2]   break_d_mode[2]   predbranch[2]"),
    ("row", "推入 fifo_push：数据回来且没走旁路\n弹出 fifo_pop = cir_room_for_fetch && !fifo_empty   L635", "fpop"),
    ("row", "jump_now → 全部 valid 清 0   L212"),
    ("row", "fifo_full = valid[1]    fifo_almost_full = valid[0]\n给 fetch_stall 用   L159-161", "ffull"),
    ("trap", "取数选择"),
    ("row", "fetch_data = FIFO 空 ? 总线数据 : FIFO 头\n元数据同样二选一   L592-599", "fdata"),
    ("row", "2 项是满速的下限：停发那拍最多还有 1 个在途   L119"),
    ("row", "debug 注入：DM 直接写 FIFO 第 0 项   L223", "dbgin", True),
]),
column(COLX[3], MY, COLW, [
    ("row", "buf_contents_q[3][20]   3 槽 × (16 bit + 4 bit 元数据)\n元数据 = break_any  break_d_mode  err  predbranch", "buf"),
    ("row", "移位 buf_shifted\n按 cir_use（0 / 1 / 2 个半字）把未用的下移   L625", "shift"),
    ("row", "叠加 buf_shifted_plus_fetch\n新字放在剩余半字之后   L637-641", "ovl"),
    ("row", "cir_room_for_fetch   剩余 ≤ 1 半字\n（新字只半个有效时 ≤ 2）才收新字   L634", "room"),
    ("row", "buf_level_q[2]   有效半字数 0..3"),
    ("row", "fetch_contents_aligned   新字只有高半有效时\n把高半放到低位   L617"),
    ("row", "buf_level_next   jump：清 0\ncir_flush_behind：保留当前指令（1 或 2 槽）   L647-650"),
    ("row", "槽 0、1 = cir_raw（CIR 的原始内容）\n槽 2：让 CIR 可以跨字（C 扩展）"),
]),
column(COLX[4], MY, COLW, [
    ("row", "next_instr[32] = 下一拍的槽 0、1\n取自叠加结果，组合给出   L701", "next"),
    ("group", "寄存器号预译码   ⑥", [
        "predecode_rs1/rs2_coarse[5] → 寄存器堆读地址",
        "predecode_rs1/rs2_fine[5] → core 的 bypass 选择",
        "比 X 正式译码早一拍   L734-799"], "group", "pre"),
    ("group", "hazard3_instr_decompress   ⑥", [
        "16 bit → 32 bit；非法压缩码置 invalid",
        "Zcmp push / pop 拆成 uop 序列，计数在模块内",
        "uop_stall / uop_clear 来自 X   L838-864"], "group", "dec"),
    ("group", "CIR 寄存器", [
        "cir_q[32]（已解压）  cir_is_32bit  cir_invalid_16bit",
        "cir_is_uop  uop_nonfinal  uop_no_pc_update  uop_atomic",
        "cir_clken：CIR 空 / 被用掉 / uop 前进时更新   L866",
        "cir_vld = min(buf_level, 2)   L661"], "group", "cir"),
    ("row", "cir_err / cir_predbranch / cir_break\n直接取自 IB 槽 0、1   L684-696"),
]),
]

heads = ["取指地址   fetch_addr 生成        L300-401", "在途跟踪 · 收数据        L404-563", "预取 FIFO        L123-244",
         "指令缓冲 IB        L565-697   ⑤", "预译码 · 解压 · CIR        L699-900"]
MB = max(bottoms)
BH = MB - BY + 80
cells.insert(0, f'<mxCell id="big" value="" style="rounded=0;html=1;strokeColor=#000000;fillColor=none;" vertex="1" parent="1"><mxGeometry x="{BX}" y="{BY}" width="{BW}" height="{BH}" as="geometry"/></mxCell>')
text(BX + BW - 460, BY + 5, 450, 16, "hazard3_frontend      ×1 per core", 11, True, "right")
for i in range(5):
    box(MID[i], COLX[i], MY, COLW, MB - MY, heads[i], size=11, top=True)

for i in range(1, 5):
    vline(COLX[i] - 20, BY, BY + BH)
stages = ["STAGE_F0\n地址相位（和 X 同拍）", "STAGE_F1\n数据相位 / 在途跟踪", "STAGE_F2\n预取 FIFO", "STAGE_F3\nIB 移位 / 叠加", "STAGE_F4\n预译码 / 解压 / CIR → X"]
for i, s in enumerate(stages):
    text(COLX[i] + COLW / 2 - 110, BY + BH + 6, 220, 32, s, 10, align="center", valign="top")

# ---------- externals ----------
box("x_jump", 20, 250, 215, 70, "core   跳转 / trap\njump_target_vld   jump_target[32]\njump_priv   core.v:1376\nX：jal / jalr / taken 分支   M：trap")
box("x_pwr", 20, 420, 215, 40, "power_ctrl\ndelay_first_fetch   ← pwrdown_ok")
box("x_btb", 20, MB - 120, 215, 56, "core   BTB 维护\nbtb_set   src_addr[32]   src_size\ntarget[32]   btb_clear   core.v:943", stroke=GREY, dashed=True)
box("x_dbg", 20, MB + 10, 215, 40, "debug module\ndbg_instr_data[32]   vld / rdy", stroke=GREY, dashed=True)

RX = 2330
box("o_rf", RX, 330, 250, 40, "regfile 读端口\n← predecode_rs1/rs2_coarse[5]")
box("o_byp", RX, 390, 250, 40, "core bypass 选择   core.v:508\n← predecode_rs1/rs2_fine[5]")
box("o_dec", RX, 560, 250, 96, "X 级 decode / core\n← cir[32]   cir_vld[2]   cir_is_32bit\ncir_err[2]   cir_predbranch[2]   cir_break_*\nuop 标志\n→ cir_use[2]   cir_flush_behind\n→ uop_stall   uop_clear")
box("o_pc", RX, MB + 30, 250, 40, "decode PC 更新   decode.v:224\n← btb_target_addr_out[32]", stroke=GREY, dashed=True)

box("ahb", 265, BY + BH + 50, 360, 92, "I 侧 AHB5   hazard3_cpu_2port.v:208-235\n（1port 时与 load / store 仲裁）\n地址相位 → HADDR[32]  HTRANS=NSEQ  HSIZE=字\nmem_addr_rdy = hready && req\n数据相位 ← HRDATA[32]  HRESP\nmem_data_vld = hready && dphase_active")
box("pmp", 665, BY + BH + 50, 360, 58, "PMP / trigger 单元（可选）\n← pmp_i_addr   trigger_addr\n→ pmp_i_kill   trigger_break_any / d_mode", stroke=GREY, dashed=True)

# ---------- edges ----------
TOPY = 196
edge("x_jump", "amux", "", "comb", ex=(1, 0.75), en=(0, 0.5), pts=[(252, 302)])
text(20, 324, 215, 28, "jump_target[32]：同拍驱动地址选择\njump_now：同拍通知在途跟踪", 9, color=BLUE)
edge("x_jump", "m_trk", "jump_now：记在途、清 FIFO / IB", "comb", ex=(1, 0.2), en=(0.5, 0), pts=[(252, 264), (252, TOPY - 14), (COLX[1] + COLW / 2, TOPY - 14)])
edge("x_pwr", "m_fa", "", "data", ex=(1, 0.5), en=(0, 0.25))
edge("x_btb", "btb", "", "data", ex=(1, 0.5), en=(0, 0.5))
edge("amux", "ahb", "mem_addr[32]   mem_addr_vld", "data", ex=(0.3, 1), en=(0.15, 0))
edge("ahb", "steer", "mem_data[32]\nmem_data_vld   err", "data", ex=(1, 0.2), en=(0, 0.5), pts=[(650, BY + BH + 68)])
edge("pend", "stall", "pending_fetches", "reg", ex=(0, 0.5), en=(1, 0.3))
edge("ffull", "stall", "fifo_full / almost_full", "reg", ex=(0, 0.5), en=(1, 0.75), pts=[(1040, MY - 10), (640, MY - 10)])
edge("steer", "fifo", "fifo_push   数据 + 元数据", "data", ex=(1, 0.3), en=(0, 0.5))
edge("fdata", "ovl", "fetch_data[32]   hwvld[2]   元数据", "data", ex=(1, 0.5), en=(0, 0.5))
edge("room", "fpop", "fifo_pop", "comb", ex=(0, 0.5), en=(1, 0.5))
edge("shift", "ovl", "", "comb", ex=(0.5, 1), en=(0.5, 0))
edge("ovl", "next", "", "comb", ex=(1, 0.5), en=(0, 0.5))
edge("buf", "shift", "", "reg", ex=(0.85, 1), en=(0.85, 0))
edge("cir", "o_dec", "cir   cir_vld   …", "data", ex=(1, 0.5), en=(0, 0.3), pts=[(2255, 589)])
edge("pre", "o_rf", "", "comb", ex=(1, 0.3), en=(0, 0.5))
edge("pre", "o_byp", "", "comb", ex=(1, 0.7), en=(0, 0.5))
edge("o_dec", "shift", "cir_use[2]   cir_flush_behind（同拍，可能依赖 hready）", "comb", ex=(0.5, 0), en=(1, 0.5), pts=[(RX + 125, TOPY), (COLX[4] - 8, TOPY)])
edge("o_dec", "dec", "uop_stall / uop_clear", "data", ex=(0, 0.85), en=(1, 0.5), pts=[(2312, 642)])
edge("btb", "o_pc", "btb_target_addr_out[32]", "reg", ex=(1, 0.5), en=(0, 0.5), pts=[(635, MB + 50)])
edge("pmpchk", "pmp", "", "data", ex=(0.5, 1), en=(0.5, 0))
edge("x_dbg", "dbgin", "", "data", ex=(1, 0.5), en=(0, 0.5), pts=[(1040, MB + 30)])

# ---------- callouts ----------
CW = 840
def callout(x, y, title, rows):
    inner = y + 30
    rs = []
    for r in rows:
        h = rowh(r, CW - 28)
        rs.append((inner, h, r)); inner += h + 4
    box(None, x, y, CW, inner - y + 8, title, size=10, sw=2, top=True)
    for ry, h, r in rs:
        box(None, x + 14, ry, CW - 28, h, r)
    return inner - y + 8

C = [
 ("①  预取：顺序取指与节流", [
  "fetch_addr 每被接收一次就 +4：F 总是按字在 PC 前面取，取回的字先放进 FIFO / IB，等 X 来用   L346",
  "要不要再发由 fetch_stall 决定：FIFO 满；或 FIFO 有 1 项且还有在途；或在途 ≥ 2   L416-418",
  "它按「在途的都会回来」预留空间，只看寄存器、不看本拍 hready → hready 不会组合地影响下一个地址   L413",
  "例   X 停住（div）   拍 0 发 W1 · 拍 1 发 W2、W1 进 FIFO · 拍 2 停发、W2 进 FIFO（满）· 之后一直停发，直到 X 恢复消耗",
  "结论   FIFO 2 项是满速取指的下限；32 bit 指令每拍用掉 1 个字，正好等于取指带宽；RVC 指令消耗慢，FIFO 很快满，取指自动降速",
 ]),
 ("②  跳转：jal / jalr / taken 分支 / trap", [
  "来源   X：jal、jalr、taken 条件分支，目标在 X 用 x_addr_sum 算出      M：trap 进入，优先于 X   core.v:1376-1377",
  "接受条件   jump_target_rdy = !mem_addr_hold：上拍地址正被总线保持时不能换地址，X 停一拍   L401   core.v:478",
  "被接受那拍（jump_now）：目标当拍直接作为 mem_addr 发出，不经过 fetch_addr；fetch_addr ← 目标（已被接收则再 +4）   L391 L327",
  "同拍冲刷：FIFO 全清、IB 清 0；已发出未返回的请求个数记入 ctr_flush_pending，它们回来时被丢掉   L212 L436 L649",
  "跳到奇数半字：首字低半无效（hwvld=10）；若目标是 32 bit 指令还要再取一个字，多 1 拍   L462",
  "CIR 保留：X 被 stall（stall 依赖 hready，挡不住跳转）却发了跳转 → cir_flush_behind=1，保留当前指令、只冲刷后面的   L648   decode.v:146",
  "代价   jal = 2 拍：拍 0 X 发目标 · 拍 1 目标数据进 IB / CIR（X 空 1 拍）· 拍 2 X 执行目标指令",
 ]),
 ("③  分支：默认不跳，可选 1 项 BTB", [
  "条件分支在 X 比较（FAST_BRANCHCMP 时用专门比较器）；taken 就按 ② 发跳转；不 taken 什么都不做 → 等于静态预测「不跳」   core.v:935",
  "BRANCH_PREDICTOR=1：BTB 只记最近一次 taken 的后向条件分支（循环回跳）   set core.v:943   clear core.v:948",
  "F 侧：fetch_addr 落在 btb_src 所在字 → 下一个地址直接换成 btb_target，并给该指令的半字打 predbranch 标记   L343 L482",
  "X 侧：带 predbranch 的分支比较结果取反、偏移改成指令长度 → 预测对：不发跳转，PC ← btb_target；预测错：跳回顺序地址并清 BTB   core.v:912   decode.v:224 242",
  "代价   预测对 1 拍（两段取指被拼成连续的）      未预测的 taken / 预测错 2 拍",
 ]),
 ("④  取回的数据怎么处理", [
  "数据回来（mem_data_vld）先看 ctr_flush_pending：非 0 → 是跳转前发出的旧请求，丢弃   L425 L592",
  "否则带上元数据：hwvld（哪半有效）、err（总线错误或 PMP 失败）、break（断点）、predbranch（预测分支）   L129-147",
  "FIFO 空 且 IB 有空位 → 旁路，当拍进 IB 并算出下一拍 CIR；否则推入 FIFO，等 IB 有空位再弹出   L425 L594 L635",
  "进 IB 前先对齐：只有高半有效时把高半放到低位（fetch_contents_aligned）   L617",
  "叠加：新字接在 IB 剩余半字之后；IB 剩余 ≤ 1 个半字（新字只半个有效时 ≤ 2）才收   L634-641",
  "元数据只在被译码时才生效：带错误的字如果被跳转冲掉，就当没发生过   L145",
 ]),
 ("⑤  IB 与 CIR：半字粒度的指令缓冲", [
  "IB = 3 个半字槽；FIFO 按字、IB 按半字，因为指令可以是 16 或 32 bit，而且可以不按字对齐",
  "X 每拍回送 cir_use = 本拍用掉的半字数 0 / 1 / 2（stall 时为 0）→ 同拍移位，再叠加新字   decode.v:142   L625",
  "next_instr = 移位 + 叠加后的槽 0、1，同拍送去预译码和解压，末沿锁进 CIR   L701 L874",
  "CIR = 槽 0、1 的解压版，和 buf_contents 同一个沿更新；cir_vld = min(buf_level, 2)   L661",
  "例   内存 [c.addi | lw 低半] [lw 高半 | c.mv]：CIR=c.addi → use=1 → CIR=lw（跨字）→ use=2 → CIR=c.mv",
  "最长同拍路径   hready → X stall → cir_use → 移位 → 叠加 → next_instr → 预译码 → 寄存器堆读地址；接口注释允许 cir_use 依赖 hready   L54",
 ]),
 ("⑥  预译码、解压与 uop", [
  "预译码在 F 里提前从 next_instr 抽出 rs1 / rs2：coarse 直接作寄存器堆读地址，fine 给 bypass 选择；都不够准，不能用来判断 stall   L85-93",
  "解压 hazard3_instr_decompress：16 bit → 32 bit，CIR 存的是解压后的指令；非法压缩码置 cir_invalid_16bit",
  "Zcmp push / pop：一条指令拆成多个 uop，计数器在解压模块里；X 用 uop_stall 让它停、uop_clear 中止   L838-869",
  "uop 标志 nonfinal / no_pc_update / atomic 告诉 X：PC 何时前进，以及中间态不允许被中断打断",
  "不开 C 扩展时没有解压，CIR 直接是 IB 槽 0、1（L810）；IB 槽 2 和对齐逻辑都被常量折叠掉",
 ]),
]
y = BY + BH + 180
for rw in (0, 1):
    y += 20 + max(callout(20 + c * (CW + 20), y, *C[rw * 3 + c]) for c in range(3))

def table(x, y, w, h, title, rows):
    box(None, x, y, w, h, title, size=10, stroke=GREY, dashed=True, top=True)
    yy = y + 32
    for r in rows:
        hh = rowh(r, w - 28)
        box(None, x + 14, yy, w - 28, hh, r)
        yy += hh + 4
TH = 200
table(20, y, CW, TH, "时序对照      依据 doc/sections/instruction_timings.adoc（总线无等待）", [
    "顺序 32 bit 指令   每拍 1 条（FIFO 旁路：拍 n 发地址 → 拍 n+2 X 执行）",
    "jal / jalr   2 拍          taken 条件分支   2 拍          BTB 预测对   1 拍          预测错   2 拍",
    "跳到不按字对齐的 32 bit 指令   再 +1 拍（要取两个字）",
    "总线等待 n 拍   取指晚 n 拍；FIFO / IB 里已有的指令可以掩盖一部分",
    "load-use 等停顿发生在 X / M，F 只看到 cir_use=0，FIFO 被填满后停发",
])
table(20 + CW + 20, y, CW, TH, "与 curryGPU ifetch_top 对照", [
    "fetch_addr_q   ↔   ifetch_frontend 的 fetch_pc_q（每 warp 一个）",
    "I 侧 AHB + 存储   ↔   ifetch_l0i / ifetch_l1i",
    "FIFO + IB 3 槽   ↔   ifetch_ib（8 条 / warp）          CIR   ↔   IB 队头（decode 读的那条）",
    "cir_use   ↔   decode 的弹出（issue_valid）          jump   ↔   redirect",
    "ctr_flush_pending   ↔   epoch_q：Hazard3 单线程、按序返回，数在途个数即可；curryGPU 多 warp、可能乱序，用 epoch 判过期",
])
lx = 20 + 2 * (CW + 20)
box(None, lx, y, CW, TH, "图例   provenance", size=10, stroke=GREY, dashed=True, top=True)
leg = [
    ("box", "#000000", 1, False, "黑色细框  =  RTL 已有，结构照搬（本图全部是）"),
    ("box", "#000000", 2, False, "黑色粗框  =  一个子功能的分组，编号对应下方说明"),
    ("box", GREY, 1.5, True, "灰色虚线框  =  可选，由配置参数决定是否存在"),
    ("line", BLUE, 2, False, "蓝色粗箭头  =  同拍组合（读本拍的值）"),
    ("line", "#888888", 1, True, "灰色虚箭头  =  寄存器输出（上一拍的值）"),
]
for i, (k, c, sw, d, s) in enumerate(leg):
    yy = y + 32 + i * 22
    if k == "box":
        box(None, lx + 16, yy, 30, 14, "", stroke=c, sw=sw, dashed=d)
    else:
        cells.append(f'<mxCell id="{nid("l")}" value="" style="endArrow=block;endSize=4;html=1;strokeColor={c};strokeWidth={sw};' + ("dashed=1;dashPattern=6 4;" if d else "") + f'" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{lx + 14}" y="{yy + 7}" as="sourcePoint"/><mxPoint x="{lx + 48}" y="{yy + 7}" as="targetPoint"/></mxGeometry></mxCell>')
    text(lx + 56, yy - 1, CW - 70, 16, s)
text(lx + 16, y + 148, CW - 30, 14, "依据   Hazard3/hdl/hazard3_{frontend,core,decode,instr_decompress,cpu_2port}.v   v1.1.1")
text(lx + 16, y + 164, CW - 30, 14, "          doc/sections/{introduction,instruction_timings}.adoc      官方总图 https://wren.wtf/hazard3/doc/#_pipeline_stages")
text(lx + 16, y + 180, CW - 30, 14, "          画法参照 curryGPU docs/design/uarch/ifetch_top.drawio")

page_h = int(y + TH + 30)
xml = ('<mxfile host="app.diagrams.net"><diagram name="hazard3_frontend"><mxGraphModel dx="1800" dy="1000" grid="1" gridSize="10" '
       f'page="1" pageWidth="2620" pageHeight="{page_h}" math="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
       + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>\n')
open(sys.argv[1], "w").write(xml)
