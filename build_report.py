"""
Builds REPORT.html from scratch. Tables are plain monospace <pre> blocks,
not <table> elements -- LibreOffice's headless HTML->PDF conversion was
found (empirically, by actually rendering and checking) to badly mis-size
narrow first columns in real <table> markup, wrapping short numbers like
"0.05" one character per line no matter what CSS was tried. <pre> text
can't suffer that bug, so it's used everywhere instead.
"""

import base64
import pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).parent


def img_tag(path, target_w=600):
    w, h = Image.open(ROOT / path).size
    target_h = round(target_w * h / w)
    data = base64.b64encode((ROOT / path).read_bytes()).decode()
    return (f'<img src="data:image/png;base64,{data}" '
            f'style="width:{target_w}px;height:{target_h}px;" alt="{path}">')


def table(rows, widths):
    """rows: list of list-of-strings, rows[0] is the header. widths: char
    width per column. Renders as plain left-aligned monospace text."""
    lines = []
    header = "".join(c.ljust(w) for c, w in zip(rows[0], widths))
    lines.append(header)
    lines.append("-" * sum(widths))
    for r in rows[1:]:
        lines.append("".join(str(c).ljust(w) for c, w in zip(r, widths)))
    return "<pre>" + "\n".join(lines) + "</pre>"


parts = []

parts.append("""<!doctype html>
<html><head><meta charset="utf-8"><title>Atomic Toy Model - Project Report</title>
<style>
  body { font-family: Georgia, serif; max-width: 680px; margin: 40px auto; color: #222; line-height: 1.5; }
  h1 { font-size: 26px; }
  h2 { font-size: 20px; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-top: 40px; }
  pre { background: #f5f5f5; padding: 10px 12px; font-size: 12.5px; border: 1px solid #ddd;
        overflow-x: auto; line-height: 1.5; }
  img { margin: 10px 0; }
  code { background: #f5f5f5; padding: 1px 4px; font-size: 13px; }
  .small { color: #555; font-size: 13px; }
</style></head><body>
""")

parts.append("<h1>Atomic Toy Model</h1>")
parts.append("<p>Fundamentals of Scientific Computing &mdash; Computational Thinking Project<br>"
              "Instructors: Prof. Anuj Goyal, Prof. Saswata Bhattacharyya<br>Group 8</p>")

parts.append(table(
    [["Name", "Roll Number", "Responsibility"],
     ["Ansh Dadhore", "CO26BTECH11003", "Baseline simulator + verification (Task 1)"],
     ["Deepak K. Singhadiya", "CO26BTECH11005", "Animation (Task 2), precision study (Task 5)"],
     ["Purushottam Narayan", "MS26BTECH11027", "Energy/timestep (Task 3), memory/scaling (Task 7)"],
     ["Sajal Bajaj", "MS26BTECH11029", "Dissipation (Task 4), innovation (Task 8)"],
     ["Boyanapelli Abhiram Rao", "CO26BTECH11004", "Efficiency (Task 6), final rec. (Task 9), report"]],
    [24, 16, 50]))

parts.append("""
<h2>1. Model description, assumptions, governing equations</h2>
<p>A 2D toy particle system: N particles in a square box of side L, connected to every
other particle within a cutoff radius r<sub>c</sub> by a Hookean (spring-like) pair force,
and bouncing elastically off the box walls.</p>
<ul>
  <li><b>Pair force:</b> F<sub>ij</sub> = -k (r<sub>ij</sub> - r<sub>0</sub>), directed along the line joining particles i and j,
      applied only when r<sub>ij</sub> &lt; r<sub>c</sub> and i &ne; j.</li>
  <li><b>Potential energy:</b> U<sub>ij</sub> = 0.5 k (r<sub>ij</sub> - r<sub>0</sub>)<sup>2</sup></li>
  <li><b>Kinetic energy:</b> K = 0.5 &Sigma; m v<sup>2</sup></li>
  <li><b>Wall handling:</b> elastic reflection &mdash; the velocity component normal to a wall flips sign,
      position is clamped inside [0, L].</li>
  <li><b>Integration:</b> velocity-Verlet (half-kick, drift, recompute force, half-kick), unless
      otherwise noted (Task 3 also tests plain Euler for comparison).</li>
  <li><b>Assumptions:</b> all particles have equal mass (m=1); the pair interaction is the only
      internal force; the box walls are the only external influence.</li>
</ul>
<p class="small">Baseline parameters used throughout unless a task is explicitly varying one of
them: N=16, L=10.0, r<sub>c</sub>=3.0, k=1.5, r<sub>0</sub>=2.5, dt=0.005, mass=1.0.</p>
""")

parts.append("<h2>2. Task 1 &mdash; Baseline simulator and verification</h2>")
parts.append("<p>Implementation: <code>sim.py</code> / <code>core.py</code>. Five required numerical "
              "checks, all run against the live simulation output rather than assumed:</p>")
parts.append(table(
    [["Check", "Result"],
     ["Distance matrix symmetry error", "0.0 (exact)"],
     ["Max diagonal distance", "0.0 (exact)"],
     ["Any particle its own neighbor?", "False"],
     ["All particles inside the box?", "True, every step"],
     ["Norm of total internal force", "~5e-16 (machine precision, i.e. 0)"]],
    [34, 36]))

parts.append("""
<h2>3. Task 2 &mdash; Trajectory animation and diagnostics</h2>
<p>16 particles, 500 steps (<code>task2_animation.gif</code>, snapshots below). Diagnostics computed
directly from the stored trajectory, not eyeballed:</p>
<ul>
  <li>No particle ever left the box.</li>
  <li>No particle got stuck at a wall for &gt;80% of the run.</li>
  <li>No frame-to-frame jump bigger than 10&times; the median step size (median step = 0.0039 units) &mdash; no instability.</li>
  <li>Mean pairwise distance went from 4.46 to 5.13 (r<sub>0</sub>=2.5) &mdash; particles spread out, not an
      unexpected clustering collapse.</li>
</ul>
""")
parts.append(img_tag("task2_snapshots.png"))

parts.append("<h2>4. Task 3 &mdash; Energy conservation and timestep accuracy</h2>")
parts.append(img_tag("task3_energy_vs_dt.png"))
parts.append(table(
    [["dt", "steps", "max drift eps_E"],
     ["0.05", "50", "8.07%"],
     ["0.02", "125", "6.94%"],
     ["0.01", "250", "5.41%"],
     ["0.005", "500", "5.43%"]],
    [10, 10, 18]))
parts.append("<p><b>Largest defensible dt (10% drift threshold): 0.05</b>, though drift keeps improving "
              "down to dt=0.01 before flattening out, so 0.01 is the practical sweet spot (see Task 9).</p>")
parts.append(img_tag("task3_euler_vs_verlet.png"))
parts.append("<p>At the same dt=0.02: Euler drifted 10.61%, velocity-Verlet drifted 6.94% &mdash; Verlet "
              "is clearly the better integrator at equal cost.</p>")

parts.append("<h2>5. Task 4 &mdash; Dissipation and relaxation</h2>")
parts.append('<p>Drag force F = -&gamma;v added to the spring force. Relaxation criterion: average '
              'particle speed must stay below 0.01 for the <i>rest</i> of the run, not just momentarily.</p>')
parts.append(img_tag("task4_dissipation.png"))
parts.append(table(
    [["gamma", "Relaxed by t=20?", "decay tau", "E_final"],
     ["0.0", "No (conservative)", "~269", "15.69"],
     ["0.05", "No", "~14.5", "4.90"],
     ["0.1", "No", "~8.35", "1.81"],
     ["0.5", "Yes, at t=19.02", "~2.08", "~0.00"]],
    [10, 22, 12, 10]))
parts.append("<p><b>Answer:</b> relaxation time decreases monotonically as &gamma; increases (&tau; drops "
              "from ~269 to ~2 across the tested range) &mdash; more drag relaxes the system strictly "
              "faster, and only strong enough damping (&gamma;=0.5 here) fully stops the system within "
              "an accessible simulation time.</p>")

parts.append("<h2>6. Task 5 &mdash; Numerical precision: float32 vs float64</h2>")
parts.append(img_tag("task5_precision.png"))
parts.append(table(
    [["dtype", "memory", "median time", "max drift"],
     ["float32", "256 bytes", "17.35 ms", "5.43%"],
     ["float64", "512 bytes", "16.84 ms", "5.43%"]],
    [10, 14, 14, 12]))
parts.append("<p>Memory ratio float64/float32 = 2.00&times; exactly, as expected. Final-position relative "
              "difference eps_pos = 6.6e-7 &mdash; negligible. At this small N (16), float32 showed "
              "<i>no</i> speed advantage (0.97&times;) because Python/NumPy call overhead dominates, not "
              "raw arithmetic &mdash; the speed benefit of float32 only shows up at the larger N tested "
              "in Task 6/7, where memory bandwidth is the bottleneck.</p>"
              "<p><b>Answer:</b> yes, float32 is accurate enough for this problem; its computational "
              "advantage is purely in memory footprint at this scale, and would extend to speed at "
              "larger N.</p>")

parts.append("<h2>7. Task 6 &mdash; Computational efficiency and scaling</h2>")
parts.append(img_tag("task6_efficiency.png"))
parts.append(table(
    [["N", "loop(s)", "numpy(s)", "C(s)", "numpy x", "C x"],
     ["50", "0.00139", "0.00011", "0.00001", "12.4x", "134.9x"],
     ["200", "0.01169", "0.00073", "0.00004", "13.6x", "311.8x"],
     ["500", "0.06586", "0.00447", "0.00016", "14.2x", "425.8x"],
     ["1000", "0.26955", "0.01873", "0.00054", "14.2x", "484.8x"]],
    [8, 10, 10, 10, 10, 10]))
parts.append("<p>All three methods were checked to produce matching forces (within 1e-6) at every N "
              "before any timing was trusted.</p>"
              "<p><b>Bottleneck:</b> the Python loop is limited by per-iteration interpreter overhead, "
              "not the arithmetic. NumPy removes that overhead but still allocates full (N,N,2)-shaped "
              "temporaries even for pairs outside the cutoff, so it does genuine O(N&sup2;) work and "
              "memory traffic. The C version has neither problem and is limited only by raw "
              "floating-point throughput &mdash; speedup over the Python loop grows with N (135x to "
              "485x) because the fixed per-call overhead matters less as the real workload grows.</p>")

parts.append("<h2>8. Task 7 &mdash; Memory and scalability</h2>")
parts.append(table(
    [["N", "dtype", "theory", "measured", "match?"],
     ["100", "float32", "0.1 MB", "0.1 MB", "yes"],
     ["100", "float64", "0.2 MB", "0.2 MB", "yes"],
     ["1000", "float32", "8.0 MB", "8.0 MB", "yes"],
     ["1000", "float64", "16.0 MB", "16.0 MB", "yes"],
     ["5000", "float32", "200.0 MB", "200.0 MB", "yes"],
     ["5000", "float64", "400.0 MB", "400.0 MB", "yes"],
     ["10000", "float32", "800.0 MB", "not built", "-"],
     ["10000", "float64", "1600.0 MB", "not built", "-"]],
    [8, 10, 12, 12, 8]))
parts.append("<p>At N=10000 the theoretical (N,N,2) array alone needs 1.6 GB for float64, and "
              "<code>compute_forces</code> builds roughly five more same-sized temporaries simultaneously "
              "(distance matrix, mask, safe-distance, direction, magnitude) &mdash; multiple GB at once "
              "just for one force evaluation. We did not allocate it on this machine for that reason.</p>"
              "<p><b>Answer:</b> the fully vectorized approach becomes impractical somewhere around "
              "N=5,000&ndash;10,000 on a typical laptop &mdash; not because any single array is "
              "impossible to allocate, but because several same-sized temporaries exist at once and "
              "memory grows as N&sup2;, so doubling N quadruples the memory (confirmed exactly by the "
              "table above).</p>")

parts.append("<h2>9. Task 8 &mdash; Innovation: a cell-linked neighbor list</h2>")
parts.append("<p>Instead of comparing every particle to every other particle, particles are binned into "
              "a grid of cells the size of the cutoff radius; each particle only needs to check the 9 "
              "cells around it. For a fixed particle density this turns an O(N&sup2;) calculation into "
              "an O(N) one.</p>")
parts.append(img_tag("task8_innovation.png"))
parts.append(table(
    [["N", "cell list(s)", "brute force(s)", "speedup"],
     ["500", "0.0025", "0.0047", "1.9x"],
     ["1000", "0.0049", "0.0183", "3.7x"],
     ["2000", "0.0099", "0.0753", "7.6x"],
     ["5000", "0.0251", "0.5443", "21.7x"],
     ["10000", "0.0536", "skipped (Task 7: unsafe mem)", "-"]],
    [8, 14, 30, 10]))
parts.append("<p><b>Correctness first:</b> at N=200, the cell list's forces matched the brute-force "
              "result to within 1.8e-15 (floating-point noise) &mdash; it is exact, not an approximation.</p>"
              "<p><b>What it improved and the evidence:</b> speedup grows with N (1.9x to 21.7x across "
              "the range actually compared), consistent with O(N) vs O(N&sup2;) scaling, and the cell "
              "list keeps running (0.054s at N=10,000) exactly where Task 7 showed the brute-force "
              "array becomes impractical to even allocate. This directly fixes the scalability limit "
              "identified earlier in the project.</p>")

parts.append("<h2>10. Task 9 &mdash; Final computational engineering recommendation</h2>")
parts.append(table(
    [["Choice", "Recommendation"],
     ["Precision", "float64 generally; float32 if memory-constrained"],
     ["Timestep", "dt = 0.01"],
     ["Integrator", "velocity-Verlet"],
     ["Force calc", "NumPy for small N; cell list beyond ~1000"],
     ["Cutoff radius", "rc = 3.0 (unchanged)"],
     ["Dissipation", "gamma = 0.1"],
     ["Innovation", "cell-linked neighbor list"]],
    [16, 48]))
parts.append("""
<p><b>One-paragraph summary.</b> For a system this size (tens to low hundreds of particles), float64
with dt=0.01, velocity-Verlet, and the plain NumPy vectorized force calculation is the simplest
correct and fast-enough choice. The moment N climbs into the thousands, two things from Task 7
become real problems &mdash; the O(N&sup2;) memory for the pairwise array and the O(N&sup2;) time &mdash;
and the cell-linked list from Task 8 is what actually fixes both, at no cost in accuracy. That is
the central engineering lesson of this project: a method that looks fine at N=16 is not
automatically the right method at N=10,000, and you only find out which one to use by actually
measuring, not by guessing.</p>

<h2>11. Limitations</h2>
<ul>
  <li>2D only; all particles share one mass; only a single Hookean interaction type was tested.</li>
  <li>The relaxation criterion (average speed &lt; 0.01, sustained) is one reasonable choice among
      several defensible ones &mdash; low-&gamma; systems genuinely may never relax under elastic wall
      collisions, which is itself a finding, not a bug.</li>
  <li>The cell list's correctness relies on cell size &ge; cutoff radius; it was only verified at
      N=200 directly, though it is checked to reproduce the exact brute-force result there.</li>
  <li>Timing numbers are specific to this machine (Apple Silicon, clang -O2); absolute numbers
      will differ elsewhere, though the relative orderings should not.</li>
</ul>
<p class="small">Code: <code>sim.py</code> (Task 1), <code>core.py</code> (shared physics),
<code>task2_animation.py</code> through <code>task8_innovation.py</code>,
<code>task9_final_recommendation.md</code>. All figures in this report are generated directly
by those scripts, not hand-drawn.</p>
</body></html>
""")

out = "\n".join(parts)
(ROOT / "REPORT.html").write_text(out)
print(f"wrote REPORT.html ({len(out)} bytes)")
