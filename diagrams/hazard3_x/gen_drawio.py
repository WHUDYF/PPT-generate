"""Hazard3 X stage: decode + operands + execute + decide, all in one cycle.

Same style as ../hazard3_frontend/gen_drawio.py (curryGPU subcore target-pipeline look),
with boxes coloured by path: instruction path, data path, and their crossing points.
"""
import html, math, sys

cells = []
n = [0]
def nid(p="c"):
    n[0] += 1
    return f"{p}{n[0]}"
def h(s): return html.escape(s, quote=False).replace("\n", "<br>")
def attr(s): return html.escape(s, quote=True)

INK, MUTED, REF = "#1F2933", "#444444", "#9AA5B1"
BLUE = ("#DAE8FC", "#6C8EBF")      # instruction path
ORANGE = ("#FFE6CC", "#D79B00")    # data path
RED = ("#F8CECC", "#B85450")       # crossing / decision
PURPLE = ("#E1D5E7", "#9673A6")    # multi-cycle unit
GREEN = ("#D5E8D4", "#82B366")     # storage side
YELLOW = ("#FFF2CC", "#D6B656")    # owns
GREYC = ("#F5F5F5", "#999999")
BROWN = "#9C6500"

def vertex(id, x, y, w, hgt, value, style):
    cells.append(f'<mxCell id="{id or nid()}" value="{attr(value)}" style="{style}" vertex="1" parent="1">'
                 f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{hgt}" as="geometry"/></mxCell>')
def text(x, y, w, hgt, v, size=11, color=INK, bold=False, align="left", valign="middle", raw=False):
    st = f"text;html=1;align={align};verticalAlign={valign};whiteSpace=wrap;fontSize={size};fontColor={color};" + ("fontStyle=1;" if bold else "")
    vertex(None, x, y, w, hgt, v if raw else h(v), st)
def rect(id, x, y, w, hgt, fill="none", stroke=INK, sw=1, dashed=False, rounded=0, arc=6):
    st = f"rounded={rounded};arcSize={arc};whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth={sw};" + ("dashed=1;" if dashed else "")
    vertex(id, x, y, w, hgt, "", st)
def bar(x, y, w, hgt):
    vertex(None, x, y, w, hgt, "", f"rounded=0;whiteSpace=wrap;html=1;fillColor={INK};strokeColor={INK};")

def tw(s, size):  # rough rendered width in px
    return sum(size * (1.0 if ord(c) > 0x2E80 else 0.56) for c in s)
def nlines(s, w, size):
    return sum(max(1, math.ceil(tw(l, size) / (w - 10))) for l in s.split("\n"))

def stagebox(id, x, y, w, title, sub, col, dashed=False):
    """Filled box: bold title + small normal text. Returns height."""
    hgt = 22 + nlines(sub, w, 9) * 13 + 8
    v = f"{h(title)}<br><font style='font-size:9px;font-weight:normal'>{h(sub)}</font>"
    st = f"rounded=1;arcSize=6;whiteSpace=wrap;html=1;fillColor={col[0]};strokeColor={col[1]};fontSize=11;fontStyle=1;" + ("dashed=1;" if dashed else "")
    vertex(id, x, y, w, hgt, v, st)
    return hgt

def edge(s, t, label="", color="#333333", dashed=False, ex=None, en=None, pts=None, width=1):
    st = (f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;fontSize=10;"
          f"labelBackgroundColor=#FFFFFF;strokeColor={color};fontColor={color};strokeWidth={width};" + ("dashed=1;" if dashed else ""))
    if ex: st += f"exitX={ex[0]};exitY={ex[1]};exitDx=0;exitDy=0;"
    if en: st += f"entryX={en[0]};entryY={en[1]};entryDx=0;entryDy=0;"
    g = '<mxGeometry relative="1" as="geometry">'
    if pts: g += '<Array as="points">' + "".join(f'<mxPoint x="{a}" y="{b}"/>' for a, b in pts) + '</Array>'
    cells.append(f'<mxCell id="{nid("e")}" value="{attr(h(label))}" style="{st}" edge="1" parent="1" source="{s}" target="{t}">{g}</mxGeometry></mxCell>')
def line(x0, y0, x1, y1, color):
    st = f"html=1;strokeColor={color};strokeWidth=1.5;dashed=1;endArrow=block;endFill=1;"
    cells.append(f'<mxCell id="{nid("l")}" value="" style="{st}" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                 f'<mxPoint x="{x0}" y="{y0}" as="sourcePoint"/><mxPoint x="{x1}" y="{y1}" as="targetPoint"/></mxGeometry></mxCell>')

W = 2160

# ---------------- title ----------------
text(20, 8, 1800, 30, "Hazard3 X 级：一拍里完成 译码 → 取操作数 → 执行 → 决策（hazard3_decode + hazard3_core）", 18, bold=True)
text(20, 40, 2100, 20, "Hazard3 v1.1.1（8af9929）· 以 RV32IMC、2port 为例 · 蓝 = 指令通路，橙 = 数据通路，红 = 两者的交叉点（C1–C6）· 下方卡片里灰色小字是源码位置", 11, MUTED)

# ---------------- columns ----------------
FX, FW = 30, 200          # F, collapsed
XX0, XX1 = 270, 1890      # X, expanded
MX, MW = 1930, 200        # M, collapsed
HY, HH = 140, 40
CY, CH = 196, 560
CW = 380
CXS = [XX0 + i * 413 for i in range(4)]
OWN_Y = CY + CH - 100

# storage-side interface (data bus)
vertex("ahb", CXS[3], 72, MX + MW - CXS[3], 50,
       f"存储侧接口 · D 侧 AHB5 → 数据存储<br><font style='font-size:9px;font-weight:normal'>"
       f"{h('地址相位 HADDR / HWRITE / HSIZE ← X3（load / store 地址）      数据相位 HRDATA / HREADY / HRESP → M')}</font>",
       f"rounded=1;arcSize=12;whiteSpace=wrap;html=1;fillColor={GREEN[0]};strokeColor={GREEN[1]};fontSize=12;fontStyle=1;")

def header(x, w, title, sub):
    vertex(None, x, HY, w, HH, f"{h(title)}<br><font style='font-size:9px;font-weight:normal'>{h(sub)}</font>",
           "rounded=0;whiteSpace=wrap;html=1;fillColor=#EEEEEE;strokeColor=#666666;fontSize=12;fontStyle=1;")
header(FX, FW, "F · 取指", "只画与 X 相关的部分")
header(XX0, XX1 - XX0, "X · 译码 + 执行   hazard3_decode + hazard3_core",
       "一个大流水级，只占一拍：X0 → X3 是同一拍里的四步组合逻辑；只有乘除法 / AMO 会让 X 原地停住多拍")
header(MX, MW, "M · 访存 + 写回", "只画与 X 相关的部分")

bar(FX + FW + 16, HY, 8, CY + CH - HY)       # F|X : CIR / RF rdata / bypass select
bar(XX1 + 16, HY, 8, CY + CH - HY)           # X|M : xm_* / data address phase

vertex(None, CXS[0] - 12, CY - 8, XX1 - CXS[0] + 20, CH + 16,
       "同一拍：X0 → X3 组合完成，末沿锁存 xm_*；数据总线地址相位在这一拍发出",
       "rounded=1;arcSize=2;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#999999;dashed=1;strokeWidth=1;"
       "verticalAlign=bottom;align=center;spacingBottom=-16;fontSize=10;fontColor=#777777;")

def container(x, col, title, sub):
    rect(None, x, CY, CW, CH, stroke=col[1], sw=1.5, dashed=True, rounded=1, arc=3)
    text(x, CY + 6, CW, 18, title, 12, col[1], bold=True, align="center")
    text(x, CY + 24, CW, 16, sub, 10, "#555555", align="center")

def owns(x, w, sub):
    vertex(None, x + 14, OWN_Y, w - 28, 88,
           f"owns<br><font style='font-size:9px;font-weight:normal'>{h(sub)}</font>",
           f"rounded=0;whiteSpace=wrap;html=1;fillColor={YELLOW[0]};strokeColor={YELLOW[1]};fontSize=11;fontStyle=1;")

def stack(x, w, items, y0=CY + 50, gap=22):
    """items: (id, title, sub, colour[, dashed])"""
    y = y0
    for it in items:
        y += stagebox(it[0], x + 14, y, w - 28, it[1], it[2], it[3], dashed=len(it) > 4 and it[4]) + gap

# X0 decode (instruction path)
container(CXS[0], BLUE, "X0 · 译码", "指令通路 · decode.v")
stack(CXS[0], CW, [
    ("x0_cir", "读 CIR", "展开好的 32 bit 指令 + cir_vld\nCIR 空或只有半条 → starved，本拍是气泡", BLUE),
    ("x0_dec", "主译码 case(opcode)", "→ aluop · 操作数来源 alusrc_a / b · 立即数\n→ memop · branchcond · rs1 / rs2 / rd · csr · 异常", BLUE),
    ("x0_gate", "门控", "starved / 非法指令 / 取指错误 / CIR lock\n→ 清掉 rd、memop、branchcond，或换成异常", BLUE),
    ("x0_pc", "PC 与 cir_use", "不停时 PC +2 / +4（预测分支时换成 BTB 目标）\ncir_use 同拍回送 F：用掉 0 / 1 / 2 个半字", BLUE),
])
owns(CXS[0], CW, "pc（当前指令地址）· cir_lock_prev\nlspair_phase（Zilsd，可选）")

# X1 operands (data path)
container(CXS[1], ORANGE, "X1 · 取操作数", "数据通路 · core.v:494-580")
stack(CXS[1], CW, [
    ("x1_rf", "RF 读数据 rdata1 / rdata2", "读地址在 F 那一拍由预译码给出，沿后读出\nX 停住时改用 d_rs1 / d_rs2 重读", ORANGE),
    ("x1_byp", "bypass 三选一", "xm_result（M 级的结果）/ mw_result（上拍写回）/ rdata\n选择信号上一拍就比好了，不在关键路径上", ORANGE),
    ("x1_mux", "操作数选择", "op_a = rs1 或 PC\nop_b = rs2 或 立即数", ORANGE),
])
owns(CXS[1], CW, "x_rs1/rs2_select_regs_xm_mw（bypass 选择）\nd_rs1/rs2_predecoded")

# X2 execute (data path, parallel units)
container(CXS[2], ORANGE, "X2 · 执行", "数据通路 · 几个单元同一拍并行")
stack(CXS[2], CW, [
    ("x2_alu", "ALU", "加减 · 逻辑 · 移位 · 比较 · Zba / Zbb / Zbs\njal / jalr：算链接地址 PC+2/4；store：透传 rs2", ORANGE),
    ("x2_addr", "地址加法器 x_addr_sum", "(rs1 或 PC) + 偏移\n→ load / store 地址，以及跳转 / 分支目标", ORANGE),
    ("x2_cmp", "分支比较", "FAST_BRANCHCMP=1：独立比较器\n否则用 ALU 的比较结果", ORANGE),
    ("x2_md", "乘除法（多拍）", "顺序电路逐位迭代，div 约 18 拍\n没算完 → X 停住；MUL_FAST 时 mul 1 拍", PURPLE),
    ("x2_csr", "CSR 读写", "在 X 里读写 CSR 文件\n写 PMP / 触发器等 → 要求重新取指", ORANGE),
], gap=14)
owns(CXS[2], CW, "CSR 文件（hazard3_csr）\n乘除法内部状态 · x_muldiv_posted")

# X3 decide (crossings)
container(CXS[3], RED, "X3 · 决策与出口", "指令 ↔ 数据交叉 · core.v:409-490, 905-950, 1113")
stack(CXS[3], CW, [
    ("x3_stall", "停顿 x_stall", "M 停 · trap · load-use · 乘除法 · AMO · fence\n· 数据地址未被接收 · 跳转未就绪 · 独占冲突", RED),
    ("x3_jump", "跳转请求 → F", "jal / jalr / taken 分支（不依赖未回来的 load）\n目标 = x_addr_sum，同拍送进 F0", RED),
    ("x3_bus", "访存地址相位 → 数据总线", "load / store 地址 = x_addr_sum\n不对齐 / PMP 失败 → 不发，改报异常", GREEN),
    ("x3_exc", "异常 x_except", "断点 > 跳转不对齐 > CSR 非法 > 访存不对齐\n> PMP > 重新取指 > 译码异常；在 M 才进 trap", RED),
    ("x3_res", "结果选择 → xm_result", "CSR 读值 > AMO > 快速乘 > 乘除法 > ALU", ORANGE),
], gap=14)
owns(CXS[3], CW, "x_amo_phase（AMO 状态机，可选）\nprev_instr_was_32_bit")

# F and M (collapsed)
rect(None, FX, CY, FW, CH, stroke="#999999", sw=1.5, dashed=True, rounded=1, arc=3)
rect(None, MX, CY, MW, CH, stroke="#999999", sw=1.5, dashed=True, rounded=1, arc=3)
stack(FX, FW, [
    ("f_cir", "IB / CIR", "展开好的指令", GREYC),
    ("f_pre", "预译码 rs1 / rs2", "→ RF 读地址", GREYC),
], y0=CY + 20, gap=30)
y_rf = CY + 170
stagebox("rf", FX + 14, y_rf, FW - 28, "寄存器堆 RF", "同步读：F 给地址，X 拿数据\nM 写回", GREEN)
stagebox("f_f0", FX + 14, CY + 300, FW - 28, "F0 地址选择", "接收 jump", GREYC)
stack(MX, MW, [
    ("m_dph", "数据相位", "load 数据回来\nhready=0 → m_stall", GREYC),
    ("m_trap", "trap 进入", "→ jump，优先于 X", GREYC),
    ("m_wb", "写回", "mw_rd / mw_result\n→ RF，也给 bypass", GREYC),
], y0=CY + 20, gap=30)

# ---------------- edges ----------------
edge("f_cir", "x0_cir", "CIR", ex=(1, 0.5), en=(0, 0.5))
edge("f_pre", "rf", "", ex=(0.5, 1), en=(0.5, 0))
edge("rf", "x1_rf", "rdata", ORANGE[1], ex=(1, 0.5), en=(0, 0.5), pts=[(FX + FW + 10, y_rf + 30), (FX + FW + 10, CY + CH - 6), (CXS[1] - 6, CY + CH - 6)])
edge("x0_cir", "x0_dec", "", BLUE[1], ex=(0.5, 1), en=(0.5, 0))
edge("x0_dec", "x0_gate", "", BLUE[1], ex=(0.5, 1), en=(0.5, 0))
edge("x0_gate", "x0_pc", "", BLUE[1], ex=(0.5, 1), en=(0.5, 0))
edge("x0_dec", "x1_mux", "alusrc · 立即数", BLUE[1], ex=(1, 0.75), en=(0, 0.5))
edge("x1_rf", "x1_byp", "", ORANGE[1], ex=(0.5, 1), en=(0.5, 0))
edge("x1_byp", "x1_mux", "", ORANGE[1], ex=(0.5, 1), en=(0.5, 0))
edge("x1_mux", "x2_alu", "op_a / op_b", ORANGE[1], ex=(1, 0.3), en=(0, 0.5))
edge("x1_byp", "x2_addr", "", ORANGE[1], ex=(1, 0.6), en=(0, 0.5))
edge("x1_byp", "x2_cmp", "", ORANGE[1], ex=(1, 0.85), en=(0, 0.5))
edge("x2_cmp", "x3_jump", "C2 比较结果", RED[1], ex=(1, 0.5), en=(0, 0.6), width=2)
edge("x2_addr", "x3_jump", "", ORANGE[1], ex=(1, 0.3), en=(0, 0.3))
edge("x2_addr", "x3_bus", "", ORANGE[1], ex=(1, 0.7), en=(0, 0.5))
edge("x2_alu", "x3_res", "", ORANGE[1], ex=(1, 0.5), en=(0.5, 1))
edge("x3_bus", "ahb", "", GREEN[1], ex=(1, 0.3), en=((XX1 + 7 - CXS[3]) / (MX + MW - CXS[3]), 1))
edge("ahb", "m_dph", "", GREEN[1], ex=(0.85, 1), en=(0.5, 0))
edge("x3_res", "m_wb", "xm_result", ORANGE[1], ex=(1, 0.5), en=(0, 0.5))

# boundary labels
LY = CY + CH + 22
def blabel(cx, title, sub):
    text(cx - 110, LY, 220, 34, f"<b>▲ {h(title)}</b><br><font style='font-size:9px;font-weight:normal'>{h(sub)}</font>", 10, raw=True, align="center")
blabel(FX + FW + 20, "F | X", "CIR · RF 读数据 · bypass 选择")
blabel(XX1 + 20, "X | M", "xm_rd · xm_result · xm_memop · xm_except")

# ---------------- flow control ----------------
FY = LY + 50
text(30, FY, 300, 18, "握手 / 流控", 11, bold=True)
def band(x, w, col, s):
    vertex(None, x, FY + 22, w, 38, h(s), f"rounded=1;arcSize=20;whiteSpace=wrap;html=1;fillColor={col[0]};strokeColor={col[1]};fontSize=11;fontStyle=1;")
band(30, 640, BLUE, "F → X · CIR + cir_vld；X 用 cir_use 当拍回送（starved / 停住时为 0）")
band(690, 760, RED, "X → M · 没有握手：M 停则 X 必停；X 停则向 M 插气泡（xm_rd=0、memop=NONE）")
band(1470, 660, GREEN, "X ↔ 数据总线 · 地址 vld / rdy；没被接收 → X 停")

# ---------------- event channels ----------------
EY = FY + 80
text(30, EY, 1600, 20, "跨级事件通道   同拍 = 组合，当拍生效      reg = 来自寄存器，下一拍生效", 11, bold=True)
CENT = {"F": FX + FW / 2, "X0": CXS[0] + CW / 2, "X1": CXS[1] + CW / 2, "X2": CXS[2] + CW / 2, "X3": CXS[3] + CW / 2, "M": MX + MW / 2}
def channel(row, src, dsts, color, tag, name, desc):
    y = EY + 46 + row * 38
    xs = [CENT[d] for d in dsts]
    sx = CENT[src]
    left = min(xs) < sx
    far = min(xs) if left else max(xs)
    lw = tw(name + "   " + desc, 10) + 30
    if lw < abs(sx - far) - 40:
        text(min(sx, far) + 20, y - 19, lw, 16, f"<b>{h(name)}</b>   {h(desc)}", 10, color, raw=True)
    elif far - 14 - lw > 20:
        text(far - 14 - lw, y - 8, lw, 16, f"<b>{h(name)}</b>   {h(desc)}", 10, color, raw=True, align="right")
    else:
        text(max(sx, far) + 24, y - 8, lw, 16, f"<b>{h(name)}</b>   {h(desc)}", 10, color, raw=True)
    line(sx - 16 if left else sx + 16, y, far + 4 if left else far - 4, y, color)
    for d in xs:
        vertex(None, d - 3, y - 3, 6, 6, "", f"ellipse;whiteSpace=wrap;html=1;fillColor={color};strokeColor={color};")
    vertex(None, sx - 16, y - 9, 32, 18, tag, f"rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor={color};fontSize=9;fontStyle=1;fontColor={color};")
channel(0, "X3", ["F"], RED[1], "同拍", "jump_target / jump_now", "X3 → F0 换地址、清 FIFO / IB（M 的 trap 也走这条，且优先）      ④")
channel(1, "X0", ["F"], ORANGE[1], "同拍", "cir_use / cir_flush_behind", "X0 → F · 本拍用掉几个半字")
channel(2, "M", ["X1"], BROWN, "reg", "xm_result / mw_result", "M → X1 · 还没写回 RF 的新结果，bypass 用      ②")
channel(3, "M", ["X3"], PURPLE[1], "同拍", "m_stall / m_trap_enter", "M → X3 · 数据总线等待、trap 进入 → X 停住      ⑤")
channel(4, "M", ["F"], GREEN[1], "reg", "写回 mw_rd / mw_result → RF", "M → RF · 下一拍起 RF 读出新值（同拍写读不旁路，靠 mw_result 补）")
channel(5, "F", ["X3"], BLUE[1], "reg", "jump_target_rdy = !mem_addr_hold", "F → X3 · 取指总线正保持地址时不能跳转，X 停一拍")

# ---------------- cards ----------------
KY = EY + 46 + 6 * 38 + 20
text(30, KY, 1400, 26, "各部分怎么工作", 15, bold=True)
KW = 680
KX = [30, 30 + KW + 35, 30 + 2 * (KW + 35)]

def card(x, y, color, title, bullets, dashed=False):
    yy = y + 40
    items = []
    for b in bullets:
        s, ref = b if isinstance(b, tuple) else (b, "")
        hh = nlines(s + "   " + ref, KW - 40, 11) * 17 + 4
        items.append((yy, hh, s, ref)); yy += hh + 6
    total = yy - y + 8
    rect(None, x, y, KW, total, stroke=color, sw=2, rounded=1, arc=2, dashed=dashed)
    text(x + 16, y + 8, KW - 32, 24, title, 13, color, bold=True)
    for (iy, hh, s, ref) in items:
        v = f"• {h(s)}" + (f"&nbsp;&nbsp;&nbsp;<font color='{REF}' style='font-size:10px'>{h(ref)}</font>" if ref else "")
        text(x + 18, iy, KW - 36, hh, v, 11, MUTED, raw=True, valign="top")
    return total

CARDS = [
 (BLUE[1], "①  X0 译码：把 CIR 变成控制信号", [
  ("主译码是一个 case(opcode)：每条指令定下 aluop、两个操作数来源、立即数、访存类型、分支条件、rs1 / rs2 / rd", "decode.v:376"),
  ("例 add x3,x1,x2 → aluop=ADD，op_a=rs1，op_b=rs2      例 lw x5,8(x2) → memop=LW，地址 = rs1 + 8", ""),
  ("例 sw → aluop=RS2：ALU 只把 rs2（要存的数据）透传到结果，rd=0", "decode.v:414"),
  ("例 beq → aluop=SUB、rd=0、branchcond=ZERO：相减为 0 才跳      例 jal → ALU 算链接地址 PC+4，目标另由地址加法器算", "decode.v:377 385"),
  ("门控：CIR 空（starved）、非法指令、取指错误时，把 rd / memop / branchcond 清掉变成气泡，或换成异常", "decode.v:558"),
  ("PC 在这里：不停时 +2 / +4，预测分支时换成 BTB 目标；发生跳转时由 F 的 jump 写入", "decode.v:224"),
 ]),
 (ORANGE[1], "②  X1 取操作数：RF + bypass", [
  ("RF 是同步读：地址在 F 那一拍由预译码给出，X 一开始 rdata 就已经读出来了", "core.v:1572"),
  ("rdata 可能是旧值：更新的结果还在 M（xm_result），或上一拍刚写回（mw_result），所以三选一", "core.v:574"),
  ("选择信号是寄存器：上一拍就用预译码的寄存器号和 xm_rd / mw_rd 比好，这拍直接用", "core.v:536"),
  ("例 add x1,… ; add x2,x1,… → 第二条在 X 时第一条在 M，直接选 xm_result，不停", ""),
  ("例 lw x1,… ; add x2,x1,… → lw 的数据 M 末尾才有，X 停 1 拍（load-use），之后从 mw_result 取", "core.v:464"),
  ("最后 op_a 在 rs1 / PC 中选，op_b 在 rs2 / 立即数中选", "core.v:589"),
 ]),
 (ORANGE[1], "③  X2 执行：几个单元同一拍并行", [
  ("ALU：加减、逻辑、移位、比较，以及 Zba / Zbb / Zbs 等位操作", "arith/hazard3_alu.v"),
  ("地址加法器单独一个：(rs1 或 PC) + 偏移；jal 同一拍既要链接地址（ALU）又要目标（加法器），所以要两个", "core.v:754"),
  ("分支比较：FAST_BRANCHCMP=1 时用独立比较器，比经过 ALU 快", "core.v:916"),
  ("乘除法：顺序电路逐位迭代，div 约 18 拍；期间 X 停住，向 M 送气泡；MUL_FAST 时 mul 只要 1 拍", "core.v:837"),
  ("CSR：在 X 里读写；读值作为结果；写 PMP / 触发器等会要求重新取指（REFETCH）", "core.v:1154"),
  ("结果选择：CSR 读值 > AMO > 快速乘 > 乘除法 > ALU → 末沿锁进 xm_result", "core.v:1359"),
 ]),
 (RED[1], "④  X3 跳转、访存与异常：决定指令流去哪", [
  ("跳转条件：jal / jalr 总是跳；条件分支看比较结果；比较依赖还没回来的 load 时先不跳（停住）", "core.v:935"),
  ("目标 = x_addr_sum 去掉最低位，同拍送进 F0 作为取指地址", "core.v:908"),
  ("BTB：taken 的后向分支写入；预测过的分支比较结果取反，只有预测错才发跳转", "core.v:912-950"),
  ("X 停住时也可能发出跳转（停顿依赖 hready，挡不住）→ CIR lock：F 保留当前指令，解除后再补写链接寄存器", "decode.v:146"),
  ("load / store 的地址相位在 X 发出，相当于数据侧的「F0」；不对齐或 PMP 失败时不发，改报异常", "core.v:779"),
  ("异常在 X 判出，随 xm_except 进 M，在 M 才真正进入 trap", "core.v:1113"),
 ]),
 (RED[1], "⑤  X3 停顿 x_stall：X 为什么走不动", [
  ("9 个来源：M 停（数据总线等待 / trap 未被 F 接受 / wfi）· trap 即将进入 · load-use 冲突 · 乘除法没算完 · AMO 多阶段 · fence 等排空 · 数据地址没被接收 · 跳转但 F 未就绪 · lr / sc 独占冲突", "core.v:476"),
  ("停住时：cir_use=0，PC 不变，RF 改为重读当前指令的寄存器，M 收到气泡（xm_rd=0、memop=NONE）", "core.v:1281"),
  ("M 停时 X 一定停；X 停时 M 可以继续，中断就插在 X 与 M 之间进入", "core.v:412"),
  ("停顿条件依赖 hready，所以 x_stall → cir_use → F 的移位是整个核最长的同拍路径之一", ""),
 ]),
 (RED[1], "⑥  指令通路 ↔ 数据通路：交叉点", [
  "C1 寻址（指令 → 数据）：寄存器号决定 RF 读地址和 bypass 选择；F 预译码给出，X 停住时由 X 重给",
  "C2 改道（数据 → 指令）：比较结果、jalr 的寄存器值 → 跳转，同拍送进 F",
  "C3 同步（数据 → 指令）：load 数据还没回来 → x_stall → cir_use=0，指令流停住",
  "C4 异常（数据 → 指令）：地址不对齐、PMP 失败 → 异常 → M 进入 trap，指令流改道",
  "C5 CSR（数据 → 指令）：写某些 CSR 要求重新取指（REFETCH）",
  "C6 控制（指令 → 数据）：aluop / alusrc / 立即数 / memop 决定数据通路怎么算；数量最多，但时序最简单",
 ]),
]
y = KY + 36
for r in range(2):
    y += 24 + max(card(KX[c], y, *CARDS[r * 3 + c]) for c in range(3))

G = "#9AA5B1"
hb = [
    card(KX[0], y, G, "时序对照（官方文档，总线无等待）", [
        "ALU 指令 1 拍；csr 读写 1 拍（写 PMP 等要重新取指，3 拍）",
        "load 1 拍；紧接着的指令依赖它时 2 拍（load-use）",
        "mul / mulh 1 拍（MUL_FAST）；div / rem 18~19 拍（MULDIV_UNROLL=2）",
        "jal / jalr / taken 分支 2 拍；ecall / ebreak 3 拍（跳到 mtvec）",
        ("依据", "doc/sections/instruction_timings.adoc"),
    ], dashed=True),
    card(KX[1], y, G, "与 F 级对照", [
        "F0 发取指地址 ↔ X3 发访存地址：都是 AHB 地址相位，数据在下一级（F1 / M）收",
        "F 被 X 节流（cir_use）↔ X 被 M 节流（m_stall）",
        "F 的 owns 主要是队列（FIFO、IB）；X 的 owns 主要是 PC 和多拍单元的状态",
        "两者都是「一拍内若干步组合」：F1 → F4、X0 → X3 都没有中间时钟沿",
    ], dashed=True),
]
LH = max(hb)
rect(None, KX[2], y, KW, LH, stroke=G, sw=2, rounded=1, arc=2, dashed=True)
text(KX[2] + 16, y + 8, KW - 32, 24, "图例", 13, G, bold=True)
for i, (col, s) in enumerate([
        (BLUE, "蓝色 = 指令通路（译码、PC）"),
        (ORANGE, "橙色 = 数据通路（操作数、执行）"),
        (RED, "红色 = 交叉点 / 决策（停顿、跳转、异常）"),
        (PURPLE, "紫色 = 多拍单元（乘除法）"),
        (GREEN, "绿色 = 存储侧（数据总线、寄存器堆）")]):
    yy = y + 42 + i * 24
    vertex(None, KX[2] + 20, yy, 34, 16, "", f"rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor={col[0]};strokeColor={col[1]};")
    text(KX[2] + 64, yy - 2, 300, 20, s, 11, MUTED)
for i, s in enumerate(["黑粗杠 = 时钟沿（级间寄存器）", "灰色虚线框 = 同一拍内组合完成", "黄色 owns = 这一步拥有的寄存器"]):
    yy = y + 42 + i * 24
    if i == 0:
        bar(KX[2] + 380, yy + 6, 34, 4)
    elif i == 1:
        rect(None, KX[2] + 380, yy, 34, 16, stroke="#999999", dashed=True, rounded=1, arc=10)
    else:
        vertex(None, KX[2] + 380, yy, 34, 16, "", f"rounded=0;whiteSpace=wrap;html=1;fillColor={YELLOW[0]};strokeColor={YELLOW[1]};")
    text(KX[2] + 424, yy - 2, 250, 20, s, 11, MUTED)
y += LH + 30

xml = ('<mxfile host="app.diagrams.net"><diagram name="hazard3_x"><mxGraphModel dx="1800" dy="1000" grid="1" gridSize="10" '
       f'page="1" pageWidth="{W}" pageHeight="{int(y)}" math="0" background="#FFFFFF"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
       + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>\n')
open(sys.argv[1], "w").write(xml)
