"""
Builds REPORT.docx - same content as REPORT.html/REPORT.pdf, as an editable
Word document (the assignment asks for Word/LaTeX + PDF, not just PDF).
Uses python-docx's native tables, so none of the LibreOffice HTML table
width bugs we hit earlier apply here.
"""

import pathlib
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT = pathlib.Path(__file__).parent
doc = Document()

# ---- base style ----
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)


def h1(text):
    doc.add_heading(text, level=1)


def h2(text):
    doc.add_heading(text, level=2)


def p(text, bold=False, italic=False, size=11):
    para = doc.add_paragraph()
    run = para.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    return para


def bullets(items):
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def img(path, width_in=6.0):
    doc.add_picture(str(ROOT / path), width=Inches(width_in))


def table(rows, header=True):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Light Grid Accent 1"
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            t.cell(i, j).text = str(cell)
            if i == 0 and header:
                for run in t.cell(i, j).paragraphs[0].runs:
                    run.bold = True
    doc.add_paragraph()
    return t


# ---------------------------------------------------------------- title
title = doc.add_heading("Atomic Toy Model", level=0)
p("Fundamentals of Scientific Computing — Computational Thinking Project")
p("Instructors: Prof. Anuj Goyal, Prof. Saswata Bhattacharyya")
p("Group 8")
doc.add_paragraph()

table([
    ["Name", "Roll Number", "Responsibility"],
    ["Ansh Dadhore", "CO26BTECH11003", "Baseline simulator + verification (Task 1)"],
    ["Deepak Kumar Singhadiya", "CO26BTECH11005", "Animation (Task 2), precision study (Task 5)"],
    ["Purushottam Narayan", "MS26BTECH11027", "Energy/timestep (Task 3), memory/scaling (Task 7)"],
    ["Sajal Bajaj", "MS26BTECH11029", "Dissipation (Task 4), innovation (Task 8)"],
    ["Boyanapelli Abhiram Rao", "CO26BTECH11004", "Efficiency (Task 6), final rec. (Task 9), report"],
])

# ---------------------------------------------------------------- 1
h1("1. Model description, assumptions, governing equations")
p("A 2D toy particle system: N particles in a square box of side L, connected to every "
  "other particle within a cutoff radius r_c by a Hookean (spring-like) pair force, and "
  "bouncing elastically off the box walls.")
bullets([
    "Pair force: F_ij = -k (r_ij - r0), directed along the line joining particles i and j, "
    "applied only when r_ij < r_c and i ≠ j.",
    "Potential energy: U_ij = 0.5 k (r_ij - r0)^2",
    "Kinetic energy: K = 0.5 Σ m v^2",
    "Wall handling: elastic reflection — the velocity component normal to a wall flips "
    "sign, position is clamped inside [0, L].",
    "Integration: velocity-Verlet (half-kick, drift, recompute force, half-kick), unless "
    "otherwise noted (Task 3 also tests plain Euler for comparison).",
    "Assumptions: all particles have equal mass (m=1); the pair interaction is the only "
    "internal force; the box walls are the only external influence.",
])
p("Baseline parameters used throughout unless a task is explicitly varying one of them: "
  "N=16, L=10.0, r_c=3.0, k=1.5, r0=2.5, dt=0.005, mass=1.0.", italic=True, size=10)

# ---------------------------------------------------------------- 2
h1("2. Task 1 — Baseline simulator and verification")
p("Implementation: sim.py / core.py. Five required numerical checks, all run against the "
  "live simulation output rather than assumed:")
table([
    ["Check", "Result"],
    ["Distance matrix symmetry error", "0.0 (exact)"],
    ["Max diagonal distance", "0.0 (exact)"],
    ["Any particle its own neighbor?", "False"],
    ["All particles inside the box?", "True, every step"],
    ["Norm of total internal force", "~5e-16 (machine precision, i.e. ≈ 0)"],
])

# ---------------------------------------------------------------- 3
h1("3. Task 2 — Trajectory animation and diagnostics")
p("16 particles, 500 steps (task2_animation.gif, snapshots below). Diagnostics computed "
  "directly from the stored trajectory, not eyeballed:")
bullets([
    "No particle ever left the box.",
    "No particle got stuck at a wall for >80% of the run.",
    "No frame-to-frame jump bigger than 10x the median step size (median step = 0.0039 "
    "units) — no instability.",
    "Mean pairwise distance went from 4.46 to 5.13 (r0=2.5) — particles spread out, not "
    "an unexpected clustering collapse.",
])
img("task2_snapshots.png")

# ---------------------------------------------------------------- 4
h1("4. Task 3 — Energy conservation and timestep accuracy")
img("task3_energy_vs_dt.png", width_in=6.0)
table([
    ["dt", "steps", "max relative drift eps_E"],
    ["0.05", "50", "8.07%"],
    ["0.02", "125", "6.94%"],
    ["0.01", "250", "5.41%"],
    ["0.005", "500", "5.43%"],
])
p("Largest defensible dt (10% drift threshold): 0.05, though drift keeps improving down to "
  "dt=0.01 before flattening out, so 0.01 is the practical sweet spot (see Task 9).", bold=True)
img("task3_euler_vs_verlet.png", width_in=5.0)
p("At the same dt=0.02: Euler drifted 10.61%, velocity-Verlet drifted 6.94% — Verlet is "
  "clearly the better integrator at equal cost.")

# ---------------------------------------------------------------- 5
h1("5. Task 4 — Dissipation and relaxation")
p("Drag force F = -γv added to the spring force. Relaxation criterion: average particle "
  "speed must stay below 0.01 for the rest of the run, not just momentarily.")
img("task4_dissipation.png")
table([
    ["gamma", "Relaxed by t=20?", "decay tau", "E_final"],
    ["0.0", "No (conservative)", "~269", "15.69"],
    ["0.05", "No", "~14.5", "4.90"],
    ["0.1", "No", "~8.35", "1.81"],
    ["0.5", "Yes, at t=19.02", "~2.08", "~0.00"],
])
p("Answer: relaxation time decreases monotonically as gamma increases (tau drops from ~269 "
  "to ~2 across the tested range) — more drag relaxes the system strictly faster, and only "
  "strong enough damping (gamma=0.5 here) fully stops the system within an accessible "
  "simulation time.")

# ---------------------------------------------------------------- 6
h1("6. Task 5 — Numerical precision: float32 vs float64")
img("task5_precision.png")
table([
    ["dtype", "memory", "median time", "max drift"],
    ["float32", "256 bytes", "17.35 ms", "5.43%"],
    ["float64", "512 bytes", "16.84 ms", "5.43%"],
])
p("Memory ratio float64/float32 = 2.00x exactly, as expected. Final-position relative "
  "difference eps_pos = 6.6e-7 — negligible. At this small N (16), float32 showed no speed "
  "advantage (0.97x) because Python/NumPy call overhead dominates, not raw arithmetic — the "
  "speed benefit of float32 only shows up at the larger N tested in Task 6/7, where memory "
  "bandwidth is the bottleneck.")
p("Answer: yes, float32 is accurate enough for this problem; its computational advantage is "
  "purely in memory footprint at this scale, and would extend to speed at larger N.", bold=True)

# ---------------------------------------------------------------- 7
h1("7. Task 6 — Computational efficiency and scaling")
img("task6_efficiency.png")
table([
    ["N", "loop (s)", "numpy (s)", "C (s)", "numpy speedup", "C speedup"],
    ["50", "0.00139", "0.00011", "0.00001", "12.4x", "134.9x"],
    ["200", "0.01169", "0.00073", "0.00004", "13.6x", "311.8x"],
    ["500", "0.06586", "0.00447", "0.00016", "14.2x", "425.8x"],
    ["1000", "0.26955", "0.01873", "0.00054", "14.2x", "484.8x"],
])
p("All three methods were checked to produce matching forces (within 1e-6) at every N before "
  "any timing was trusted.")
p("Bottleneck: the Python loop is limited by per-iteration interpreter overhead, not the "
  "arithmetic. NumPy removes that overhead but still allocates full (N,N,2)-shaped "
  "temporaries even for pairs outside the cutoff, so it does genuine O(N^2) work and memory "
  "traffic. The C version has neither problem and is limited only by raw floating-point "
  "throughput — speedup over the Python loop grows with N (135x to 485x) because the fixed "
  "per-call overhead matters less as the real workload grows.")

# ---------------------------------------------------------------- 8
h1("8. Task 7 — Memory and scalability")
table([
    ["N", "dtype", "theory", "measured", "match?"],
    ["100", "float32", "0.1 MB", "0.1 MB", "yes"],
    ["100", "float64", "0.2 MB", "0.2 MB", "yes"],
    ["1000", "float32", "8.0 MB", "8.0 MB", "yes"],
    ["1000", "float64", "16.0 MB", "16.0 MB", "yes"],
    ["5000", "float32", "200.0 MB", "200.0 MB", "yes"],
    ["5000", "float64", "400.0 MB", "400.0 MB", "yes"],
    ["10000", "float32", "800.0 MB", "not built", "-"],
    ["10000", "float64", "1600.0 MB", "not built", "-"],
])
p("At N=10000 the theoretical (N,N,2) array alone needs 1.6 GB for float64, and "
  "compute_forces builds roughly five more same-sized temporaries simultaneously (distance "
  "matrix, mask, safe-distance, direction, magnitude) — multiple GB at once just for one "
  "force evaluation. We did not allocate it on this machine for that reason.")
p("Answer: the fully vectorized approach becomes impractical somewhere around N=5,000–10,000 "
  "on a typical laptop — not because any single array is impossible to allocate, but because "
  "several same-sized temporaries exist at once and memory grows as N^2, so doubling N "
  "quadruples the memory (confirmed exactly by the table above).", bold=True)

# ---------------------------------------------------------------- 9
h1("9. Task 8 — Innovation: a cell-linked neighbor list")
p("Instead of comparing every particle to every other particle, particles are binned into a "
  "grid of cells the size of the cutoff radius; each particle only needs to check the 9 cells "
  "around it. For a fixed particle density this turns an O(N^2) calculation into an O(N) one.")
img("task8_innovation.png")
table([
    ["N", "cell list (s)", "brute force (s)", "speedup"],
    ["500", "0.0025", "0.0047", "1.9x"],
    ["1000", "0.0049", "0.0183", "3.7x"],
    ["2000", "0.0099", "0.0753", "7.6x"],
    ["5000", "0.0251", "0.5443", "21.7x"],
    ["10000", "0.0536", "skipped (Task 7: unsafe memory)", "-"],
])
p("Correctness first: at N=200, the cell list's forces matched the brute-force result to "
  "within 1.8e-15 (floating-point noise) — it is exact, not an approximation.", bold=True)
p("What it improved and the evidence: speedup grows with N (1.9x to 21.7x across the range "
  "actually compared), consistent with O(N) vs O(N^2) scaling, and the cell list keeps "
  "running (0.054s at N=10,000) exactly where Task 7 showed the brute-force array becomes "
  "impractical to even allocate. This directly fixes the scalability limit identified earlier "
  "in the project.")

# ---------------------------------------------------------------- 10
h1("10. Task 9 — Final computational engineering recommendation")
table([
    ["Choice", "Recommendation"],
    ["Precision", "float64 generally; float32 if memory-constrained"],
    ["Timestep", "dt = 0.01"],
    ["Integrator", "velocity-Verlet"],
    ["Force calculation", "NumPy for small N; cell list beyond ~1000"],
    ["Cutoff radius", "rc = 3.0 (unchanged)"],
    ["Dissipation", "gamma = 0.1"],
    ["Innovation", "cell-linked neighbor list"],
])
p("One-paragraph summary: For a system this size (tens to low hundreds of particles), "
  "float64 with dt=0.01, velocity-Verlet, and the plain NumPy vectorized force calculation "
  "is the simplest correct and fast-enough choice. The moment N climbs into the thousands, "
  "two things from Task 7 become real problems — the O(N^2) memory for the pairwise array "
  "and the O(N^2) time — and the cell-linked list from Task 8 is what actually fixes both, "
  "at no cost in accuracy. That is the central engineering lesson of this project: a method "
  "that looks fine at N=16 is not automatically the right method at N=10,000, and you only "
  "find out which one to use by actually measuring, not by guessing.")

# ---------------------------------------------------------------- 11
h1("11. Limitations")
bullets([
    "2D only; all particles share one mass; only a single Hookean interaction type was tested.",
    "The relaxation criterion (average speed < 0.01, sustained) is one reasonable choice "
    "among several defensible ones — low-gamma systems genuinely may never relax under "
    "elastic wall collisions, which is itself a finding, not a bug.",
    "The cell list's correctness relies on cell size ≥ cutoff radius; it was only verified "
    "at N=200 directly, though it is checked to reproduce the exact brute-force result there.",
    "Timing numbers are specific to this machine (Apple Silicon, clang -O2); absolute numbers "
    "will differ elsewhere, though the relative orderings should not.",
])
p("Code: sim.py (Task 1), core.py (shared physics), task2_animation.py through "
  "task8_innovation.py, task9_final_recommendation.md. All figures in this report are "
  "generated directly by those scripts, not hand-drawn.", italic=True, size=9)

doc.save(str(ROOT / "REPORT.docx"))
print("saved REPORT.docx")
