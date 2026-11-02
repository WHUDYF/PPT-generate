"""Hazard3 F stage as a big pipeline stage with five sub-stages.

Style follows projects/currygpu_subcore_ppt169_20261004/sources/11-target-pipeline.drawio
(grey stage headers, dashed coloured containers, filled sub-stage boxes, dark bars = clock edges,
"owns" boxes, coloured backward event channels, rule cards).
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
BLUE = ("#DAE8FC", "#6C8EBF")
GREEN = ("#D5E8D4", "#82B366")
PURPLE = ("#E1D5E7", "#9673A6")
YELLOW = ("#FFF2CC", "#D6B656")
GREYC = ("#F5F5F5", "#999999")
RED, ORANGE = "#B85450", "#D79B00"

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
    """Filled sub-stage box: bold title + small normal text. Returns height."""
    hgt = 22 + nlines(sub, w, 9) * 13 + 8
    v = f"{h(title)}<br><font style='font-size:9px;font-weight:normal'>{h(sub)}</font>"
    st = f"rounded=1;arcSize=6;whiteSpace=wrap;html=1;fillColor={col[0]};strokeColor={col[1]};fontSize=11;fontStyle=1;" + ("dashed=1;" if dashed else "")
    vertex(id, x, y, w, hgt, v, st)
    return hgt

def edge(s, t, label="", color="#333333", dashed=False, ex=None, en=None, pts=None):
    st = (f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;fontSize=10;"
          f"labelBackgroundColor=#FFFFFF;strokeColor={color};fontColor={color};" + ("dashed=1;" if dashed else ""))
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
text(20, 8, 1800, 30, "Hazard3 F 级：一个大流水级套 5 个小级（hazard3_frontend）", 18, bold=True)
text(20, 40, 2100, 20, "Hazard3 v1.1.1（8af9929）· 以 RV32IMC、2port 为例 · 虚线框 = 可选（由配置参数决定）· 下方卡片里灰色小字是 hazard3_frontend.v 行号", 11, MUTED)

# ---------------- storage-side interface ----------------
vertex("ahb", 30, 72, 620, 50,
       f"存储侧接口 · I 侧 AHB5 → 存储（以后可以换成 I-cache）<br><font style='font-size:9px;font-weight:normal'>"
       f"{h('地址相位 HADDR / HTRANS ← F0      数据相位 HRDATA / HREADY / HRESP → F1      hazard3_cpu_2port.v:208')}</font>",
       f"rounded=1;arcSize=12;whiteSpace=wrap;html=1;fillColor={GREEN[0]};strokeColor={GREEN[1]};fontSize=12;fontStyle=1;")

# ---------------- stage headers ----------------
HY, HH = 140, 40
def header(x, w, title, sub):
    vertex(None, x, HY, w, HH, f"{h(title)}<br><font style='font-size:9px;font-weight:normal'>{h(sub)}</font>",
           "rounded=0;whiteSpace=wrap;html=1;fillColor=#EEEEEE;strokeColor=#666666;fontSize=12;fontStyle=1;")
FX0, FX1 = 30, 1640
XX, XW = 1680, 220
MX, MW = 1940, 190
header(FX0, FX1 - FX0, "F · 取指   hazard3_frontend", "一个大流水级：内部 5 个小级，其中 F0 → F1 隔一个时钟沿，F1 → F4 在同一拍里组合完成")
header(XX, XW, "X · 译码 + 执行", "这里只画与 F 相关的部分")
header(MX, MW, "M · 访存 + 写回", "这里只画与 F 相关的部分")

CY, CH = 196, 410                       # sub-stage containers
CW = 290
CXS = [30 + i * 330 for i in range(5)]
OWN_Y = CY + CH - 100

# big-stage boundaries (F|X, X|M) and the one clock edge inside F (F0|F1)
bar(FX1 + 12, HY, 8, CY + CH - HY)
bar(XX + XW + 12, HY, 8, CY + CH - HY)
bar(CXS[0] + CW + 17, CY, 6, CH)

# "same cycle" frame around F1..F4
vertex(None, CXS[1] - 12, CY - 8, FX1 - CXS[1] + 20, CH + 16,
       "同一拍（拍 n+1）：旁路时 F1 → F4 组合完成，末沿同时锁存 IB 和 CIR",
       "rounded=1;arcSize=2;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#999999;dashed=1;strokeWidth=1;"
       "verticalAlign=bottom;align=center;spacingBottom=-16;fontSize=10;fontColor=#777777;")

def container(x, col, title, sub):
    rect(None, x, CY, CW, CH, stroke=col[1], sw=1.5, dashed=True, rounded=1, arc=3)
    text(x, CY + 6, CW, 18, title, 12, col[1], bold=True, align="center")
    text(x, CY + 24, CW, 16, sub, 10, "#555555", align="center")

def owns(x, sub):
    vertex(None, x + 14, OWN_Y, CW - 28, 88,
           f"owns<br><font style='font-size:9px;font-weight:normal'>{h(sub)}</font>",
           f"rounded=0;whiteSpace=wrap;html=1;fillColor={YELLOW[0]};strokeColor={YELLOW[1]};fontSize=11;fontStyle=1;")

def latch(x):  # dark bar = this column's registers are written at the clock edge
    bar(x + 60, OWN_Y - 16, CW - 120, 3)
    text(x + CW - 60, OWN_Y - 24, 60, 14, "末沿", 9, "#777777")

def stack(x, w, items, col, y0=CY + 50, gap=26):
    """items: (id, title, sub[, dashed]); returns {id: (y, h)}"""
    y, pos = y0, {}
    for it in items:
        hh = stagebox(it[0], x + 14, y, w - 28, it[1], it[2], col, dashed=len(it) > 3 and it[3])
        pos[it[0]] = (y, hh)
        y += hh + gap
    return pos

# F0
container(CXS[0], BLUE, "F0 · 发地址", "拍 n · 逻辑上和 X 同一拍")
stack(CXS[0], CW, [
    ("f0_sel", "地址选择 → 总线", "优先级  hold > jump > debug 停取 > 顺序\n总是整字对齐、32 bit"),
    ("f0_stall", "节流 fetch_stall", "FIFO 满；或 FIFO 有 1 项且还有在途；\n或在途 ≥ 2  → 本拍不发"),
    ("f0_btb", "BTB 换地址（可选）", "取到最近一次 taken 的后向分支\n→ 下一个地址直接换成目标", True),
], BLUE)
owns(CXS[0], "fetch_addr · fetch_priv\nmem_addr_hold · reset_holdoff\nBTB 1 项（可选）")
edge("f0_stall", "f0_sel", "", BLUE[1], ex=(0.5, 0), en=(0.5, 1))
edge("f0_btb", "f0_sel", "", BLUE[1], dashed=True, ex=(0.85, 0), en=(0.85, 1))

# F1
container(CXS[1], GREEN, "F1 · 收数据", "拍 n+1 · 总线数据相位")
stack(CXS[1], CW, [
    ("f1_rx", "收数据", "hready=1 时 mem_data 有效\n带上元数据：哪半有效 · 错误 · 断点"),
    ("f1_cnt", "在途计数", "pending_fetches：已发未回 0..2\nctr_flush_pending：跳转前在途的，回来就丢"),
    ("f1_steer", "数据去向", "旧请求 → 丢弃\nFIFO 空且 IB 有空位 → 旁路\n否则 → 进 FIFO"),
], GREEN)
owns(CXS[1], "pending_fetches · ctr_flush_pending\nmem_data_hwvld · predbranch\ncheck_addr（PMP / 断点，可选）")
edge("f1_rx", "f1_cnt", "", GREEN[1], ex=(0.5, 1), en=(0.5, 0))
edge("f1_cnt", "f1_steer", "", GREEN[1], ex=(0.5, 1), en=(0.5, 0))

# F2
container(CXS[2], PURPLE, "F2 · 预取 FIFO", "队列 · 空时旁路，不加延迟")
stack(CXS[2], CW, [
    ("f2_pop", "取数 / 弹出", "FIFO 空 → 直接用总线数据（旁路）\n否则取 FIFO 头；IB 有空位就弹出"),
    ("f2_push", "推入", "数据回来、但没能走旁路\n跳转时全部清空"),
], PURPLE)
latch(CXS[2])
owns(CXS[2], "fifo_mem 2 项 × 32 bit\n每项：哪半有效 · err · break · predbranch")
edge("f2_push", "f2_pop", "下一拍起", PURPLE[1], dashed=True, ex=(0.2, 0), en=(0.2, 1))

# F3
container(CXS[3], PURPLE, "F3 · 指令缓冲 IB", "队列 · 按半字存，3 个槽")
stack(CXS[3], CW, [
    ("f3_shift", "移位", "按 cir_use 去掉 X 本拍用掉的\n0 / 1 / 2 个半字"),
    ("f3_ovl", "叠加新字", "剩余 ≤ 1 个半字才收（同时让 FIFO 弹出）\n新字只有高半有效时先对齐"),
    ("f3_flush", "冲刷", "jump：清空\ncir_flush_behind：保留当前指令"),
], PURPLE)
latch(CXS[3])
owns(CXS[3], "buf_contents：3 个半字槽（含元数据）\nbuf_level 0..3")
edge("f3_shift", "f3_ovl", "", PURPLE[1], ex=(0.5, 1), en=(0.5, 0))
edge("f3_ovl", "f3_flush", "", PURPLE[1], ex=(0.5, 1), en=(0.5, 0))

# F4
container(CXS[4], BLUE, "F4 · 预译码 / 解压", "组合 · 末沿锁存成 CIR")
stack(CXS[4], CW, [
    ("f4_next", "next_instr", "叠加后的槽 0、1 = 下一拍的指令"),
    ("f4_pre", "预译码 rs1 / rs2", "→ 寄存器堆读地址、bypass 选择\n比 X 正式译码早一拍"),
    ("f4_dec", "解压 + uop", "16 bit → 32 bit\nZcmp push / pop 拆成 uop"),
], BLUE)
latch(CXS[4])
owns(CXS[4], "cir（已解压，= IB 队头）· cir_vld\ncir_is_32bit · uop 标志")
edge("f4_next", "f4_pre", "", BLUE[1], ex=(0.5, 1), en=(0.5, 0))
edge("f4_pre", "f4_dec", "", BLUE[1], ex=(0.5, 1), en=(0.5, 0))

# X and M (collapsed)
rect(None, XX, CY, XW, CH, stroke="#999999", sw=1.5, dashed=True, rounded=1, arc=3)
rect(None, MX, CY, MW, CH, stroke="#999999", sw=1.5, dashed=True, rounded=1, arc=3)
stack(XX, XW, [
    ("x_dec", "decode", "读 CIR\n算 cir_use（stall 时为 0）"),
    ("x_br", "分支 / jal / jalr", "目标在 X 算出\ntaken → jump"),
    ("x_rf", "寄存器堆 + ALU", "读地址来自 F4 预译码"),
], GREYC, y0=CY + 20)
stack(MX, MW, [
    ("m_ls", "load / store", "数据相位"),
    ("m_trap", "trap 进入", "→ jump（优先于 X）"),
    ("m_wb", "写回", "M 末尾"),
], GREYC, y0=CY + 20)

# ---------------- main forward edges ----------------
edge("f0_sel", "ahb", "mem_addr", ex=(0.5, 0), en=(0.25, 1))
edge("ahb", "f1_rx", "mem_data", ex=(0.75, 1), en=(0.5, 0))
edge("f1_steer", "f2_push", "进 FIFO", ex=(1, 0.75), en=(0, 0.5))
edge("f1_steer", "f2_pop", "旁路", ex=(1, 0.3), en=(0, 0.5))
edge("f2_pop", "f3_ovl", "fetch_data（1 个字）", ex=(1, 0.5), en=(0, 0.5))
edge("f3_ovl", "f4_next", "next_instr", ex=(1, 0.3), en=(0, 0.5))
edge("f4_dec", "x_dec", "CIR", ex=(1, 0.5), en=(0, 0.5))
edge("f4_pre", "x_rf", "rs1 / rs2", ex=(1, 0.75), en=(0, 0.5))

# boundary labels under the containers
LY = CY + CH + 14
def blabel(cx, title, sub):
    text(cx - 90, LY, 180, 34, f"<b>▲ {h(title)}</b><br><font style='font-size:9px;font-weight:normal'>{h(sub)}</font>", 10, raw=True, align="center")
blabel(CXS[0] + CW + 20, "时钟沿", "总线：地址相位 → 数据相位")
blabel(FX1 + 16, "IB + CIR", "末沿同时锁存")
blabel(XX + XW + 16, "xm_*", "X / M 级间寄存器")

# ---------------- flow control ----------------
FY = LY + 50
text(30, FY, 300, 18, "握手 / 流控", 11, bold=True)
def band(x, w, col, s):
    vertex(None, x, FY + 22, w, 38, h(s), f"rounded=1;arcSize=20;whiteSpace=wrap;html=1;fillColor={col[0]};strokeColor={col[1]};fontSize=11;fontStyle=1;")
band(30, 620, GREEN, "F0 / F1 ↔ 总线 · 地址 vld / rdy，没被接收就保持；数据无反压，所以 F0 只在放得下时才发")
band(670, 970, PURPLE, "F1 → F2 → F3 · 没有握手：去向只由「FIFO 是否空」和「IB 剩余几个半字」决定")
band(1680, 450, BLUE, "F → X · cir_vld 给出有效半字数；X 用 cir_use 当拍回送用掉多少")

# ---------------- backward event channels ----------------
EY = FY + 80
text(30, EY, 1400, 20, "反向事件通道   同拍 = 组合，当拍生效      reg = 来自寄存器，或写寄存器、下一拍生效", 11, bold=True)
CENT = {"F0": CXS[0] + CW / 2, "F1": CXS[1] + CW / 2, "F2": CXS[2] + CW / 2, "F3": CXS[3] + CW / 2, "F4": CXS[4] + CW / 2,
        "X": XX + XW / 2, "M": MX + MW / 2}
def channel(row, src, dsts, color, tag, name, desc):
    y = EY + 46 + row * 38
    xs = [CENT[d] for d in dsts]
    sx = CENT[src]
    left = min(xs) < sx
    far = min(xs) if left else max(xs)
    lw = tw(name + "   " + desc, 10) + 30
    if lw < abs(sx - far) - 40:
        text(min(sx, far) + 20, y - 19, lw, 16, f"<b>{h(name)}</b>   {h(desc)}", 10, color, raw=True)
    else:  # short channel: put the label to the left of its far end
        text(far - 14 - lw, y - 8, lw, 16, f"<b>{h(name)}</b>   {h(desc)}", 10, color, raw=True, align="right")
    line(sx - 16 if left else sx + 16, y, far + 4 if left else far - 4, y, color)
    for d in xs:
        vertex(None, d - 3, y - 3, 6, 6, "", f"ellipse;whiteSpace=wrap;html=1;fillColor={color};strokeColor={color};")
    vertex(None, sx - 16, y - 9, 32, 18, tag, f"rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor={color};fontSize=9;fontStyle=1;fontColor={color};")
channel(0, "X", ["F0", "F1", "F2", "F3"], RED, "同拍", "jump_target / jump_now",
        "X（jal · jalr · taken 分支）、M（trap，优先）→ F0 换地址 · F1 记在途个数 · F2 清 FIFO · F3 清 IB      ②")
channel(1, "X", ["F3"], ORANGE, "同拍", "cir_use[2] / cir_flush_behind",
        "X → F3 · 本拍用掉几个半字，同拍移位；可能依赖 hready，是最长的同拍路径      ⑤")
channel(2, "X", ["F4"], PURPLE[1], "同拍", "uop_stall / uop_clear", "X → F4 · 让 Zcmp 的 uop 序列停住或中止      ⑥")
channel(3, "X", ["F0"], PURPLE[1], "reg", "btb_set / btb_clear", "X → F0 · 写 BTB，下一拍生效（可选）      ③")
channel(4, "F0", ["X"], BLUE[1], "reg", "jump_target_rdy = !mem_addr_hold", "F0 → X · 总线正保持地址时不能跳转，X 停一拍      ②")

# ---------------- cards ----------------
KY = EY + 46 + 5 * 38 + 20
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
 (BLUE[1], "①  预取：F0 每拍决定发不发", [
  ("fetch_addr 每被总线接收一次就 +4，所以 F 总是按字在 PC 前面取", "L346"),
  ("是否再发由 fetch_stall 决定：FIFO 满；或 FIFO 有 1 项且还有在途；或在途 ≥ 2", "L416"),
  ("只看寄存器、不看本拍 hready：按「在途的都会回来」预留空间，hready 不会组合地影响下一个地址", "L413"),
  ("例：X 停住（div）→ 拍 0 发 W1 · 拍 1 发 W2，W1 进 FIFO · 拍 2 停发，W2 进 FIFO，正好满", ""),
  ("所以 FIFO 至少 2 项才能满速取指；RVC 指令消耗慢时 FIFO 很快满，取指自动降速", "L119"),
 ]),
 (RED, "②  跳转：jal / jalr / taken 分支 / trap", [
  ("来源：X 的 jal、jalr、taken 分支（目标在 X 算出）；M 的 trap 进入，优先于 X", "core.v:1376"),
  ("只有 jump_target_rdy = !mem_addr_hold 时能接受；总线正保持上拍地址时 X 停一拍", "L401"),
  ("接受那拍（jump_now）：目标当拍直接作为地址发出，不经过 fetch_addr", "L391"),
  ("同拍冲刷：FIFO、IB 清空；已发出未返回的个数记入 ctr_flush_pending，回来就丢", "L212 L436"),
  ("跳到奇数半字：首字低半无效；目标是 32 bit 指令时还要再取一个字，多 1 拍", "L462"),
  ("CIR 保留：X 被 stall 却发了跳转 → cir_flush_behind，保留当前指令、只冲刷后面的", "L648"),
  ("代价：jal 2 拍 = 拍 0 发目标 · 拍 1 数据进 IB / CIR（X 空 1 拍）· 拍 2 执行", ""),
 ]),
 (PURPLE[1], "③  分支：默认不跳，可选 1 项 BTB", [
  ("条件分支在 X 比较；taken 按 ② 发跳转，不 taken 什么都不做，等于静态预测「不跳」", "core.v:935"),
  ("可选 BTB 只有 1 项：记最近一次 taken 的后向条件分支（循环回跳）", "core.v:943"),
  ("F0：取到该分支所在的字 → 下一个地址直接换成目标，并给这条指令打上 predbranch 标记", "L343 L482"),
  ("X：预测对 → 不发跳转，PC ← BTB 目标；预测错 → 跳回顺序地址，并清 BTB", "core.v:912 948"),
  ("代价：预测对 1 拍；未预测的 taken、预测错都是 2 拍", ""),
 ]),
 (GREEN[1], "④  取回的数据：F1 → F2 → F3", [
  ("F1 数据回来先看 ctr_flush_pending：非 0 说明是跳转前的旧请求，丢弃", "L425"),
  ("元数据和数据一起走：哪半有效、总线错误或 PMP 失败、断点、预测分支", "L129-147"),
  ("FIFO 空且 IB 有空位 → 旁路，当拍进 IB；否则推入 FIFO，等 IB 有空位再弹出", "L594 L635"),
  ("进 IB 前先对齐：只有高半有效时（跳到奇数半字），把高半放到低位", "L617"),
  ("元数据只在被译码时才生效：带错误的字如果被跳转冲掉，就当没发生过", "L145"),
 ]),
 (PURPLE[1], "⑤  IB 与 CIR：半字粒度的队列", [
  ("指令可以是 16 或 32 bit，而且可以不按字对齐，所以 IB 按半字存，共 3 个槽", "L568"),
  ("X 每拍回送 cir_use = 用掉的半字数 0 / 1 / 2 → 同拍移位，再把新字接在剩余半字后面", "L625 L637"),
  ("剩余 ≤ 1 个半字（新字只半个有效时 ≤ 2）才收新字，同时决定 FIFO 弹不弹", "L634"),
  ("CIR = 槽 0、1 的解压版，和 IB 同一个沿锁存，也就是 IB 的队头", "L874"),
  ("例：内存 [c.addi | lw 低半] [lw 高半 | c.mv] → CIR=c.addi，用 1 → CIR=lw（跨字），用 2 → CIR=c.mv", ""),
  ("最长同拍路径：hready → X stall → cir_use → 移位 → 叠加 → 预译码 → 寄存器堆读地址", "L54"),
 ]),
 (BLUE[1], "⑥  预译码、解压与 uop", [
  ("预译码：从下一拍的 CIR 里提前抽出 rs1 / rs2，作寄存器堆读地址和 bypass 选择，省一拍", "L734"),
  ("它只是近似，不能用来判断 stall；正式译码仍在 X", "L85-93"),
  ("解压：16 bit → 32 bit，CIR 存的是解压后的指令；非法压缩码置 invalid", "L844"),
  ("Zcmp push / pop：一条指令拆成多个 uop，X 用 uop_stall / uop_clear 控制", "L838"),
  ("不开 C 扩展时没有解压，IB 第 3 个槽和对齐逻辑都会被常量折叠掉", "L810"),
 ]),
]
y = KY + 36
for r in range(2):
    y += 24 + max(card(KX[c], y, *CARDS[r * 3 + c]) for c in range(3))

# bottom row: timing, mapping, legend
G = "#9AA5B1"
hb = [
    card(KX[0], y, G, "时序对照（官方文档，总线无等待）", [
        "顺序 32 bit 指令每拍 1 条：拍 n 发地址 → 拍 n+2 X 执行",
        "jal / jalr 2 拍；taken 分支 2 拍；BTB 预测对 1 拍、预测错 2 拍",
        "跳到不按字对齐的 32 bit 指令：再 +1 拍（要取两个字）",
        "总线等待 n 拍 → 取指晚 n 拍；FIFO / IB 里已有的指令可以掩盖一部分",
        ("依据", "doc/sections/instruction_timings.adoc"),
    ], dashed=True),
    card(KX[1], y, G, "与 curryGPU ifetch_top 对照", [
        "fetch_addr ↔ ifetch_frontend 的 fetch_pc_q（每 warp 一个）",
        "I 侧 AHB + 存储 ↔ ifetch_l0i / ifetch_l1i",
        "FIFO + IB ↔ ifetch_ib；CIR ↔ IB 队头（decode 读的那条）",
        "cir_use ↔ decode 的弹出；jump ↔ redirect",
        "ctr_flush_pending ↔ epoch：Hazard3 单线程、按序返回，数在途个数就够；curryGPU 多 warp、可能乱序，用 epoch 判断过期",
    ], dashed=True),
]
LH = max(hb)
rect(None, KX[2], y, KW, LH, stroke=G, sw=2, rounded=1, arc=2, dashed=True)
text(KX[2] + 16, y + 8, KW - 32, 24, "图例", 13, G, bold=True)
for i, (col, s) in enumerate([
        (BLUE, "蓝色 = 组合步骤（F0 发地址、F4 预译码 / 解压）"),
        (GREEN, "绿色 = 存储侧（总线、F1 收数据）"),
        (PURPLE, "紫色 = 队列（F2 FIFO、F3 IB）"),
        (YELLOW, "黄色 owns = 这个小级拥有的寄存器")]):
    yy = y + 42 + i * 24
    vertex(None, KX[2] + 20, yy, 34, 16, "", f"rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor={col[0]};strokeColor={col[1]};")
    text(KX[2] + 64, yy - 2, 300, 20, s, 11, MUTED)
for i, s in enumerate(["黑粗杠 = 时钟沿（寄存器边界）", "灰色虚线框 = 同一拍内组合完成", "虚线小框 = 可选部件"]):
    yy = y + 42 + i * 24
    if i == 0:
        bar(KX[2] + 380, yy + 6, 34, 4)
    else:
        rect(None, KX[2] + 380, yy, 34, 16, stroke="#999999", dashed=True, rounded=1, arc=10)
    text(KX[2] + 424, yy - 2, 250, 20, s, 11, MUTED)
text(KX[2] + 20, y + 42 + 4 * 24 + 4, KW - 40, 40,
     "事件通道颜色：红 = 跳转，橙 = cir_use，紫 = uop / BTB，蓝 = jump_target_rdy\n画法参照 curryGPU subcore 目标流水线图（大流水线套小流水线）", 10, "#777777")
y += LH + 30

xml = ('<mxfile host="app.diagrams.net"><diagram name="hazard3_frontend"><mxGraphModel dx="1800" dy="1000" grid="1" gridSize="10" '
       f'page="1" pageWidth="{W}" pageHeight="{int(y)}" math="0" background="#FFFFFF"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
       + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>\n')
open(sys.argv[1], "w").write(xml)
