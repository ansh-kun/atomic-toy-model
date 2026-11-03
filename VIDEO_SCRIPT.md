# Video presentation script (target: ~19 min)

Everyone reads their own part in their own words — this is a script to work from, not to
read verbatim on camera. Each [SHOW: ...] line is what should be on screen at that point.

---

## 1. Problem and model — ANSH (0:00–1:30)

[SHOW: title slide / mindmap.png]

"We built a toy particle simulator: N particles in a 2D box, connected to nearby particles
by spring-like forces, bouncing off the walls. The assignment wasn't just to make it run —
we had to prove it's accurate, efficient, and that we actually improved it, with real numbers
backing every claim.

The model: each particle feels a Hooke's-law spring force from every other particle within a
cutoff radius — pull together if farther than the rest length, push apart if closer. Particles
integrate forward in time with velocity-Verlet, and bounce elastically off the box walls.

The computational questions we're answering: is it correct, how accurate, how fast, how does
it scale, and what did we add beyond the baseline."

---

## 2. Baseline simulator and animation — ANSH + DEEPAK (1:30–3:30)

**Ansh:**
"The baseline (Task 1) computes pairwise distances between every particle using NumPy
broadcasting — no loops — then filters to neighbors within the cutoff, computes the spring
force, and integrates with velocity-Verlet: half-kick, move, recompute force, half-kick."

[SHOW: sim.py / core.py compute_forces function, briefly]

**Deepak:**
"Here's the animation — 16 particles, 500 steps."

[SHOW: task2_animation.gif playing]

"We didn't just make this for show — we used it to check for bugs. No particle ever escaped
the box, nothing got stuck at a wall, no sudden unrealistic jumps between frames, and the
particles spread out rather than collapsing into an unexpected clump."

[SHOW: task2_snapshots.png — the 4 static frames]

---

## 3. Verification — ANSH (3:30–5:30)

[SHOW: REPORT Task 1 table]

"Five required checks, with actual numbers, not just claims:
- Distance matrix is symmetric — error is exactly 0.
- Diagonal distances are exactly 0.
- No particle is ever counted as its own neighbor.
- Every particle stayed inside the box, every single step.
- And the big one — Newton's third law: total internal force should sum to zero. We measured
  5 times 10 to the minus 16 — that's machine precision, so effectively zero."

---

## 4. Accuracy and energy — PURUSHOTTAM (5:30–8:30)

[SHOW: task3_energy_vs_dt.png]

"We ran the same starting configuration at four timesteps: 0.05 down to 0.005, and tracked
kinetic energy, potential energy, and total energy. Energy should roughly conserve, and it
does — drift goes from 8.1% at dt=0.05 down to about 5.4% at dt=0.01, then barely improves
further at 0.005. So 0.01 is the point of diminishing returns."

[SHOW: task3_euler_vs_verlet.png]

"We also compared integrators at the same timestep. Euler drifts 10.6%, velocity-Verlet only
6.9% — same computational cost, clearly better accuracy. That's why we use Verlet everywhere."

---

## 5. Dissipation and relaxation — SAJAL (8:30–11:00)

[SHOW: task4_dissipation.png]

"The baseline is conservative — energy goes up and down but doesn't drain away. We added a
drag force, proportional to velocity, to model energy loss. At gamma=0 it's flat, as expected.
As gamma increases, energy visibly bleeds out faster.

We didn't just eyeball 'looks stopped' — we defined a real criterion: average particle speed
has to stay below 0.01 for the rest of the run, not just one lucky instant. Only gamma=0.5 hit
that, at t=19. For the others we measured a decay time constant instead — it drops from about
269 at gamma=0 down to about 2 at gamma=0.5. More drag, strictly faster relaxation — not just
intuitively, but by a number."

---

## 6. Numerical precision — DEEPAK (11:00–13:30)

[SHOW: task5_precision.png]

"We compared float32 against float64. Memory is exactly half for float32 — 256 bytes versus
512 — exactly as expected. Accuracy loss is tiny: the final positions only differ by about
6.6 times 10 to the minus 7, relatively. At our small particle count, float32 wasn't actually
faster — Python call overhead dominates at this scale, not raw math — but the memory savings
still matter, and we expected the speed benefit to show up more at larger N, which is exactly
what the next section covers."

---

## 7. Efficiency, scaling, and memory — ABHIRAM + PURUSHOTTAM (13:30–16:30)

**Abhiram:**
[SHOW: task6_efficiency.png]

"We compared three ways to compute the pair forces: a plain Python double loop, NumPy
vectorized, and a compiled C version — all checked to give the same answer before we trusted
any timing. At N=1000, NumPy is about 14 times faster than the loop, and C is about 485 times
faster than the loop. The bottleneck in the loop is pure interpreter overhead; NumPy still
builds full N-squared temporary arrays; C has neither problem."

**Purushottam:**
[SHOW: REPORT Task 7 table]

"That N-squared cost shows up in memory too. We checked our theoretical formula against
NumPy's actual byte count, and it matches exactly, every time. At N=10,000, that one array
alone would need 1.6 gigabytes, and the real calculation needs several of those at once — so
we didn't even try to allocate it. The fully vectorized approach stops being practical
somewhere between 5,000 and 10,000 particles."

---

## 8. Innovation — SAJAL (16:30–18:30)

[SHOW: task8_innovation.png]

"This is where we fix that exact wall. Instead of comparing every particle to every other
particle, we bin particles into a grid of cells the size of the cutoff radius, so each
particle only checks its own cell and the 8 around it. For fixed density, that turns an
N-squared calculation into something closer to N.

First, we proved it's correct — at N=200 it matches the brute-force result to within
10 to the minus 15, basically floating-point noise, not an approximation.

Then the speedup: 1.9 times at N=500, climbing to almost 22 times at N=5000. And it keeps
running fine all the way to N=10,000 — exactly where the brute-force method becomes
impractical. This directly solves the scaling problem from the last section."

---

## 9. Final recommendation — ABHIRAM (18:30–19:30)

[SHOW: REPORT Task 9 table]

"Pulling it together: float64 for correctness, float32 only if memory-constrained. Timestep
0.01 — the point where accuracy stops improving. Velocity-Verlet over Euler. NumPy for small
N, our cell list beyond about a thousand particles. Cutoff radius unchanged — it already
passed every verification check. Drag coefficient 0.1 for a visible but not instant
relaxation. And our innovation, the cell list, as the one change that actually matters at
scale.

The lesson from this whole project: what works at N=16 isn't automatically right at
N=10,000 — you only know which method to use by actually measuring it, which is what we did
at every step."

---

## Notes for recording

- Total: ~19.5 minutes, within the 15–20 min window.
- Every number above is pulled directly from `REPORT.pdf` / the `task*.py` script outputs —
  don't round differently or invent new numbers on camera.
- Each person should have the relevant image/plot/table open and visible before they start
  talking, not scrambling to find it mid-sentence.
- The task sheet explicitly says: don't just read slides or scroll through the notebook —
  explain it like you understand it.
