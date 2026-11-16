# Video presentation script (target: ~19 min)

Everyone reads their own part in their own words — this is a script to work from, not to
read verbatim on camera. [SHOW: ...] = what's on screen (animation/plot/table).
[CODE: ...] = the one snippet to pull up and point at while talking — don't scroll through
the whole file, just that function, say what it does, then go back to the plot.

---

## 1. Problem and model — ANSH (0:00–1:30)

[SHOW: title slide / mindmap.png]

"We built a toy particle simulator: N particles in a 2D box, connected to nearby particles
by spring-like forces, bouncing off the walls. The assignment wasn't just to make it run —
we had to prove it's accurate, efficient, and that we actually improved it, with real numbers
backing every claim.

The model: each particle feels a Hooke's-law spring force from every other particle within a
cutoff radius — pull together if farther than the rest length, push apart if closer. Particles
integrate forward in time with velocity-Verlet, and bounce elastically off the box walls."

No code yet — save it for the next section.

---

## 2. Baseline simulator and animation — ANSH + DEEPAK (1:30–3:30)

**Ansh:**
"The baseline computes every pairwise distance in one shot, no loops, using NumPy
broadcasting."

[CODE: core.py, function `get_dist`]
```python
def get_dist(pos):
    diff = pos[:, None, :] - pos[None, :, :]
    dist = np.linalg.norm(diff, axis=-1)
    return dist, diff
```
"That one line computes every particle's distance to every other particle at once — that's
the trick that makes this fast later on."

[CODE: core.py, function `verlet_step`, just point at the shape of it]
"Half-kick the velocity, move the position, recompute the force, half-kick again — that's
velocity-Verlet, and it's what keeps energy from drifting, which we show in a few minutes."

**Deepak:**
"Here's the animation — 16 particles, 500 steps."

[SHOW: task2_animation.gif playing]

"We didn't just make this for show — we used it to check for bugs."

[CODE: task2_animation.py, the diagnostics block]
```python
outside = (traj < -1e-6) | (traj > L + 1e-6)
...
jumps = step_disp > 10 * med
```
"We check this directly from the stored trajectory: did anyone escape the box, get stuck at
a wall, or jump unrealistically between frames? All clear. And particles spread out rather
than collapsing into an unexpected clump."

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

[CODE: core.py, function `get_neighbors` — just the one line]
```python
np.fill_diagonal(mask, False)
```
"That line is what guarantees the 'no self-neighbor' check passes — we force the diagonal to
false so a particle can never be its own neighbor."

---

## 4. Accuracy and energy — PURUSHOTTAM (5:30–8:30)

[SHOW: task3_energy_vs_dt.png]

"We ran the same starting configuration at four timesteps: 0.05 down to 0.005, and tracked
kinetic energy, potential energy, and total energy. Drift goes from 8.1% at dt=0.05 down to
about 5.4% at dt=0.01, then barely improves further at 0.005. So 0.01 is the point of
diminishing returns."

[SHOW: task3_euler_vs_verlet.png]

[CODE: core.py, `verlet_step` vs `euler_step` side by side]
```python
# euler_step: new_pos = pos + dt * vel   (uses the OLD velocity)
# verlet_step: new_pos = pos + dt * vel_half   (uses a half-updated velocity)
```
"That's the actual difference in the code — Euler moves you using the velocity you had before
the force update; Verlet updates velocity halfway first. Same cost, but Euler drifts 10.6%
at this timestep, Verlet only 6.9%. That's why we use Verlet everywhere else in the project."

---

## 5. Dissipation and relaxation — SAJAL (8:30–11:00)

[SHOW: task4_dissipation.png]

"The baseline is conservative — energy goes up and down but doesn't drain away. We added a
drag force to model energy loss."

[CODE: core.py, `verlet_step`]
```python
forces = forces - gamma * vel
```
"One line — drag proportional to velocity, same sign as the spring force so it always
opposes motion. At gamma=0 this does nothing, so energy stays flat, as expected. As gamma
increases, energy visibly bleeds out faster.

We didn't just eyeball 'looks stopped' — we defined a real criterion: average particle speed
has to stay below 0.01 for the rest of the run, not just one lucky instant. Only gamma=0.5 hit
that, at t=19. For the others we measured a decay time constant instead — it drops from about
269 at gamma=0 down to about 2 at gamma=0.5."

---

## 6. Numerical precision — DEEPAK (11:00–13:30)

[SHOW: task5_precision.png]

[CODE: task5_precision.py, the dtype loop]
```python
for dtype in (np.float32, np.float64):
    pos, vel = core.init_state(N, L, dtype=dtype)
```
"Same simulation, just cast to a different number type. Memory is exactly half for float32 —
256 bytes versus 512 — exactly as expected. Accuracy loss is tiny: final positions only
differ by about 6.6 times 10 to the minus 7, relatively. At our small particle count, float32
wasn't actually faster — Python call overhead dominates at this scale — but the memory
savings still matter, and we expected the speed benefit to show up more at larger N, which is
exactly what the next section covers."

---

## 7. Efficiency, scaling, and memory — ABHIRAM + PURUSHOTTAM (13:30–16:30)

**Abhiram:**
[SHOW: task6_efficiency.png]

"We compared three ways to compute the pair forces."

[CODE: task6_efficiency.py, `forces_python_loop`, just the inner loop]
```python
for i in range(n):
    for j in range(n):
        ...
```
"A plain Python double loop — this is the slow, obvious way."

[CODE: pair_forces.c, the same loop in C]
```c
for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
```
"And the exact same algorithm, compiled in C. All three — loop, NumPy, C — were checked to
give the same answer before we trusted any timing. At N=1000, NumPy is about 14 times faster
than the loop, C is about 485 times faster. The loop's bottleneck is pure interpreter
overhead; NumPy still builds full N-squared temporary arrays; C has neither problem."

**Purushottam:**
[SHOW: REPORT Task 7 table]

[CODE: task7_memory.py, `theory_bytes`]
```python
def theory_bytes(n, itemsize):
    return n * n * 2 * itemsize
```
"That N-squared cost shows up in memory too. We checked this formula against NumPy's actual
byte count, and it matches exactly, every time. At N=10,000, that one array alone would need
1.6 gigabytes, and the real calculation needs several of those at once — so we didn't even
try to allocate it. The fully vectorized approach stops being practical somewhere between
5,000 and 10,000 particles."

---

## 8. Innovation — SAJAL (16:30–18:30)

[SHOW: task8_innovation.png]

"This is where we fix that exact wall."

[CODE: task8_innovation.py, `cell_list_forces` — just the cell-binning part]
```python
cell_of = np.clip((pos // cell_size).astype(int), 0, ncells - 1)
...
for dcx in (-1, 0, 1):
    for dcy in (-1, 0, 1):
        for j in cells.get((cx + dcx, cy + dcy), ()):
```
"Instead of comparing every particle to every other particle, we bin particles into a grid of
cells the size of the cutoff radius, so each particle only checks its own cell and the 8
around it. For fixed density, that turns an N-squared calculation into something closer to N.

First, we proved it's correct — at N=200 it matches the brute-force result to within
10 to the minus 15, basically floating-point noise, not an approximation.

Then the speedup: 1.9 times at N=500, climbing to almost 22 times at N=5000. And it keeps
running fine all the way to N=10,000 — exactly where the brute-force method becomes
impractical."

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
- For every [CODE: ...] cue: open that one file, scroll to that one function, point at it,
  say the one sentence about what it does — then switch back to the plot. Never scroll through
  a whole file live; the rubric explicitly penalizes that.
- Each person should have the relevant image/plot/table/code file open and ready before they
  start talking, not scrambling to find it mid-sentence.
- The task sheet explicitly says: don't just read slides or scroll through the notebook or
  code — explain it like you understand it. The video must be understandable without anyone
  opening the source code themselves.
