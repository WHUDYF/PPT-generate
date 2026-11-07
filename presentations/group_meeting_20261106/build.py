#!/usr/bin/env python3
"""Group meeting deck v4 (2026-11-07), midterm-review style. Focus: causal structural IR with
container / state facets, for AI RTL generation and traceable AI verification.
Style follows projects/midterm_review_ppt169_20261028; ideas follow the paper-1 v4 draft
and curryGPU/document/2026-11-05-research-directions.md."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml.ns import qn

FONT = "Microsoft YaHei"
NAVY = RGBColor(0x1F, 0x3A, 0x5F)
MID = RGBColor(0x5B, 0x7B, 0xA6)
RED = RGBColor(0xC8, 0x10, 0x2E)
BODY = RGBColor(0x22, 0x22, 0x22)
SUB = RGBColor(0x6B, 0x72, 0x80)
TER = RGBColor(0x9C, 0xA3, 0xAF)
STRIP = RGBColor(0xF5, 0xF7, 0xFA)
RULE = RGBColor(0xE5, 0xE7, 0xEB)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
FOOT = "组会 · 2026-11"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
W, H = prs.slide_width, prs.slide_height


def style(run, size, color=BODY, bold=False):
    f = run.font
    f.name, f.size, f.bold = FONT, Pt(size), bold
    f.color.rgb = color
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {})
            rpr.append(el)
        el.set("typeface", FONT)


def rich(p, parts, size, color=BODY, bold=False):
    """parts: str with **red** spans."""
    segs = parts.split("**")
    for k, seg in enumerate(segs):
        if not seg:
            continue
        r = p.add_run()
        r.text = seg
        hot = k % 2 == 1
        style(r, size, RED if hot else color, bold or hot)


def text(slide, x, y, w, h, lines, size=18, color=BODY, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, gap=8):
    """lines: str | (str, opts). opts: size, color, bold, indent(int)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, ln in enumerate(lines):
        s, opt = (ln, {}) if isinstance(ln, str) else ln
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(gap)
        rich(p, ("    " * opt.get("indent", 0)) + s, opt.get("size", size),
             opt.get("color", color), opt.get("bold", bold))
    return tb


def rect(slide, x, y, w, h, fill=None, line=RULE, lw=1.0):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line; sh.line.width = Pt(lw)
    return sh


def box(slide, x, y, w, h, title, body=None, line=NAVY, fill=WHITE, tsize=17, bsize=13,
        tcolor=NAVY, align=PP_ALIGN.CENTER):
    sh = rect(slide, x, y, w, h, fill=fill, line=line, lw=1.5)
    tf = sh.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for m in ("margin_left", "margin_right"):
        setattr(tf, m, Inches(0.08))
    p = tf.paragraphs[0]; p.alignment = align
    rich(p, title, tsize, tcolor, True)
    if body:
        for b in body.split("\n"):
            q = tf.add_paragraph(); q.alignment = align
            rich(q, b, bsize, SUB)
    return sh


def hline(slide, x1, y, x2, color=RULE, w=1.0):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y), Inches(x2), Inches(y))
    c.line.color.rgb = color; c.line.width = Pt(w)


def vline(slide, x, y1, y2, color=RULE, w=1.0):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y1), Inches(x), Inches(y2))
    c.line.color.rgb = color; c.line.width = Pt(w)


def arrow(slide, x1, y1, x2, y2, color=MID, dashed=False, width=1.75):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color; c.line.width = Pt(width)
    if dashed:
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    ln = c.line._get_or_add_ln()
    ln.append(ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"}))


def strip(slide, s, y=6.35, h=0.6, size=17):
    r = rect(slide, 0.6, y, 12.1, h, fill=STRIP, line=None)
    text(slide, 0.85, y + 0.05, 11.7, h - 0.1, [s], size=size, anchor=MSO_ANCHOR.MIDDLE)


def notes(slide, s):
    slide.notes_slide.notes_text_frame.text = s


def page(title, tag):
    s = prs.slides.add_slide(BLANK)
    text(s, 0.6, 0.38, 10.4, 0.7, [title], size=27, color=NAVY, bold=True)
    text(s, 10.6, 0.5, 2.1, 0.4, [tag], size=12, color=SUB, align=PP_ALIGN.RIGHT)
    hline(s, 0.6, 1.08, 12.7, NAVY, 2.0)
    text(s, 0.6, 7.03, 4, 0.3, [FOOT], size=10, color=TER)
    text(s, 11.7, 7.03, 1, 0.3, [str(len(prs.slides))], size=10, color=TER, align=PP_ALIGN.RIGHT)
    return s


def table(slide, x, y, rows, colw, size=13, rowh=0.5, head=NAVY):
    t = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y),
                               Inches(sum(colw)), Inches(rowh * len(rows))).table
    for j, cw in enumerate(colw):
        t.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.text = ""
            c.fill.solid()
            c.fill.fore_color.rgb = head if i == 0 else (STRIP if i % 2 == 0 else WHITE)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.margin_left = c.margin_right = Inches(0.08)
            rich(c.text_frame.paragraphs[0], val, size, WHITE if i == 0 else BODY, i == 0)
    return t


def numbered(slide, x, y, w, items, tsize=17, bsize=14, step=0.95):
    """items: (title, body)."""
    for i, (t, b) in enumerate(items):
        yy = y + i * step
        text(slide, x, yy, 0.4, 0.4, [str(i + 1)], size=tsize, color=NAVY, bold=True)
        text(slide, x + 0.45, yy, w - 0.45, 0.4, [t], size=tsize, color=BODY, bold=True)
        if b:
            text(slide, x + 0.45, yy + 0.38, w - 0.45, step - 0.35, [b], size=bsize, color=SUB, gap=2)


def hero(slide, x, y, w, big, small, color=RED):
    text(slide, x, y, w, 0.6, [big], size=32, color=color, bold=True, align=PP_ALIGN.CENTER)
    text(slide, x, y + 0.62, w, 0.6, [small], size=13, color=SUB, align=PP_ALIGN.CENTER, gap=0)


T1, T2, T3, T4 = "一 · 问题", "二 · 思想", "三 · 验证", "四 · 计划"

# =============================================================== 1 cover
s = prs.slides.add_slide(BLANK)
rect(s, 1.0, 2.2, 0.08, 2.0, fill=NAVY, line=None)
text(s, 1.35, 2.15, 11, 0.9, ["带因果的结构 IR"], size=40, color=NAVY, bold=True)
text(s, 1.35, 3.15, 11, 0.6, ["容器面与状态面：提升 AI 生成 RTL 的能力，实现可追溯的 AI 验证"], size=20, color=BODY)
hline(s, 1.35, 4.5, 6.5, RULE)
text(s, 1.35, 4.7, 8, 0.5, ["组会汇报 · 2026-11"], size=15, color=SUB)
notes(s, "今天只讲一件事：我们在 RTL 的结构描述里加入因果关系，把内部结构拆成容器面和状态面，"
         "用它来让 AI 生成更复杂的 RTL，并且在出错时能追到错从哪里来。")

# =============================================================== 2 background
s = page("背景：AI 已经能写出第一版流水线 RTL", T1)
numbered(s, 0.6, 1.4, 7.3, [
    ("ChatCPU（DAC'24）", "LLM 逐模块生成 6 级 RISC-V，并已流片"),
    ("Design Conductor；2610.39570", "agent 从需求做出 5 级流水 CPU，乃至三发射乱序核"),
    ("curryGPU 子核", "约 10.8 万行 Verilog，大部分由 AI 生成；约 1960 个提交带 AI 署名"),
], tsize=17, bsize=14, step=1.05)
vline(s, 8.2, 1.45, 4.6)
hero(s, 8.4, 1.7, 4.3, "通过测试", "这些工作都止步于此")
text(s, 8.45, 3.1, 4.25, 1.5, ["但大型流水线的第一版能通过测试，不等于它可控：改一处会坏哪里、出错时错在哪，都说不清"],
     size=15, color=BODY)
strip(s, "问题：AI 生成的流水线 RTL，**怎样做到真实可控**")
notes(s, "出处：survey/25-gen、survey/26-chatcpu。")

# =============================================================== 3 problem
s = page("问题：通过测试的第一版，并不可控", T1)
rows = [["可控的标准", "含义", "curryGPU 第一版的真实情况"],
        ["结构一致", "RTL 的级、状态、连线与设计一致", "功能被放到了图上没有的流水级，功能测试全过"],
        ["依赖显式", "每条跨级的时序依赖都写下来", "队列深度改 1 → 2，打破了没写下来的“发射间隔 ≥ 2”"],
        ["规格可信", "每条规格有来源、经过独立核对", "一句规格来自 AI 写的核实报告，本身是错的，验收仍判通过"],
        ["修改可预测", "改一处之前知道会影响哪里", "某条路径从 6 拍变 9 拍，慢 **6–7%**，人试了几轮才找到"]]
table(s, 0.6, 1.35, rows, [2.1, 4.0, 6.0], size=14, rowh=0.75)
strip(s, "四个问题的共同点：测试只看最终结果，**看不到结构与结构之间的因果**")
notes(s, "四条标准来自论文一 v4 §1.2。")

# =============================================================== 4 feedback
s = page("AI 自己修正时，缺的是“错从哪里来”", T1)
rows = [["给 AI 的反馈", "例：队列深度改动后出错", "例：两个模块接起来出错", "AI 可能怎么做"],
        ["测试结果", "“第 256 号输出错了”", "“整合后第 5051 拍不一致”", "在报错处打补丁"],
        ["第一处分歧", "“下游某状态是旧的”", "“下游模块的输入不一致”", "去改没错的下游模块"],
        ["按模块归因（ChatCPU）", "归到后改的模块", "归到后放进去的模块（其实两者都没错）", "改错模块"],
        ["**带因果的 IR**", "**改动打破了“发射间隔 ≥ 2”，依赖方是下游推进**", "**这条同拍的边在接口上没导出**", "**改对地方**"]]
table(s, 0.6, 1.35, rows, [2.6, 3.4, 3.6, 2.5], size=14, rowh=0.8)
strip(s, "前三种反馈都把 AI 引向**报错的位置**；只有沿因果关系，才能指向**出错的来源**")
notes(s, "这张表来自 v4 §1.3。只给测试结果时，AI 还容易插寄存器、加 lint_off 之类的假修复。"
         "别的领域也有数字：SWE-bench 上 AI“已解决”的补丁约 11% 不正确（ICSE'26）。")

# =============================================================== 5 core idea
s = page("核心思想：加入因果，把结构拆成容器面与状态面", T2)
box(s, 0.6, 1.4, 5.9, 1.9, "容器面：占位置", "有限的位置，被占了别人就得等\n例：scoreboard 最多 8 条；功能单元一拍只接一条\n追问：现在是谁占着？什么时候走？",
    tsize=19, bsize=14)
box(s, 6.8, 1.4, 5.9, 1.9, "状态面：存信息", "被写、被读，影响后面的决定，但不让人排队\n例：寄存器是否准备好；分支历史表\n追问：上一次是谁、哪一拍改的？",
    tsize=19, bsize=14)
numbered(s, 0.6, 3.6, 12, [
    ("一个结构可以两面都有", "scoreboard 既有 8 个位置（容器面），又记着每个寄存器还有谁没写完（状态面）；一次提交同时改变两面"),
    ("指令是在结构里流动的“灵魂”", "每类指令按路线依次使用各个结构；用五项规矩写清怎么用：几个位置、占多久、在哪判断、知道什么、多人抢时给谁"),
], tsize=16, bsize=14, step=1.05)
strip(s, "硬件 = **指令在使用结构做事**；因果就是“谁通过哪个结构的哪一面，影响了谁”")
notes(s, "这是思路总结 §1.10 的内容。分开“占位置”和“存信息”，是因为追因果时要往不同的方向追："
         "被占位置挡住，要找占着的人；因为信息没准备好，要找写它的人。")

# =============================================================== 6 causal edge + example
s = page("因果边：一个动作经过某一面影响另一个动作", T2)
text(s, 0.6, 1.25, 12, 0.4, ["每条边标明“本拍就看到”还是“下一拍才看到”。例：一条乘法后紧跟一条用它结果的加法"], size=14, color=SUB)
cols = ["第 t 拍", "第 t+1 拍", "第 t+2 拍", "第 t+3 拍"]
rows = [("mul a0, s0, s1", ["发射", "执行中", "算完", "提交"]),
        ("add a1, a0, s2", ["", "等待", "发射", "算完"]),
        ("功能单元（容器面）", ["", "被乘法占着", "", ""]),
        ("a0 是否就绪（状态面）", ["", "没有", "本拍算完即可用", ""])]
x0, y0, cw, rh = 3.4, 1.7, 2.3, 0.55
for j, c in enumerate(cols):
    box(s, x0 + j * cw, y0, cw - 0.06, 0.48, c, fill=NAVY, line=NAVY, tcolor=WHITE, tsize=14)
for i, (lab, cells) in enumerate(rows):
    y = y0 + 0.6 + i * rh
    text(s, 0.6, y + 0.08, 2.8, rh, [lab], size=14, color=NAVY, bold=True)
    for j, v in enumerate(cells):
        if v:
            hot = v in ("等待", "被乘法占着", "没有")
            box(s, x0 + j * cw, y + 0.04, cw - 0.06, rh - 0.1, v, line=RED if hot else MID,
                tcolor=RED if hot else NAVY, tsize=14)
numbered(s, 0.6, 4.75, 12, [
    ("加法的一次等待，记下两个原因、各自“被谁挡住”", "容器面：功能单元被乘法占着；状态面：a0 的写入者是那条乘法，还没算完"),
    ("“本拍算完、本拍可用”在模拟器代码里没写", "只是函数调用顺序带出来的——这类隐含的因果，正是 IR 要显式写出来的"),
], tsize=15, bsize=13, step=0.75)
strip(s, "模拟器按功能组织代码，因果**藏在调用顺序里**；IR 把它变成**可检查、可追溯**的边")
notes(s, "CVA6 模型的 IR 里有 19 条因果边，其中 13 条只由调用顺序或端口先后决定。")

# =============================================================== 7 use 1: generation
s = page("用途一：提升 AI 生成 RTL 的能力", T2)
labels = [("模拟器", "周期级模型"), ("因果 IR", "容器面 / 状态面 / 边"), ("FML 模型", "寄存器 / 本拍信号"),
          ("AI 生成 RTL", "照时序写电路"), ("逐拍比对", "与模型对照")]
for i, (t, b) in enumerate(labels):
    x = 0.6 + i * 2.48
    box(s, x, 1.45, 2.25, 1.15, t, b, line=RED if i == 1 else NAVY, tsize=17, bsize=12)
    if i < 4:
        arrow(s, x + 2.27, 2.03, x + 2.46, 2.03, color=NAVY)
numbered(s, 0.6, 2.95, 7.4, [
    ("给 AI 的不再只是“功能描述”", "而是每个结构的两面、谁检查谁占用、哪些是本拍可见、哪些要等下一拍"),
    ("本拍 / 下一拍正好对应 RTL", "隔一拍的边 → 读触发器；同拍的边 → 读组合逻辑输出"),
    ("最难的地方被显式化", "跨级同拍依赖、接口时序，是 AI 整合多个模块时最常出错的地方"),
], tsize=15, bsize=13, step=0.95)
vline(s, 8.25, 3.0, 5.9)
text(s, 8.5, 2.95, 4.2, 3, [("证据（初步）", {"bold": True, "color": NAVY, "size": 15}),
                           "route B：两模块各自全对、整合后出错，原因正是接口缺了一条同拍边",
                           ("待做：在 CVA6 上比较有 / 无因果 IR 时 AI 的生成成功率", {"color": RED})], size=14, gap=6)
strip(s, "一句话：**时序由模型规定，实现由 AI 完成，正确性由因果 IR 检查**")
notes(s, "这是 11-06 的决定：生成提升为论文一主线的一部分（思路总结 §1.11）。")

# =============================================================== 8 use 2: traceable verification
s = page("用途二：可追溯的 AI 验证", T2)
rows = [["沿因果边追到的来源", "AI 怎么做"],
        ["① 某个结构内部实现错了", "修"],
        ["② 结构之间的接口 / 同拍与寄存弄反了", "修"],
        ["③ 改动打破了别人依赖的时序规矩", "修，或登记规矩的修改"],
        ["④ 规格或参考本身错了", "**停下，报告给人**"],
        ["⑤ IR 漏画了一条依赖", "**停下，报告给人**"],
        ["⑥ 追不下去", "**停下，报告给人**"]]
table(s, 0.6, 1.35, rows, [5.2, 2.9], size=14, rowh=0.6)
text(s, 9.0, 1.35, 3.7, 4.4, [("为什么要“报”", {"bold": True, "color": NAVY, "size": 16}),
                             "规格错时让 AI 先试着修，它多半能凑出一个“通过”",
                             "给 AI 一个合法的“停下”出口，作弊大幅减少（ImpossibleBench：54% → 9%）",
                             "IR、检查对 AI 只读"], size=14, gap=6)
strip(s, "可追溯：每次失败都给出**哪个结构、哪一面、哪条边、哪一拍、被谁挡住**")
notes(s, "理论上属于基于模型的一致性诊断（Reiter 1987）；我们把连线和规格条目也当作可能出错的部件。")

# =============================================================== 9 related work
s = page("和已有工作的关系", T2)
rows = [["工作", "有什么", "缺什么（我们补的）"],
        ["HINT（2608.07625）", "规格与 RTL 之间的可执行中间层；状态归属", "不做周期精确；报错只到“哪一层”"],
        ["ChatCPU（DAC'24）", "周期精确模型作参考，逐模块生成", "每模块一个延迟；参考与 RTL 同源；归因到“新模块”"],
        ["Kôika / BSV / Assassyn", "同拍 / 寄存是语言概念，直接编译", "用于设计，不用于检查 AI 写的 RTL、不做归因"],
        ["基于模型的诊断（Reiter'87）", "先有模型，再用矛盾找故障部件", "连线默认不出错；没有规格条目这一类"],
        ["Zeller 因果链（FSE'02）", "对比两次运行找原因", "没有内部规格，要靠大量重跑"]]
table(s, 0.6, 1.35, rows, [3.2, 4.4, 4.5], size=14, rowh=0.72)
strip(s, "我们的位置：**容器面 / 状态面 + 周期级因果边**，同时作为 AI 生成的规格和可追溯验证的依据")
notes(s, "细节见 survey/25-gen-summary、survey/27-xdomain-summary。审稿人一定会问：既然时序都写清了，为什么不直接编译？"
         "我们的回答：模型有大量抽象，同一时序有多种实现，重点在检查与归因——待实验支撑。")

# =============================================================== 10 validation on CVA6
s = page("验证这个思想：在 CVA6 上从模拟器得到因果 IR", T3)
numbered(s, 0.6, 1.4, 6.2, [
    ("平台：CVA6", "开源 RISC-V，官方带 Python 周期级性能模型和可综合 RTL"),
    ("只看模型、逐条数出 IR", "14 个结构（10 个有容器面、5 个有状态面）、19 条因果边、10 种等待原因"),
    ("三方向检查", "没漏画 · 每次等待能解释 · 只用 IR 的规则能预测模型"),
], tsize=16, bsize=13, step=1.0)
vline(s, 7.0, 1.45, 5.4)
for i, (big, small) in enumerate([("1,312", "次运行，0 次解释不了的等待"), ("19 / 19", "条因果边都被触发过"),
                                  ("100%", "12.5 万条指令的发射拍，只用 IR 就全部推对")]):
    hero(s, 7.3, 1.35 + i * 1.35, 5.4, big, small)
strip(s, "结论：容器面 / 状态面 + 因果边的写法，**足以完整描述**这个模拟器的时序行为")
notes(s, "测试程序直接生成：单条指令、两两组合、压满资源，在 32 组参数下运行。预测器不调用模型，只按 IR 推算。")

# =============================================================== 11 corrections
s = page("这套写法也会暴露自己的问题：IR 被修正了 7 次", T3)
numbered(s, 0.6, 1.4, 12, [
    ("预测错误的惩罚可以中途变短", "状态面（分支历史）在等待期间被提交更新，预测改判——两条边碰在一起才出现"),
    ("“检查”与“占用”要分开", "每类指令发射前只检查一个单元，却占用好几个：分支挡得住存储，存储挡不住分支——单向挡住"),
    ("指令队列的对齐规则没写清", "预测器 307 个错误由此而来，补上后全部消失"),
], tsize=16, bsize=14, step=1.15)
strip(s, "这三次修正都来自“**只用 IR 去预测**”：能解释每一步，不等于 IR 的说法是对的")
notes(s, "每次修正都有证据、记录在案，旧条目不删、标为已被替代。")

# =============================================================== 12 next
s = page("下一步", T4)
numbered(s, 0.6, 1.4, 12, [
    ("按 IR 设计 FML 模型", "每个结构一个模块，状态分寄存器 / 本拍信号，隐含顺序写成显式信号；设计初稿已完成"),
    ("用官方 RTL 核对 IR", "先查 13 条只由代码顺序决定的边：真实硬件是不是也这样"),
    ("第一次 AI 生成实验", "CVA6 控制通路：有 / 无因果 IR 时，AI 生成的成功率、迭代次数、假修复"),
    ("可追溯验证实验", "注入错误，看能否归到正确的来源与类别；与 Zeller 式、SAT 调试式的方法对照"),
], tsize=16, bsize=14, step=1.05)
strip(s, "两条线最终汇合：**同一份因果 IR，既是 AI 生成的规格，也是验证追溯的地图**")
notes(s, "论文二（IR 不完整时怎么办）、论文三（性能瓶颈）在此基础上展开。")

# =============================================================== 13 discussion
s = page("想和大家讨论的问题", "讨论")
for i, (q, d) in enumerate([
        ("容器面 / 状态面的划分合理吗？", "一个结构可以两面都有；分开是为了追因果时往不同方向追。有没有它覆盖不了的硬件结构？"),
        ("为什么不直接编译？", "时序已写清，BSV / Kôika 可直接编译出 RTL。我们强调抽象、实现选择与检查归因，够不够？"),
        ("下一个平台", "CVA6 没有多请求方仲裁和 credit。下一个用 Vortex 还是 curryGPU？")]):
    y = 1.4 + i * 1.6
    text(s, 0.6, y, 0.5, 0.5, [str(i + 1)], size=26, color=RED, bold=True)
    text(s, 1.15, y + 0.02, 4.0, 0.6, [q], size=18, color=NAVY, bold=True)
    text(s, 5.2, y + 0.04, 7.5, 1.3, [d], size=15, color=BODY)
    if i < 2:
        hline(s, 0.6, y + 1.42, 12.7)
notes(s, "第一个问题最想听意见。")

out = "/home/dyf/PPT-generate/presentations/group_meeting_20261106/group_meeting_20261106.pptx"
prs.save(out)
print(out, len(prs.slides), "slides")
