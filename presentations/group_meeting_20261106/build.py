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

# =============================================================== 2 background: simulators
s = page("背景 ①：模拟器把“指令”和“部件”的关系藏在了代码里", T1)
text(s, 0.6, 1.3, 12, 0.5, ["硬件实际工作时：**指令是灵魂，部件是身体**——指令依次流过各个部件，部件的位置和状态决定指令哪一拍能走"],
     size=17)
rows = [["模拟器", "组织方式"],
        ["GPGPU-Sim / Accel-Sim", "GPU 周期级模拟器；route B 用它的 FML 移植版"],
        ["gem5（MinorCPU / O3CPU）", "最常用的 CPU 模拟器"],
        ["CVA6 官方性能模型", "Python，约 670 行；我们的实验对象"],
        ["Vortex simX", "开源 GPGPU 的 C++ 周期级模拟器，与官方 RTL 同仓库"],
        ["PyMTL3", "功能级 / 周期级 / RTL 三层，周期级与 RTL 不要求一一对应"]]
table(s, 0.6, 2.0, rows, [3.1, 3.9], size=13, rowh=0.58)
vline(s, 7.95, 2.05, 5.5)
text(s, 8.2, 1.95, 4.5, 3.6, [("以 CVA6 模型为例（我们逐条核对过）", {"bold": True, "color": NAVY, "size": 15}),
                             "19 条因果边里，**13 条**只由函数调用顺序或端口先后决定，代码里没有一句话表达这个意图",
                             "每类指令发射前只**检查**一个部件，却**占用**好几个：单向挡住，读代码时很容易看漏",
                             "注释说乘除与第二 ALU 是同一部件，代码行为并非如此"], size=14, gap=7)
strip(s, "模拟器有部件也有指令，但“**哪条指令在哪一拍、经过哪个部件、挡住了谁**”没有写成可检查的规格")
notes(s, "措辞要准：不是说模拟器没有部件和指令的概念——gem5 的功能单元按指令类型配置，GPGPU-Sim 有流水线寄存器和 scoreboard。"
         "我们说的是：指令与部件之间的因果关系隐含在代码执行顺序里。"
         "右边三条是我们在 CVA6 模型上逐条核对的结果；对 gem5、GPGPU-Sim 是同类的经验判断，未逐条验证。")

# =============================================================== 2a example from CVA6
s = page("例子：CVA6 模型里“谁挡住了谁”藏在两段代码的组合里", T1)
text(s, 0.6, 1.25, 12, 0.4, ["双发射（每拍最多发两条），实验 2 的真实记录；两段程序只差指令顺序；右侧方框是发射的拍"], size=14, color=SUB)
cases = [("情况 A：先加载，后分支", [("#8", "lw（加载）", "第 4 拍", False), ("#9", "bne（分支）", "第 4 拍", False)],
          "同一拍都发出去了；这一拍“存储单元”上有两个占用者"),
         ("情况 B：先分支，后存储", [("#8", "bne（分支）", "第 4 拍", False), ("#9", "sw（存储）", "第 5 拍", True)],
          "记录：第 4 拍被“存储单元”挡住，挡住它的是第 8 条（分支）")]
for k, (title, rows, note) in enumerate(cases):
    x = 0.6 + k * 3.25
    text(s, x, 1.75, 3.1, 0.45, [title], size=16, color=NAVY, bold=True)
    for r, (n, ins, cyc, hot) in enumerate(rows):
        y = 2.3 + r * 0.62
        text(s, x, y + 0.1, 0.75, 0.5, [n], size=12, color=SUB)
        box(s, x + 0.72, y, 1.3, 0.5, ins, line=MID, tsize=11)
        box(s, x + 2.07, y, 1.03, 0.5, cyc, line=RED if hot else MID, tcolor=RED if hot else NAVY, tsize=11)
    text(s, x, 3.65, 3.05, 0.9, [note], size=13, color=RED if k else BODY)
    if k:
        vline(s, x - 0.13, 1.8, 4.5)
vline(s, 7.05, 1.8, 5.95)
code = ("def issue_branch(self):   # 分支发射时\n"
        "    self.alu = True\n"
        "    self.branch = True\n"
        "    # Stores are not allowed yet\n"
        "    self.stu = True        # 也标“存储单元”忙\n"
        "\n"
        "def issue_ldu(self):      # 加载发射时\n"
        "    self.ldu = True\n"
        "    self.stu = True        # 也标“存储单元”忙")
cb = rect(s, 7.3, 1.75, 5.4, 2.35, fill=STRIP, line=RULE)
tb = s.shapes.add_textbox(Inches(7.45), Inches(1.82), Inches(5.2), Inches(2.25)).text_frame
tb.word_wrap = True
for i, ln in enumerate(code.split("\n")):
    p_ = tb.paragraphs[0] if i == 0 else tb.add_paragraph()
    r_ = p_.add_run(); r_.text = ln
    r_.font.name = "Consolas"; r_.font.size = Pt(12); r_.font.color.rgb = NAVY
text(s, 7.3, 4.3, 5.4, 1.2, ["发射**前**：每类只查自己那一位——存储查“存储单元”，分支只查“分支单元”",
                            ("model.py 第 290–300、323–335 行", {"size": 11, "color": TER})], size=13, gap=3)
numbered(s, 0.6, 4.6, 6.3, [("挡住是单向的", "分支挡得住存储；加载、存储都挡不住分支"),
                            ("意图看不出", "唯一的说明是一句注释“Stores are not allowed yet”")], tsize=14, bsize=12, step=0.68)
strip(s, "IR 里明确写成：分支对存储单元“**只占用、不检查**”，存储对它“**检查并占用**”")
notes(s, "情况 A、B 分别来自实验 2 的测试程序 g2-load-branch、g2-branch-store，参数 i2c2-sb8-fw1-rn1。"
         "单向的挡住关系不是写在一个地方的规则，而是“发射时标哪些位”和“发射前查哪一位”两段代码合起来产生的。"
         "我第一次整理 IR 时就漏了，是只用 IR 的预测器算错了 38 个情况才暴露出来。")

# =============================================================== 2b background: HINT
s = page("背景 ②：把微架构明确写出来，AI 就写得更好", T1)
numbered(s, 0.6, 1.4, 6.9, [
    ("HINT（arXiv 2608.07625）的启发", "在规格与 RTL 之间加一层可执行的中间层，写明状态归属、提交纪律；AI 先写这一层，再照着写 RTL"),
    ("Representation Bottleneck（arXiv 2604.17097）", "6 种中间表示、202 个任务：换表示，仿真通过率 **3% → 88%**；换更强的模型，提升不到 1.25 倍"),
    ("FML（合作者）", "按部件建模，读别的部件时必须写明读本拍值还是上一拍值——和中间 IR 一样，体现的是实际微架构"),
], tsize=16, bsize=14, step=1.25)
vline(s, 7.75, 1.45, 5.4)
text(s, 8.0, 1.4, 4.7, 4, [("我们比 HINT 多了什么", {"bold": True, "color": NAVY, "size": 16}),
                          "HINT 是**事务级**，原文明确不做周期精确；我们写明本拍还是下一拍",
                          "HINT 没有容器面 / 状态面和因果边；出错时只能说“错在哪一层”",
                          "我们能追到**哪个部件、哪一面、哪一拍、被谁挡住**"], size=14, gap=8)
strip(s, "目的：让 AI 在**复杂处理器**上也能生成 RTL，并且**更快、更好**——复杂处理器必须处理指令与结构之间的关系")
notes(s, "注意出处：3% → 88% 和 < 1.25 倍出自 Representation Bottleneck，不是 HINT（旧笔记 survey/08-conclusions 把两者写在一起，引用时要分开）。"
         "HINT 是 Qiang Xu 组的工作；FML 是合作者的框架。"
         "这一页的逻辑：表示层比模型更重要；我们的表示层在 HINT 的基础上加了周期级的因果与容器面 / 状态面。")

# =============================================================== 3 problem: complexity cliff
s = page("问题 ①：结构越复杂，AI 越写不对", T1)
rows = [["Benchmark", "考的是什么", "结果"],
        ["VerilogEval v2（NVIDIA，2024）", "单个模块，按描述写 RTL", "最好的模型通过率 **89–98%**，基本饱和"],
        ["ArchXBench（MLCAD'25）", "6 级：组合 → 多周期 → **流水线** → 层次化", "从第 4 级（流水线）起，**所有模型全部失败**"],
        ["CVDP（NVIDIA，2025）", "783 题，模块到小子系统", "代码生成 pass@1 最高约 **34%**"],
        ["HWE-Bench（2026）", "417 个真实 bug 修复：RISC-V 核、SoC", "小核 > 90%，SoC **< 65%**；难在定位和硬件语义"]]
table(s, 0.6, 1.4, rows, [3.4, 4.3, 4.4], size=14, rowh=0.75)
text(s, 0.6, 5.35, 12.1, 0.8, ["流水线里，一条指令能不能前进，取决于它和 scoreboard、功能单元、队列、仲裁之间的关系——这正是单模块 benchmark 考不到的"],
     size=15, color=BODY)
strip(s, "难点已经从“写对一个模块”，转到**处理好指令与结构之间的关系**")
notes(s, "数字来自 survey/01-benchmarks-models（中期报告也用过）。ArchXBench 中 o4-mini-high 30 题对 16 题，"
         "但从 L4 起全部失败。这一页对应“目的”：让 AI 在复杂处理器上也能生成 RTL。")

# =============================================================== 4 problem: tests are not enough
s = page("问题 ②：只看测试结果，AI 改不到地方", T1)
text(s, 0.6, 1.35, 5.6, 0.45, ["别的领域的证据"], size=17, color=NAVY, bold=True)
numbered(s, 0.6, 1.9, 5.6, [
    ("SWE-bench（Wang 等 ICSE'26）", "AI“已解决”的补丁约 **11%** 不正确"),
    ("自动程序修复（Qi 等 ISSTA'15）", "通过测试的补丁约 **95%** 是错的，多是删掉功能"),
    ("香山处理器（VSpector）", "25 个 bug 中 **9 个**是 RTL 与参考模型错得一样，测试发现不了"),
], tsize=15, bsize=13, step=0.95)
vline(s, 6.45, 1.4, 5.9)
text(s, 6.7, 1.35, 6.0, 0.45, ["我们的例子：route B（基于开源 GPGPU-Sim）"], size=17, color=NAVY, bold=True)
text(s, 6.7, 1.85, 6.0, 0.6, ["AI 分别生成两个模块，各自逐拍比对全过；接起来，第 5051 拍不一致。真正原因：接口少了一条“本拍更新后的值”"],
     size=13, color=BODY)
rows = [["给 AI 的反馈", "会把 AI 引到哪"],
        ["测试结果：“第 5051 拍不一致”", "在报错处打补丁"],
        ["第一处分歧：“下游模块输入不一致”", "去改没错的下游模块"],
        ["按模块归因（ChatCPU）", "改后放进去的模块——其实两个都没错"],
        ["**带因果的 IR**：“这条同拍边在接口上没导出”", "**改接口**"]]
table(s, 6.7, 2.75, rows, [3.55, 2.45], size=12, rowh=0.6)
strip(s, "只靠测试，AI 被引向**报错的位置**；沿着指令与结构之间的因果，才能指向**出错的来源**")
notes(s, "左边：survey/27-xdomain-A、survey/25-gen-C。右边：route B 的整合错误（~/fml-routeb STATUS 阶段 2）。"
         "第 3 页的 CVA6 例子也说明同一点：分支挡住存储、加载挡不住分支，只看测试是推不出来的。")

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
strip(s, "硬件 = **指令在使用结构做事**；把这层关系写清楚，AI 才能在复杂处理器上写对")
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

# =============================================================== 7 use 1: a simulator paradigm for generation
s = page("用途一：提出一种方便 AI 生成的模拟器范式", T2)
text(s, 0.6, 1.25, 1.6, 0.4, ["起点"], size=13, color=SUB, bold=True)
text(s, 0.6, 1.5, 1.6, 0.3, ["route B"], size=11, color=SUB)
for k, (t, b) in enumerate([("现成模拟器", "GPGPU-Sim / CVA6 模型"), ("切出流水级", "FML 级规格"), ("AI 写 RTL", "逐级生成、逐拍比对")]):
    x = 2.3 + k * 2.6
    box(s, x, 1.15, 2.25, 0.62, t, b, line=MID, tsize=13, bsize=10)
    if k < 2:
        arrow(s, x + 2.27, 1.46, x + 2.58, 1.46)
text(s, 10.15, 1.2, 2.6, 0.6, ["依赖现成模拟器怎么写；复杂系统上因果藏在代码里"], size=11, color=SUB)
text(s, 0.6, 2.05, 1.6, 0.4, ["复杂系统"], size=13, color=RED, bold=True)
for k, (t, b) in enumerate([("因果 IR", "容器面 / 状态面 / 边"), ("按范式写的 FML 模拟器", "既能跑，又是规格"), ("AI 写 RTL", "照模型的时序写电路")]):
    x = 2.3 + k * 2.6
    box(s, x, 1.95, 2.25, 0.62, t, b, line=RED if k < 2 else NAVY, tsize=13, bsize=10)
    if k < 2:
        arrow(s, x + 2.27, 2.26, x + 2.58, 2.26, color=RED)
text(s, 10.15, 2.0, 2.6, 0.6, ["模拟器本身按“方便 AI 生成”来写"], size=11, color=RED)
hline(s, 0.6, 2.85, 12.7)
text(s, 0.6, 3.0, 6.3, 0.45, ["范式包括什么"], size=16, color=NAVY, bold=True)
numbered(s, 0.6, 3.45, 6.3, [
    ("按三类路径分开写", "固定功能路径：只写延迟 / 吞吐；非固定路径（访存）：事件模型；指令路径：按结构逐个写"),
    ("指令路径按 IR 组织", "每个结构一个模块，分容器面与状态面；状态分寄存器（下一拍）与本拍信号（本拍）"),
    ("因果不许藏在代码顺序里", "每处读都对应 IR 的一条边；检查与占用分开写"),
], tsize=14, bsize=12, step=0.85)
vline(s, 7.15, 3.05, 6.05)
text(s, 7.4, 3.0, 5.3, 3.2, [("为什么方便 AI 生成", {"bold": True, "color": NAVY, "size": 16}),
                            "复杂处理器的难点（指令与结构的关系）已经在模型里写清，AI 只需“翻译”",
                            "本拍 / 下一拍直接对应组合逻辑 / 触发器",
                            "模型可运行，生成的 RTL 能逐拍比对，出错能沿边归因",
                            ("先例要引用：PyMTL3、Cascade（周期模型细化成 RTL）；Kôika / BSV（直接编译）", {"color": SUB, "size": 12})],
     size=13, gap=5)
strip(s, "目的：让 AI 在**复杂处理器**上也能生成 RTL，并且**更快、更好**（待生成实验证明）")
notes(s, "路线的演变：v3（11-03）是“现成模拟器 → 按流水级切分 → AI 写 RTL”，route B 在 GPGPU-Sim 上就是这样做的。"
         "但现成模拟器怎么写由别人决定，复杂系统里指令与结构的因果藏在代码顺序里（CVA6 模型 19 条边中 13 条如此）。"
         "所以对复杂系统，我们提出一种确切的模拟器范式：用因果 IR 加 FML 来写模拟器，它既能跑、又能直接作为 AI 生成 RTL 的规格。"
         "三类路径的划分来自 11-03 的建模 spec；写法规则来自“可生成 RTL 的 FML 模型规范”初稿（18 条）。"
         "与先例的区别：PyMTL3 / Cascade 由人把周期模型细化成 RTL；Kôika / BSV 直接编译、不用 AI，也不做检查与归因。")

# =============================================================== 8 use 2: traceable verification -> AI checks its own RTL
s = page("用途二：可追溯的验证，让 AI 检查并修好自己生成的 RTL", T2)
loop = [("AI 生成 RTL", "照 FML 模型"), ("逐拍比对", "与模型对照"), ("因果归因", "哪个结构 · 哪一面\n哪条边 · 哪一拍 · 被谁挡"), ("AI 修正", "改对地方，或停下报告")]
for k, (t, b) in enumerate(loop):
    x = 0.6 + k * 3.1
    box(s, x, 1.35, 2.7, 1.05, t, b, line=RED if k == 2 else NAVY, tsize=15, bsize=11)
    if k < 3:
        arrow(s, x + 2.72, 1.87, x + 3.08, 1.87, color=NAVY)
arrow(s, 10.0, 2.4, 10.0, 2.65, color=MID); arrow(s, 10.0, 2.65, 5.0, 2.65, color=MID)
arrow(s, 5.0, 2.65, 5.0, 2.42, color=MID)
text(s, 6.2, 2.62, 3.0, 0.3, ["修完再比对，直到逐拍一致"], size=11, color=SUB, align=PP_ALIGN.CENTER)
rows = [["追到的来源", "AI 怎么做"],
        ["① 结构内部实现错 / ② 接口、同拍与寄存弄反", "修"],
        ["③ 打破了别人依赖的时序规矩", "修，或登记修改"],
        ["④ 规格或参考错 / ⑤ IR 漏了依赖 / ⑥ 追不下去", "**停下，报告给人**"]]
table(s, 0.6, 3.2, rows, [4.9, 1.9], size=13, rowh=0.62)
vline(s, 7.75, 3.25, 6.05)
text(s, 8.0, 3.15, 4.7, 3.0, [("期望效果", {"bold": True, "color": NAVY, "size": 16}),
                             "AI 不再只知道“错了”，而知道**错在哪、为什么**，能检查自己生成的 RTL",
                             "修正迭代更少，假修复（凑出“通过”）更少，该停时会停",
                             "从而**提升 AI 生成 RTL 的效果**",
                             ("衡量：有 / 无因果归因时，修正成功率、迭代次数、假修复率", {"color": SUB, "size": 12})],
     size=13, gap=6)
strip(s, "两个用途合成一个闭环：**范式让 AI 生成，因果让 AI 自查自纠**——共同提升复杂处理器上的生成效果")
notes(s, "用途二的落脚点不是“给人看的报告”，而是给 AI 的反馈：每次比对失败，都告诉 AI 哪个结构、哪一面、哪条边、哪一拍、被谁挡住。"
         "前三类 AI 自己修；后三类停下报告——规格错时让 AI 先试着修，它多半能凑出一个“通过”"
         "（ImpossibleBench：给“停下”出口后作弊从 54% 降到 9%）。"
         "衡量方法对应论文一 RQ1：四种反馈（只给测试结果 / 第一处分歧 / 按模块归因 / 因果归因）下，"
         "修正成功率、迭代次数、假修复率。理论归属：基于模型的一致性诊断（Reiter 1987）。")

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
        ("下一个平台", "CVA6 没有多请求方仲裁和 credit。下一个用 Vortex 还是其他 GPU 设计？")]):
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
