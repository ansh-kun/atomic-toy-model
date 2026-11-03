from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

NAVY = RGBColor(0x1F, 0x3B, 0x57)
INK = RGBColor(0x22, 0x22, 0x22)
SLATE = RGBColor(0x4A, 0x53, 0x61)
ACCENT = RGBColor(0xB0, 0x56, 0x1C)
LIGHT_BG = RGBColor(0xF6, 0xF4, 0xEE)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def add_slide():
    return prs.slides.add_slide(BLANK)


def box(slide, l, t, w, h, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf


def para(tf, text, size=18, bold=False, color=INK, first=False, before=0, after=0,
         align=None, line=1.1):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.space_before = Pt(before)
    p.space_after = Pt(after)
    p.line_spacing = line
    if align:
        p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = "Calibri"
    return p


def bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def header(slide, title, subtitle=None):
    bg(slide, RGBColor(0xFF, 0xFF, 0xFF))
    tf = box(slide, 0.6, 0.35, 12.1, 0.9)
    para(tf, title, size=32, bold=True, color=NAVY, first=True)
    if subtitle:
        tf2 = box(slide, 0.6, 1.05, 12.1, 0.4)
        para(tf2, subtitle, size=14, color=SLATE, first=True)
    line = slide.shapes.add_connector(1, Inches(0.6), Inches(1.5), Inches(12.73), Inches(1.5))
    line.line.color.rgb = RGBColor(0xDD, 0xDD, 0xDD)
    line.line.width = Pt(1)


# ---------------------------------------------------------------- slide 1: title
s = add_slide()
bg(s, NAVY)
tf = box(s, 1.0, 2.2, 11.3, 1.3, anchor=MSO_ANCHOR.MIDDLE)
para(tf, "Atomic Toy Model", size=48, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), first=True)
tf = box(s, 1.0, 3.35, 11.3, 0.6)
para(tf, "Fundamentals of Scientific Computing — Computational Thinking Project",
     size=18, color=RGBColor(0xDD, 0xE2, 0xEA), first=True)
tf = box(s, 1.0, 3.95, 11.3, 0.5)
para(tf, "Instructors: Prof. Anuj Goyal · Prof. Saswata Bhattacharyya", size=14,
     color=RGBColor(0xB8, 0xC2, 0xCF), first=True)
tf = box(s, 1.0, 5.4, 11.3, 1.6)
para(tf, "Group 8", size=16, bold=True, color=ACCENT, first=True, after=6)
for name, roll in [("Ansh Dadhore", "CO26BTECH11003"),
                    ("Deepak Kumar Singhadiya", "CO26BTECH11005"),
                    ("Purushottam Narayan", "MS26BTECH11027"),
                    ("Sajal Bajaj", "MS26BTECH11029"),
                    ("Boyanapelli Abhiram Rao", "CO26BTECH11004")]:
    para(tf, f"{name}   ·   {roll}", size=13, color=RGBColor(0xEE, 0xEE, 0xEE), line=1.3)

# ---------------------------------------------------------------- slide 2: problem + goal
s = add_slide()
header(s, "What we're building", "The assignment, in plain terms")
tf = box(s, 0.6, 1.85, 12.1, 1.0)
para(tf, "A toy particle simulator — particles in a box, connected by spring-like forces, "
         "bouncing off walls. We have to prove it's correct, fast, and improved — not just "
         "that it runs.", size=20, bold=True, color=INK, first=True, line=1.25)

tf = box(s, 0.6, 3.1, 5.6, 3.3)
para(tf, "The three things we're judged on", size=16, bold=True, color=NAVY, first=True, after=8)
for label, desc in [("Accurate", "verified with real numbers, not claims"),
                     ("Efficient", "measured timing, memory, scaling"),
                     ("Innovative", "one real improvement, proven with data")]:
    para(tf, label, size=15, bold=True, color=ACCENT, before=10)
    para(tf, desc, size=13, color=SLATE)

tf = box(s, 6.7, 3.1, 6.0, 3.3)
para(tf, "What we submit", size=16, bold=True, color=NAVY, first=True, after=8)
for item in ["Report (PDF)", "Full code + data (reproducible)",
             "Animation (GIF/MP4)", "15–20 min video presentation",
             "All plots, tables, quantitative evidence"]:
    para(tf, "•  " + item, size=13.5, color=INK, before=6)

# ---------------------------------------------------------------- slide 3: task plan (grid)
s = add_slide()
header(s, "Project plan — 9 tasks", "What each task needs and who owns it")

tasks = [
    ("1", "Baseline + verification", "distances, neighbors, forces ~0", "Ansh", "15"),
    ("2", "Animation", "500+ steps, watch for bugs", "Deepak", "10"),
    ("3", "Energy & timestep", "K, U, E_total vs dt", "Purushottam", "15"),
    ("4", "Dissipation", "drag force, relaxation", "Sajal", "10"),
    ("5", "Precision", "float32 vs float64", "Deepak", "10"),
    ("6", "Efficiency", "loop vs NumPy vs C, speedup", "Abhiram", "15"),
    ("7", "Memory & scaling", "when does it break?", "Purushottam", "—"),
    ("8", "Innovation", "one real upgrade, proven", "Sajal", "15"),
    ("9", "Final recommendation", "best settings, justified", "Abhiram", "—"),
]

cols = 3
cw, ch = 3.95, 1.55
gx, gy = 0.18, 0.18
x0, y0 = 0.6, 1.85
for i, (num, title, detail, owner, marks) in enumerate(tasks):
    r, c = divmod(i, cols)
    x = x0 + c * (cw + gx)
    y = y0 + r * (ch + gy)
    card = s.shapes.add_shape(1, Inches(x), Inches(y), Inches(cw), Inches(ch))
    card.fill.solid()
    card.fill.fore_color.rgb = LIGHT_BG
    card.line.color.rgb = RGBColor(0xDD, 0xD7, 0xC8)
    card.line.width = Pt(0.75)
    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.18)
    tf.margin_top = tf.margin_bottom = Inches(0.12)
    para(tf, f"Task {num} · {title}", size=14, bold=True, color=NAVY, first=True, after=2)
    para(tf, detail, size=11.5, color=SLATE, after=6)
    tail = f"{owner}" if marks == "—" else f"{owner}  ·  {marks} marks"
    para(tf, tail, size=11, bold=True, color=ACCENT)

# ---------------------------------------------------------------- slide 4: deliverables
s = add_slide()
header(s, "Deliverables", "What goes in the submission folder")

tf = box(s, 0.6, 1.95, 11.5, 4.5)
para(tf, "•  README (team, roles, AI usage)", size=16, color=INK, first=True, before=0, line=1.3)
for item in ["Flowchart + mind map (project plan)",
             "Source code + test code + visualization code",
             "Animation / movies produced",
             "Report: Word/LaTeX + PDF with plots and results",
             "5 video files, one per member",
             "Prompts & recorded AI sessions"]:
    para(tf, "•  " + item, size=16, color=INK, before=14, line=1.3)

prs.save("/Users/ansh/atomic_toy_model/Atomic-Toy-Model-Project-Plan.pptx")
print("saved")
