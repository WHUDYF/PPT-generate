import html, sys
cells = []
n = [0]
def esc(s): return html.escape(s, quote=True).replace("\n", "&#xa;")
def text(x, y, w, h, v, size=9, bold=False, align="left", color="#000000"):
    n[0] += 1
    st = f"text;html=1;fontSize={size};align={align};verticalAlign=middle;strokeColor=none;fillColor=none;fontColor={color};" + ("fontStyle=1;" if bold else "")
    cells.append(f'<mxCell id="t{n[0]}" value="{esc(v)}" style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
def box(id, x, y, w, h, v, size=9, stroke="#000000", fill="#FFFFFF", bold=False, mono=False, valign="top", dashed=False, sw=1):
    st = (f"rounded=0;whiteSpace=wrap;html=1;fontSize={size};strokeColor={stroke};fillColor={fill};align=left;"
          f"verticalAlign={valign};spacingLeft=6;spacingTop=3;strokeWidth={sw};")
    if bold: st += "fontStyle=1;"
    if mono: st += "fontFamily=Courier New;"
    if dashed: st += "dashed=1;"
    cells.append(f'<mxCell id="{id}" value="{esc(v)}" style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
def edge(id, s, t, label="", kind="latest", pts=None, ex=None, en=None):
    color = {"latest": "#0066CC", "curr": "#888888", "write": "#000000"}[kind]
    st = f"endArrow=block;endSize=5;html=1;strokeColor={color};fontSize=9;fontColor={color};labelBackgroundColor=#FFFFFF;edgeStyle=orthogonalEdgeStyle;rounded=0;"
    if kind == "curr": st += "dashed=1;dashPattern=6 4;"
    if kind == "latest": st += "strokeWidth=2;"
    if ex: st += f"exitX={ex[0]};exitY={ex[1]};exitDx=0;exitDy=0;"
    if en: st += f"entryX={en[0]};entryY={en[1]};entryDx=0;entryDy=0;"
    g = '<mxGeometry relative="1" as="geometry">'
    if pts: g += '<Array as="points">' + "".join(f'<mxPoint x="{a}" y="{b}"/>' for a, b in pts) + '</Array>'
    g += '</mxGeometry>'
    cells.append(f'<mxCell id="{id}" value="{esc(label)}" style="{st}" edge="1" parent="1" source="{s}" target="{t}">{g}</mxCell>')
def vline(x, y0, y1):
    n[0] += 1
    cells.append(f'<mxCell id="v{n[0]}" value="" style="endArrow=none;html=1;dashed=1;dashPattern=6 6;strokeColor=#999999;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{x}" y="{y0}" as="sourcePoint"/><mxPoint x="{x}" y="{y1}" as="targetPoint"/></mxGeometry></mxCell>')

BLUE, RED = "#0066CC", "#CC0000"
TASKFILL = "#EAF2FB"

# ---------- header ----------
text(20, 30, 1600, 26, "curryGPU 取指子系统 ifetch_top   →   FML 模块与 task 切分（草案）", 17, True)
text(20, 64, 2300, 16, "参数（与 RTL 相同）   Subcores=4   WarpsPerSubcore=12   Instr=128b   Line=1024b=8 instr   L0I=64 行全相联 / subcore   L1I=4 way × 128 set   MissQ=48+16   IB=8/warp   Dispatch=2 instr/拍   FillBeat=256b × 4   时钟=SM 核心时钟（一个 fml::Clock）")
text(20, 84, 2300, 16, "FML 层次   Sm → Ifetch ×1 → { Frontend ×4（含 warp 状态、取指仲裁、L0I）,  Ib ×4,  L1i ×1（含 tag / data / miss queue / 预取窗口） };   上游 subcore_top ×4（S1.decode、S2.issue）、sm_top cta_dispatch；下游 lsu_top 指令 TLB、L2 访存出口")
text(20, 104, 2300, 16, "访问模式   &T = 读本拍开始时的值（RTL 寄存器输出，不建立先后）     &'latest T = 读本拍其他 task 写完之后的值（RTL 同拍组合通路，建立先后）     &mut T = 写（每个状态只有一个写者）。下图的列 = 由访问模式推导出的一个时钟沿内的先后层次，不是手工指定的顺序")
text(20, 124, 2300, 16, "依据   ifetch_top.drawio（curryGPU docs/design/uarch）；fr_ready 组合式 ifetch_l1i.v:322；redirect 同拍参与 lookup_response_live ifetch_frontend.v:251；IB 同拍推送/弹出/旁路 ifetch_ib.v:45-50、flush ifetch_ib.v:182")

# ---------- big box + stage columns ----------
box("big", 245, 150, 1865, 860, "", stroke="#000000", fill="none")
text(1610, 154, 490, 16, "Ifetch      FML module   ×1 per SM", 11, True, "right")
vline(760, 150, 1010); vline(1460, 150, 1010)
text(265, 172, 480, 30, "层 0\n先写同拍请求的 task", 10, True, "center")
text(775, 172, 670, 30, "层 1\nFrontend.cycle ×4（读层 0 的 &'latest 结果）", 10, True, "center")
text(1475, 172, 620, 30, "层 2\n寄存器更新 task（读层 1 的 &'latest 请求）", 10, True, "center")

# ---------- external upstream (left) ----------
box("s2", 20, 215, 205, 92, "subcore_top ×4   S2.issue\n分支状态机 Redirect 拍\n写 RedirectReq（&mut）\nsm_top 4→1 仲裁后每拍 1 个", dashed=True)
box("s1", 20, 330, 205, 80, "subcore_top ×4   S1.decode\n读 IbView.head_instr（&，上一拍）\n写 PopReq（&mut）", dashed=True)
box("cta", 20, 435, 205, 80, "sm_top   cta_dispatch\nLaunchRetire\nlaunch / retire / exit_mask", stroke=RED, dashed=True)
text(20, 520, 205, 16, "⑤ 时序待核", 9, False, "left", RED)

# ---------- external downstream (right) ----------
box("tlb", 2135, 720, 230, 70, "lsu_top   sm_tlb\n指令 TLB（翻译请求 / 应答）\nfml::Fifo 两端", dashed=True)
box("l2", 2135, 830, 230, 70, "L2 / 访存出口\nfml::Fifo<Mf>\n缺失行请求与回填", dashed=True)

# ---------- layer 0: note ----------
box("l0note", 265, 215, 480, 300,
    "本层还有两个 Ifetch 之外的 task（左侧虚线框）：\n"
    "  • S2.issue：写 RedirectReq\n"
    "  • S1.decode：读 IbView、写 PopReq\n\n"
    "它们和 L1i.serve 之间没有共享状态，\n"
    "FML 可以把三者放进同一批并行执行。\n\n"
    "Ifetch 内部只有 L1i.serve 在这一层：\n"
    "它要先算出本拍 4 个 subcore 里\n"
    "谁的需求被服务（demand_here），\n"
    "Frontend 才能决定 fr 是否被接收。  ①", size=10, stroke="#BBBBBB")

# ---------- layer 1: Frontend ----------
box("fe", 775, 215, 670, 360, "Frontend        FML module   ×4（每 subcore 一个实例，4 行同一张表）", size=11, bold=True)
box("fe_st", 787, 243, 646, 92,
    "状态（Frontend 独占）\n"
    "warp[12]：fetch_pc 35b   epoch 2b   occupied   miss_pending   miss_wait   starve_count 7b\n"
    "单槽：lookup（warp / pc / epoch）   miss_rsp（warp / pc / epoch）   freq_pace（每 4 拍 ≤1 次 fr）\n"
    "l0i：tag[64] 32b   valid[64]   data[64] × 1024b = 8 KiB   rr_ptr   填充 stage 1024b + beat 2b")
box("fe_t", 787, 345, 646, 218,
    "#[fml::task(triggers = (clock,))]\n"
    "fn cycle(ctx: &mut fml::TaskCtx,\n"
    "    st: &mut FeState,  l0i: &mut L0i,\n"
    "    redirect:  &'latest RedirectReq,     // ③ 同拍生效\n"
    "    served:    &'latest [bool; 4],       // ① L1i.serve 本拍结果\n"
    "    lifecycle: &LaunchRetire,            // ⑤ & 还是 &'latest 待核\n"
    "    ib:   &IbView,      // count / deadline，上一拍\n"
    "    fill: &FillBeat,    // ④ L1i 回送流寄存器\n"
    "    push: &mut PushReq, // ≤2 条 + flush\n"
    "    fr:   &mut FrReq,   // L0I 缺失 → L1I\n"
    ") -> Result<(), fml::SimError>\n"
    "// 重定向/生命周期 → lookup 响应是否 live → 推送 IB\n"
    "// → eligible 仲裁 12→1 → 发 L0I 查找 → 缺失时发 fr",
    size=9, stroke=BLUE, fill=TASKFILL, mono=True, sw=2)

# ---------- layer 2: Ib ----------
box("ib", 1475, 215, 620, 360, "Ib        FML module   ×4（每 subcore 一个实例）   ②", size=11, bold=True, stroke=BLUE)
box("ib_st", 1487, 243, 596, 76,
    "状态（只有 Ib.step 写）\n"
    "mem[2 bank][48][128b] = 12 warp × 8 深   每 warp head / tail / count\n"
    "head_instr[12] 队头旁路寄存器   deadline[12] 8b（送 Frontend 仲裁）")
box("ib_t", 1487, 330, 596, 130,
    "#[fml::task(triggers = (clock,))]\n"
    "fn step(ctx: &mut fml::TaskCtx,\n"
    "    ib:   &mut IbState,\n"
    "    push: &'latest PushReq,   // Frontend 本拍写的\n"
    "    pop:  &'latest PopReq,    // S1.decode 本拍写的\n"
    ") -> Result<(), fml::SimError>\n"
    "// = RTL 的 next-state：flush > 推送/弹出/旁路",
    size=9, stroke=BLUE, fill=TASKFILL, mono=True, sw=2)
box("ib_view", 1487, 472, 596, 90,
    "IbView = { count[12], deadline[12], head_instr[12] }\n"
    "别人只用 & 读它（本拍开始时的寄存器值）：\n"
    "  • Frontend 用 count / deadline 算 has_room 和仲裁 key\n"
    "  • S1.decode 读 head_instr 取指令\n"
    "所以 Frontend、S1.decode 与 Ib.step 之间不需要额外顺序")

# ---------- L1i ----------
box("l1i", 265, 640, 1830, 355, "L1i        FML module   ×1 per SM（4 subcore 共享）——一个模块、两个 task   ①", size=11, bold=True, stroke=RED)
box("l1_serve", 277, 670, 468, 190,
    "#[fml::task(triggers = (clock,))]\n"
    "fn serve(ctx: &mut fml::TaskCtx,\n"
    "    regs:   &L1iState,      // 上一拍\n"
    "    served: &mut [bool; 4], // demand_here\n"
    ") -> Result<(), fml::SimError>\n"
    "// tag 口每拍 1 次：\n"
    "// 交付 > 需求 > 推送 > 窗口\n"
    "// 需求在 subcore 间轮转",
    size=9, stroke=BLUE, fill=TASKFILL, mono=True, sw=2)
box("l1_st", 787, 670, 646, 190,
    "状态（只有 L1i.capture 写）\n"
    "freq[4]：每 subcore 1 项需求寄存   fr_ready[k] = !freq_valid[k] || served[k]\n"
    "tag：4 way × 128 set × 25b，valid[512]，rr_ptr[128]\n"
    "data：512 行 × 1024b = 64 KiB（读写各 1 口 / 拍）\n"
    "hit_pending[4] / hit_data[4]：命中行按 subcore 暂存\n"
    "stream[4]：回送流，每拍 1 beat × 256b，4 拍一行  →  FillBeat\n"
    "miss_queue：48 需求项（按 warp）+ 16 预取项\n"
    "预取窗口[4]：L+1 … L+8；L0I 下一行推送")
box("l1_cap", 1487, 670, 596, 190,
    "#[fml::task(triggers = (clock,))]\n"
    "fn capture(ctx: &mut fml::TaskCtx,\n"
    "    regs:   &mut L1iState,\n"
    "    served: &'latest [bool; 4],\n"
    "    fr:     &'latest [FrReq; 4], // 4 个 Frontend\n"
    "    tlb:    &mut TlbPort,\n"
    "    l2:     &mut fml::FifoTx<Mf>,\n"
    ") -> Result<(), fml::SimError>",
    size=9, stroke=BLUE, fill=TASKFILL, mono=True, sw=2)
box("l1_note", 277, 872, 1806, 110,
    "为什么拆成两个 task：RTL 里 fr_ready 是组合输出（ifetch_l1i.v:322），Frontend 的 fr_valid 又在同一拍被 L1I 锁存进 freq。\n"
    "若 L1i 只有一个 task，它既要在 Frontend 之前（给出 served），又要在 Frontend 之后（读 fr）→ FML 加载时报环。\n"
    "拆开后：serve（层 0，只读上一拍状态）→ Frontend（层 1）→ capture（层 2，单写者更新全部寄存器）。这正是 RTL 里\"组合输出\"和\"时钟沿更新\"两半的对应。\n"
    "同理 Ib 两端（Frontend 推送 / flush、S1.decode 弹出）都只写请求，存储由 Ib.step 一个 task 更新 ②。",
    size=10, stroke="#BBBBBB")

# ---------- edges ----------
edge("e_s2", "s2", "fe_t", "RedirectReq   &'latest  ③", "latest", pts=[(250, 261), (250, 395)], ex=(1, 0.5), en=(0, 0.2))
edge("e_cta", "cta", "fe_t", "LaunchRetire   & / &'latest ?  ⑤", "curr", ex=(1, 0.5), en=(0, 0.75))
edge("e_srv", "l1_serve", "fe_t", "served[4]   &'latest  ①", "latest", pts=[(760, 740), (760, 440)], ex=(1, 0.35), en=(0, 0.45))
edge("e_push", "fe_t", "ib_t", "PushReq   &'latest", "latest", ex=(1, 0.3), en=(0, 0.5))
edge("e_fr", "fe_t", "l1_cap", "FrReq[4]   &'latest  ①", "latest", pts=[(1455, 520), (1455, 740)], ex=(1, 0.8), en=(0, 0.35))
edge("e_srv2", "l1_serve", "l1_cap", "served[4]   &'latest（同模块）", "latest", pts=[(511, 618), (1785, 618)], ex=(0.5, 0), en=(0.5, 0))
edge("e_pop", "s1", "ib_t", "PopReq   &'latest", "latest", pts=[(235, 370), (235, 592), (1470, 592), (1470, 440)], ex=(1, 0.5), en=(0, 0.85))
edge("e_view", "ib_view", "fe_t", "IbView   &", "curr", ex=(0, 0.25), en=(1, 0.5))
edge("e_fill", "l1_st", "fe_t", "FillBeat   &  ④", "curr", ex=(0.3, 0), en=(0.3, 1))
edge("e_tlb", "l1_cap", "tlb", "", "write", ex=(1, 0.4), en=(0, 0.5))
edge("e_l2", "l1_cap", "l2", "", "write", ex=(1, 0.8), en=(0, 0.5))

# ---------- legend ----------
box("lg", 20, 640, 205, 170, "图例\n\n黑框   FML module（拥有状态）\n蓝底粗框   FML task\n虚线框   Ifetch 之外的 task\n\n蓝粗箭头   &'latest（定先后）\n灰虚箭头   &（上一拍，不定先后）\n黑细箭头   fml::Fifo 端口\n\n蓝/红框编号 → 下方说明", size=9)

# ---------- order DAG ----------
box("dag", 20, 1035, 520, 120,
    "一个时钟沿内由访问模式推导出的顺序\n\n"
    "  S2.issue ─┐\n"
    "  L1i.serve ┴─► Frontend.cycle ×4 ─┬─► Ib.step ×4\n"
    "  S1.decode ───────────────────────┘   L1i.capture\n\n"
    "同一层内的 task 互不冲突，可由多个 worker 并行；\n"
    "没有任何手写的执行顺序。", size=10, mono=False, bold=False)

# ---------- callouts ----------
co = [
 (RED, "① fr_ready 跨模块组合环 → L1i 拆成两个 task",
  "fr_ready_o[k] = !freq_valid_q[k] || demand_here（ifetch_l1i.v:322），而 fr_valid 又在同拍被锁存。单个 task 无法同时在 Frontend 前后运行，FML 加载时会报环。拆成 serve（只读上一拍）和 capture（单写者）后，顺序由 &'latest 自动推出。"),
 (BLUE, "② IB 两端同拍改同一存储 → 请求 + Ib.step",
  "Frontend 推送 / flush，S1.decode 弹出，count==0 或同拍弹出时还有写旁路（ifetch_ib.v:45-50）。FML 每个状态只能有一个写者：两端只写 PushReq / PopReq，Ib.step 用 &'latest 读二者，按 flush > 推送 / 弹出 / 旁路更新。"),
 (BLUE, "③ redirect 必须同拍可见 → &'latest",
  "lookup_response_live 直接用 redirect_valid_i 作废本拍的 L0I 响应（ifetch_frontend.v:251），epoch 同拍 +1。若写成 &，Frontend 晚一拍看到重定向，被作废的响应会写进 IB，周期级不再与 RTL 一致。"),
 ("#000000", "④ L1I 回送流来自寄存器 → & 即可",
  "stream_*_q 每拍出 1 beat（4 拍一行），是 L1I 的寄存器输出。Frontend 用 & 读，不建立先后：4 个 Frontend 与 L1i.capture 可以并行。IbView 同理。能用 & 的地方都用 &，这是并行度的来源。"),
 (RED, "⑤ launch / retire / exit 的时序待核",
  "它们同样参与 lookup_response_live 和 IB flush。若 sm_top 给出的是寄存器输出，用 &；若是同拍组合（cta_dispatch 当拍决定），要用 &'latest，把 cta_dispatch 排在 Frontend 之前。需要对照 sm_top.v:1901 一带确认。"),
 (RED, "⑥ FML 目前没有、需要外挂的部分",
  "时序契约（taken 分支到目标发射 ≥10 拍、每 4 拍最多 1 次 fr、L0I 1 拍查找）、握手 / 阶段结构，以及与 RTL 信号名的对应表。FML 只检查同拍读写顺序；这些要像 S1 原型那样由 contract 层读 .fasm 另行检查。"),
]
for i, (c, title, body) in enumerate(co):
    col, row = i % 3, i // 3
    x, y = 560 + col * 600, 1035 + row * 130
    box(f"co{i}", x, y, 585, 118, title + "\n\n" + body, size=10, stroke=c, sw=2 if c != "#000000" else 1)
    cells[-1] = cells[-1].replace("fontSize=10;", "fontSize=10;", 1)

xml = ('<mxfile host="app.diagrams.net"><diagram name="fml_ifetch_partition"><mxGraphModel dx="1800" dy="1000" grid="1" gridSize="10" '
       'page="1" pageWidth="2400" pageHeight="1300" math="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
       + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>\n')
open(sys.argv[1], "w").write(xml)
