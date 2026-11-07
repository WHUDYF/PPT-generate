#!/usr/bin/env python3
"""Group meeting deck v2 (2026-11-07): causal structural IR for AI-generated pipeline RTL.

Changes from v1: two diagrams (CVA6 causal graph, a traced wait on a timeline),
fewer words per page, no internal jargon, a separate discussion page, speaker notes.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml.ns import qn

FONT = "Microsoft YaHei"
NAVY = RGBColor(0x1F, 0x3A, 0x5F)
BLUE = RGBColor(0x2E, 0x6F, 0xB5)
GREY = RGBColor(0x45, 0x4B, 0x55)
LIGHT = RGBColor(0xEE, 0xF3, 0xF9)
ORANGE = RGBColor(0xD9, 0x7A, 0x1E)
GREEN = RGBColor(0x2E, 0x8B, 0x57)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PALE = RGBColor(0xC9, 0xDA, 0xEE)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
W, H = prs.slide_width, prs.slide_height


def style(run, size, color=GREY, bold=False):
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


def text(slide, x, y, w, h, lines, size=20, color=GREY, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, gap=10):
    """lines: str | (str, level) | (str, level, opts). level -1 = no bullet."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, ln in enumerate(lines):
        if isinstance(ln, str):
            ln = (ln, 0, {})
        elif len(ln) == 2:
            ln = (ln[0], ln[1], {})
        s, lvl, opt = ln
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(gap)
        bullet = "" if lvl < 0 else ("● " if lvl == 0 else "– ")
        r = p.add_run()
        r.text = ("    " * max(lvl, 0)) + bullet + s
        style(r, opt.get("size", size - 3 * max(lvl, 0)), opt.get("color", color),
              opt.get("bold", bold))
    return tb


def box(slide, x, y, w, h, s, fill=LIGHT, fg=NAVY, size=18, sub=None, line=BLUE,
        shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sh = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = line
    sh.line.width = Pt(1.25)
    tf = sh.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for m in ("margin_left", "margin_right"):
        setattr(tf, m, Inches(0.06))
    for i, part in enumerate(s.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = part
        style(r, size if i == 0 else (sub or size - 4), fg, i == 0)
    return sh


def arrow_line(slide, x1, y1, x2, y2, color=BLUE, dashed=False, width=2.0):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1),
                                   Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    if dashed:
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    ln = c.line._get_or_add_ln()
    tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"})
    ln.append(tail)
    return c


def right_arrow(slide, x, y, w, h):
    a = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    a.fill.solid()
    a.fill.fore_color.rgb = BLUE
    a.line.fill.background()


def notes(slide, s):
    slide.notes_slide.notes_text_frame.text = s


def page(title, sub=None):
    s = prs.slides.add_slide(BLANK)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, Inches(0.12))
    bar.fill.solid(); bar.fill.fore_color.rgb = NAVY; bar.line.fill.background()
    text(s, 0.6, 0.32, 12, 0.8, [(title, -1)], size=30, color=NAVY, bold=True)
    if sub:
        text(s, 0.6, 1.02, 12, 0.5, [(sub, -1)], size=17, color=BLUE)
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(0.6), Inches(1.5),
                                Inches(12.7), Inches(1.5))
    ln.line.color.rgb = PALE; ln.line.width = Pt(1.5)
    text(s, 12.2, 7.0, 1, 0.4, [(str(len(prs.slides)), -1)], size=12, align=PP_ALIGN.RIGHT)
    return s


def table(slide, x, y, w, rows, colw, size=16, rowh=0.55):
    t = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w),
                               Inches(rowh * len(rows))).table
    for j, cw in enumerate(colw):
        t.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.text = ""
            c.fill.solid()
            c.fill.fore_color.rgb = NAVY if i == 0 else (LIGHT if i % 2 == 0 else WHITE)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            r = c.text_frame.paragraphs[0].add_run()
            r.text = val
            style(r, size, WHITE if i == 0 else GREY, i == 0)
    return t


def stat(slide, x, y, w, h, big, small):
    box(slide, x, y, w, h, f"{big}\n{small}", size=34, sub=15)


# ===================================================================== 1 title
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
text(s, 0.9, 2.2, 11.5, 1.2, [("让 AI 生成的流水线 RTL 真实可控", -1)], size=42, color=WHITE, bold=True)
text(s, 0.9, 3.35, 11.5, 1, [("带因果的结构 IR：从模拟器到 AI 生成 RTL", -1)], size=26, color=PALE)
text(s, 0.9, 5.3, 11.5, 0.8, [("组会 · 两周进展（10-24 至 11-07）", -1)], size=18, color=PALE)
notes(s, "这两周的工作围绕一个问题：AI 已经能写出能跑通测试的流水线 RTL，但写出来的东西不可控。"
         "我们想用一层带因果关系的结构 IR，把“错从哪里来”说清楚，并以此指导 AI 生成和修正 RTL。")

# ===================================================================== 2 outline
s = page("今天讲什么")
for i, (t, d) in enumerate([
        ("问题", "AI 写的 RTL 能通过测试，为什么还不够"),
        ("想法", "带因果的结构 IR：把“谁挡住了谁”写清楚"),
        ("实验", "在 CVA6 上从模拟器得到 IR，并验证它"),
        ("下一步", "从 IR 到 FML 模型，再到 AI 生成 RTL；想讨论的问题")]):
    y = 1.95 + i * 1.25
    box(s, 0.9, y, 2.4, 0.9, t, fill=NAVY, fg=WHITE, size=24)
    text(s, 3.65, y + 0.2, 9, 0.8, [(d, -1)], size=22)
notes(s, "四部分，大约 25 分钟。重点在第二、三部分。")

# ===================================================================== 3 problem
s = page("问题：AI 写的 RTL 能通过测试，但不可控",
         "curryGPU 的一个子核（约 10 万行 Verilog，大部分由 AI 生成）上的真实情况")
table(s, 0.6, 1.85, 7.6, [
    ["测试的表现", "真正的问题"],
    ["端到端测试通过，改一个参数后部分用例出错", "有一条依赖从没写下来（同一 warp 至少隔 2 拍发射）"],
    ["两个模块各自全对，接起来出错", "接口少了“本拍更新后的值”"],
    ["验收脚本判通过", "规格本身是错的，来自 AI 写的核实报告"],
    ["功能全对，慢了 6–7%", "某条路径从 6 拍变成 9 拍，人找了几轮"],
], [3.6, 4.0], size=15, rowh=0.8)
stat(s, 8.7, 1.85, 4.1, 1.45, "约 95%", "早期自动修复中，通过测试的补丁是错的")
stat(s, 8.7, 3.45, 4.1, 1.45, "约 11%", "SWE-bench 上 AI“已解决”的补丁不正确")
stat(s, 8.7, 5.05, 4.1, 1.45, "54–76%", "测试与规格矛盾时，GPT-5 作弊的比例")
notes(s, "左边是我们自己的案例：测试通过了，但真正的问题在依赖、接口、规格或时序上，测试看不到。"
         "右边是别的领域的数字：Qi 等 ISSTA'15；Wang 等 ICSE'26；ImpossibleBench（Zhong 等 2025）。"
         "ImpossibleBench 还发现，允许 AI 说“这个任务有问题，交给人”，作弊率从 54% 降到 9%。"
         "结论：只靠测试结果去修，AI 容易在报错的地方打补丁，甚至去改测试。")

# ===================================================================== 4 core idea
s = page("核心想法：硬件就是“指令在使用结构做事”")
box(s, 0.7, 1.9, 3.8, 1.7, "结构\n有限的位置：满了别人要等\n存着的信息：影响后面的决定", size=22, sub=16)
box(s, 4.8, 1.9, 3.8, 1.7, "动作\n每拍按顺序：提交 → 执行 → 发射 → 取指", size=22, sub=16)
box(s, 8.9, 1.9, 3.8, 1.7, "指令\n沿着路线依次使用各个结构", size=22, sub=16)
text(s, 0.7, 4.0, 12, 3, [
    "因果边：一个动作通过某个结构影响另一个动作，并标明“本拍就看到”还是“下一拍才看到”",
    "每类指令怎样使用一个结构，用五项规矩写清：几个位置、占多久、在哪里判断、判断时知道什么、多人抢时给谁",
    "目标：出错时能沿着这张图，从“报错的地方”追到“出错的地方”",
], size=20)
notes(s, "模拟器通常按功能组织代码，“谁会挡住谁、在哪一拍看到”藏在函数的调用顺序里。"
         "我们把它显式写出来。同一个结构可以既有“位置”又存“信息”，比如 scoreboard："
         "最多 8 条在途指令（位置），同时记着每个寄存器还有谁没写完（信息）。"
         "五项规矩足以描述常见的预约表、令牌（credit）、容量、仲裁，不需要为每种单独发明写法。")

# ===================================================================== 5 timeline example
s = page("一个例子：一次等待是怎么被追出来的",
         "单发射 CPU：一条乘法后面紧跟一条要用它结果的加法")
cols = ["第 t 拍", "第 t+1 拍", "第 t+2 拍", "第 t+3 拍", "第 t+4 拍"]
rows = [
    ("mul a0, s0, s1", ["发射", "执行中", "算完", "提交", ""]),
    ("add a1, a0, s2", ["", "等待", "发射", "算完", "提交"]),
    ("ALU 是否被占", ["", "被乘法占着", "", "", ""]),
    ("a0 准备好了吗", ["", "没有", "本拍算完即可用", "", ""]),
]
x0, y0, cw, rh, lw = 3.2, 1.8, 1.9, 0.62, 2.5
for j, c in enumerate(cols):
    box(s, x0 + j * cw, y0, cw - 0.08, 0.55, c, fill=NAVY, fg=WHITE, size=16, line=NAVY,
        shape=MSO_SHAPE.RECTANGLE)
for i, (lab, cells) in enumerate(rows):
    y = y0 + 0.65 + i * rh
    text(s, 0.6, y + 0.12, lw, rh, [(lab, -1)], size=16, color=NAVY, bold=True)
    for j, v in enumerate(cells):
        if not v:
            continue
        hot = v in ("等待", "被乘法占着", "没有")
        box(s, x0 + j * cw, y + 0.05, cw - 0.08, rh - 0.12, v, size=15,
            fill=RGBColor(0xFD, 0xEB, 0xD8) if hot else LIGHT, fg=ORANGE if hot else NAVY,
            line=ORANGE if hot else BLUE, shape=MSO_SHAPE.RECTANGLE)
text(s, 0.6, 5.2, 12.2, 2.2, [
    "第 t+1 拍加法没发出去，记录下两个原因，每个都写明“被谁挡住”：",
    ("ALU 被乘法占着（乘法和 ALU 共用写回口，乘法发射后下一拍 ALU 忙）", 1),
    ("a0 还没准备好，写它的是那条乘法", 1),
    "第 t+2 拍乘法算完，加法同一拍就能用上结果——因为模型里“执行”排在“发射”前面",
], size=17, gap=4)
notes(s, "这是 CVA6 性能模型里真实的行为，自检时每一次等待都会这样记录。"
         "关键点：加法的等待有两个原因，分别对应 IR 里的两条因果边。"
         "第三条要点里“本拍算完、本拍就能用”，模型代码里没有任何一句话这样写，只是函数调用顺序带出来的。"
         "这种“只由调用顺序决定”的关系，就是以后拿真实 RTL 核对时首先要查的地方。")

# ===================================================================== 6 causal graph
s = page("IR 长什么样：CVA6 控制通路的因果图（局部）",
         "上排是每拍的动作，下排是结构；实线 = 本拍就看到，虚线 = 下一拍才看到")
acts = {"提交": 0.7, "执行": 3.5, "发射": 6.3, "取指": 10.4}
for name, x in acts.items():
    box(s, x, 1.85, 2.3 if name != "发射" else 3.4, 0.85, name, fill=NAVY, fg=WHITE, size=22)
issue_cx = 6.3 + 1.7
sts = [("scoreboard\n位置 + 寄存器是否准备好", 0.5), ("分支历史表\n预测下一条", 3.05),
       ("功能单元\nALU / 乘除 / 访存", 5.6), ("指令队列\n还有几个字节", 8.15), ("上一条发射的指令\n用来判断预测对错", 10.7)]
yb = 4.55
for lab, x in sts:
    box(s, x, yb, 2.3, 1.15, lab, size=17, sub=13)
top, bot = 2.7, yb
# writers -> structures
arrow_line(s, 1.85, top, 1.65, bot)                     # 提交 -> scoreboard
arrow_line(s, 4.65, top, 1.95, bot)                     # 执行 -> scoreboard (done)
arrow_line(s, 1.55, top, 4.0, bot)                      # 提交 -> BHT
arrow_line(s, 11.55, top, 9.4, bot, color=ORANGE, dashed=True)   # 取指 -> 指令队列 (下一拍)
arrow_line(s, 7.2, top, 6.75, bot)                      # 发射 -> 功能单元
arrow_line(s, 8.6, top, 11.85, bot)                     # 发射 -> 上一条发射
# structures -> issue
for x in (1.85, 4.3, 6.95, 9.1, 11.6):
    arrow_line(s, x + 0.2, bot, issue_cx + (x - 6.5) * 0.12, top, color=GREEN, width=1.5)
text(s, 0.6, 5.95, 12.2, 1.2, [
    ("CVA6 的完整 IR：14 个结构、19 条因果边、10 种等待原因、8 类指令；每一条都标着模型代码的行号", -1),
    ("19 条边里有 13 条“只由调用顺序或端口先后决定”，没人明确说过是设计意图", -1, {"color": ORANGE}),
], size=17, gap=4)
notes(s, "蓝线：动作写结构；绿线：发射读这些结构做判断；橙色虚线：取指的字节要到下一拍才能用。"
         "举几条：提交腾出 scoreboard 位置，本拍就能发射新指令；执行算完的结果，本拍就能前递；"
         "提交时更新分支历史表，本拍发射的预测就用上了新值。"
         "这张图只画了一部分，完整的 IR 是一个 Python 文件，带两张清单说明每个结构和每个停止条件是怎么从模型代码里数出来的。")

# ===================================================================== 7 attribution
s = page("出错时：归到哪一类，AI 是“修”还是“报”",
         "理论上属于“基于模型的一致性诊断”（Reiter 1987；de Kleer & Williams 1987）")
table(s, 0.6, 1.85, 8.0, [
    ["归因结果", "AI 怎么做"],
    ["① 某个部件内部写错了", "修"],
    ["② 部件之间的接口或连线错了", "修"],
    ["③ 改动打破了别人依赖的时序规矩", "修，或登记规矩的修改"],
    ["④ 规格或参考本身错了", "停下，报告给人"],
    ["⑤ IR 漏画了一条依赖", "停下，报告给人"],
    ["⑥ 追不下去", "停下，报告给人"],
], [5.0, 3.0], size=17, rowh=0.68)
text(s, 9.0, 1.85, 3.9, 5, [
    ("原则", -1, {"bold": True, "color": NAVY, "size": 22}),
    "不是“修不动了才报”，而是“看出不该修就报”",
    "规格错时让 AI 先试着修，它多半能凑出一个“通过”",
], size=18)
notes(s, "前三类问题在 RTL 上，AI 去修；后三类问题在规格、参考或 IR 本身，AI 应该停下。"
         "对比：Zeller 的因果链方法没有内部规格，要靠大量重跑试验，GCC 上一次诊断约 12 小时；"
         "基于 SAT 的硬件调试把期望输出当成一定正确，规格错时会把错误怪到 RTL 头上。"
         "我们把连线和规格条目也当作“可能出错的部件”，这是和经典诊断理论的主要区别。")

# ===================================================================== 8 main line
s = page("主线：从模拟器到 AI 生成 RTL")
labels = ["模拟器\n周期级性能模型", "因果 IR\n经过验证", "FML 模型\n按 IR 组织", "AI 生成 RTL", "逐拍比对\n出错时归因"]
x0, bw, gap = 0.5, 2.15, 0.42
for i, lb in enumerate(labels):
    x = x0 + i * (bw + gap)
    hl = i in (1, 2)
    box(s, x, 2.0, bw, 1.35, lb, fill=NAVY if hl else LIGHT, fg=WHITE if hl else NAVY, size=19, sub=14)
    if i < len(labels) - 1:
        right_arrow(s, x + bw + 0.06, 2.52, gap - 0.12, 0.3)
text(s, 0.6, 3.9, 12.2, 3.2, [
    "一句话：时序由模型规定，实现由 AI 完成，正确性由因果 IR 检查",
    "FML 模型里状态分两种：寄存器（下一拍才看到）和本拍信号（本拍就看到），正好对应 RTL 的触发器和组合逻辑",
    ("和 ChatCPU、HINT 的区别：周期级的因果约定、与模拟器不同源的自检、按因果边归因", 0, {"color": NAVY}),
], size=19)
notes(s, "FML 是合作者的周期级建模框架，用 Rust 写，每次读别的模块的状态都要声明读的是本拍值还是上一拍的值。"
         "ChatCPU（DAC'24）用周期精确模型让 LLM 逐模块生成 CPU，但时序只有每个模块一个延迟，"
         "参考模型和 RTL 来自同一份规格，出错时归到“新换进来的模块”。"
         "HINT 在规格和 RTL 之间加了可执行中间层，但明确不做周期精确，报错只到“哪一层”。")

# ===================================================================== 9 papers
s = page("计划：三篇论文")
table(s, 0.6, 1.85, 12.1, [
    ["", "论文一", "论文二", "论文三（新）"],
    ["问的问题", "AI 生成的 RTL 对不对、错从哪来", "IR 本身缺东西、出错时怎么办", "慢在哪里、改一处会影响谁"],
    ["核心", "因果 IR + IR 自检 + 归因；AI 生成作为主线", "谁来补 IR、按来源决定信多少", "沿带时序的因果边找瓶颈"],
    ["状态", "IR 验证完成，FML 模型设计中", "已有草稿，等论文一的数据", "文献检索计划待定"],
], [1.6, 3.7, 3.4, 3.4], size=16, rowh=0.95)
text(s, 0.6, 5.9, 12, 1.2, [
    "分界：论文一只要求“发现 IR 有问题并停下报告”；发现之后谁来修、信谁，交给论文二",
], size=18)
notes(s, "论文三的动机来自 curryGPU 的两个性能案例：WARPSYNC 分叉从 6 拍变 9 拍，慢 6–7%；"
         "访存响应那一拍的忙信号挡住所有发射，慢 8.5%。功能都对，原因很难找。")

# ===================================================================== 10 platforms
s = page("实验平台")
box(s, 0.7, 1.9, 5.8, 1.0, "CVA6：第一个实验平台", fill=NAVY, fg=WHITE, size=22)
text(s, 0.7, 3.05, 5.8, 3.5, [
    "开源 RISC-V 核，官方带一个 Python 周期级性能模型（约 670 行）和可综合 RTL",
    "能演示“从模拟器出发”的完整链条",
], size=18)
box(s, 6.9, 1.9, 5.8, 1.0, "Hazard3：受控注入平台", fill=LIGHT, size=22)
text(s, 6.9, 3.05, 5.8, 3.5, [
    "小 RISC-V 核，没有周期级模拟器，IR 从 RTL 抄出",
    "用来故意注入错误，测归因准不准",
], size=18)
text(s, 0.7, 5.3, 12, 1.8, [
    ("FML 版模型分两条线：一条不看 IR、独立移植，用来检验 IR；之后再按 IR 改造成生成 RTL 用的规格", -1,
     {"color": NAVY}),
], size=18)
notes(s, "Hazard3 的硬伤是没有周期级模拟器，所以“从模拟器生成 IR”这半条链在它上面演示不了。"
         "两条 FML 线：独立线现在完成了指令解码（110 万条指令和 Python 版逐条一致），正在写时序模型；"
         "它不看我们的 IR，自己决定每处同拍还是寄存，最后和 IR 对照，分歧就是模型里的隐含假设。")

# ===================================================================== 11 exp1
s = page("实验 1：CVA6 的性能模型和 RTL 差多少",
         "CoreMark 在 Verilator 上跑通；逐条指令比较“提交间隔”")
stat(s, 0.8, 1.9, 5.5, 1.6, "84.9%", "超标量配置：提交间隔相同的指令比例")
stat(s, 7.0, 1.9, 5.5, 1.6, "82.6%", "单发射配置：提交间隔相同的指令比例")
text(s, 0.8, 3.9, 12, 3, [
    "论文报告 99.2%，我们没复现：配置和模型的假设对不上（ALU 旁路、真实 cache、论文的配置已过时）",
    "这十几个百分点的分歧，正是以后要追溯的对象：模型和 RTL 在哪里分开、为什么",
    ("决定：先只看模型生成 IR，RTL 留作之后的独立核对，避免“自己检查自己”", 0, {"color": ORANGE}),
], size=19)
notes(s, "顺带发现两件事：CVA6 官方的 CoreMark 脚本在 Verilator 下没有真正关掉调试（参数没拆开），"
         "有调试功能的配置整个运行中被反复拉进调试 ROM，多算了约 7 万拍；性能模型不认识 fence 指令。")

# ===================================================================== 12 exp2 method
s = page("实验 2：怎样确认 IR 画对了")
for i, (t, d) in enumerate([
        ("没漏画", "模型里每个会变的状态、每处能让指令停下的代码，都在 IR 里有位置"),
        ("能解释", "模型运行中每一次等待，都能在 IR 里找到原因和“被谁挡住”"),
        ("被检验过", "IR 的每条边都真的被触发过；只用 IR 的规则能预测模型的行为")]):
    box(s, 0.6 + i * 4.2, 1.9, 3.9, 1.9, f"{t}\n{d}", size=22, sub=15)
text(s, 0.6, 4.2, 12.2, 2.8, [
    "测试程序直接用脚本生成（模型只需要“地址 + 指令编码”）：单条指令、两两组合、把资源压满",
    "每个程序在 32 组参数下跑：单 / 双发射、单 / 双提交、前递开关、重命名开关、scoreboard 大小",
    "“预测器”：不跑模型，只按 IR 写的规则推算每条指令哪一拍发射，再和模型比",
], size=18)
notes(s, "可以把 IR 看成一张图：点是结构和动作，线是因果边。要检查的不只是点和线在不在，"
         "还有线上的标注（本拍还是下一拍）对不对，以及两条线碰到一起时 IR 的说法还对不对。"
         "后者这次真的发现了问题，见后面。")

# ===================================================================== 13 exp2 results
s = page("实验 2 结果：只用 IR 的规则，就能推出模型的每一拍")
stat(s, 0.6, 1.85, 2.9, 1.8, "1,312", "次运行（89 个测试程序 × 参数组合）")
stat(s, 3.75, 1.85, 2.9, 1.8, "0", "次行为不一致或解释不了的等待")
stat(s, 6.9, 1.85, 2.9, 1.8, "19 / 19", "条因果边都被触发过")
stat(s, 10.05, 1.85, 2.7, 1.8, "100%", "12.5 万条指令的发射拍全部推对")
text(s, 0.6, 4.1, 12.2, 2.8, [
    "预测准确率：93.4% → 99.3% → 100%，每一步都对应一次 IR 的修正",
    "CoreMark（两个配置，各约 55 万条指令）同样全部通过",
], size=20)
notes(s, "预测器是一个 IR 的解释器，完全不调用模型。它能逐条推对，说明 IR 写下的规则足以推出模型的行为，"
         "而不只是事后能解释。两两组合 5,216 种情况全部推对。")

# ===================================================================== 14 corrections
s = page("实验 2：IR 被自己的检查纠正了 7 次", "每一次都有证据和记录；以下是最有代表性的三次")
table(s, 0.6, 1.85, 12.1, [
    ["发现了什么", "由哪种检查发现"],
    ["分支预测错误后，每次重新尝试都会重新预测；中途分支历史被更新，惩罚可以短于 6 拍", "专门构造的测试第一次触发了“同拍写、同拍读分支历史”"],
    ["指令队列取走字节后要按下一条指令的地址对齐，IR 原来没写清", "预测器：307 个预测错误"],
    ["每类指令发射前只“检查”一个单元，却“占用”好几个：分支挡得住后面的存储，存储挡不住后面的分支", "预测器：最后 38 个预测错误"],
], [7.6, 4.5], size=16, rowh=1.0)
text(s, 0.6, 6.05, 12.2, 1.0, [
    ("教训：“每一步都能解释”不等于“IR 的说法是对的”；检查代码本身也查出 4 处缺陷", -1, {"color": ORANGE}),
], size=18)
notes(s, "第一条：原来 IR 写“预测错误要等 6 拍”，默认了等待期间预测不变。单看每条边都对，两条边碰在一起才暴露。"
         "第三条：这导致 IR 的写法升级，把“检查”和“占用”分成两栏——单向的挡住关系在真实硬件里很常见。"
         "检查代码的 4 处缺陷包括漏计数、以及双发射时记下了虚假的等待原因，之后要求记下的每条原因都必须真的成立。")

# ===================================================================== 15 next
s = page("下一步：按 IR 设计 FML 模型，再让 AI 生成 RTL")
text(s, 0.6, 1.85, 6.2, 5, [
    ("“能生成 RTL 的 FML 模型”规范（初稿）", -1, {"bold": True, "color": NAVY, "size": 21}),
    "IR 的每个结构对应一个模块",
    "状态分寄存器和本拍信号",
    "每处读都对应 IR 的一条边，双向检查",
    "隐含的顺序一律写成显式信号",
    "模型自带“被谁挡住”的记录",
], size=18)
text(s, 7.0, 1.85, 5.9, 5, [
    ("接下来", -1, {"bold": True, "color": NAVY, "size": 21}),
    "FML 模型设计已完成初稿，正在复核",
    "独立线完成后，对照它和 IR，再按规范改造",
    "用官方 RTL 核对 IR（先查 13 条隐含顺序的边）",
    "在 CVA6 控制通路上做第一次 AI 生成实验",
], size=18)
notes(s, "设计初稿：13 个模块（10 个对应硬件），13 条隐含顺序的边中 3 条改为读寄存器，"
         "10 条改为显式本拍信号，估计新增约 20 个信号。"
         "生成实验的对照：给 AI“带因果 IR 的 FML 模型”与只给 Python 模型或文字规格，比较成功率、迭代次数和假修复。")

# ===================================================================== 16 discussion
s = page("想和大家讨论的问题")
for i, (q, d) in enumerate([
        ("1. 为什么不直接编译？",
         "FML 已写清每拍时序，审稿人会问为什么不像 BSV、Kôika 那样直接编译成 RTL。我们的回答：模型有大量抽象（执行单元只是计数器、没有数据通路），同一时序有多种电路实现，重点在检查和归因。够不够？"),
        ("2. 验证怎样才算充分？",
         "计划四层：生成的 RTL 和模型逐拍一致；有无因果 IR 时 AI 修正的成功率；注入错误的归因准确率；与官方实现比面积和时序。还缺什么？"),
        ("3. 平台够不够？",
         "CVA6 是顺序发射 CPU，没有多请求方仲裁和 credit。打算再用 GPU 类的 Vortex 或 curryGPU 验证，优先哪个？")]):
    y = 1.85 + i * 1.75
    box(s, 0.6, y, 3.4, 1.5, q, fill=NAVY, fg=WHITE, size=19)
    text(s, 4.25, y + 0.05, 8.6, 1.5, [(d, -1)], size=17, anchor=MSO_ANCHOR.MIDDLE)
notes(s, "这三个问题是目前最没把握的地方，希望听大家的意见。")

out = "/home/dyf/PPT-generate/presentations/group_meeting_20261106/group_meeting_20261106.pptx"
prs.save(out)
print(out, len(prs.slides), "slides")
