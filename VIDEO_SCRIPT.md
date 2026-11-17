# Video presentation script (target: ~19 min)

Everyone reads their own part in their own words — this is a script to work from, not to
read verbatim on camera. [SHOW: ...] = what's on screen (animation/plot/table).
[CODE: ...] = the one snippet to pull up and point at while talking — don't scroll through
the whole file, just that function, say what it does, then go back to the plot.

---

## 1. Problem and model — ANSH (0:00–1:30)

[SHOW: title slide / mindmap.png]

"Making a simulation with a bunch of particles isn't the hard part. The hard part is proving
it actually works, making it fast, and showing it's actually better than the simple way of
doing it. By the end of this video, we'll show you one piece of code we made almost 500 times
faster, and a smarter way of finding nearby particles that scales way better as you add more
of them. And every number we give you, we actually measured it — we're not guessing.

Here's the model. We have a bunch of particles moving around inside a 2D box — think of it
like balls inside a square, not a cube, just to keep things simple and easy to actually watch
on screen. Every particle pulls or pushes on the particles close to it, like they're
connected by tiny springs. If two particles are too far apart, they pull together, trying to
get back to a natural resting distance. If they're too close, they push apart, like a spring
that's been squeezed. This only happens between particles that are within a certain distance
of each other, which we call the cutoff radius — anything farther than that just gets
ignored, otherwise every particle would have to check every other particle in the entire box,
which gets really expensive really fast.

Every tiny step in time, we do the same four things: figure out the force on every particle,
update how fast each one is moving, update where it is, and if a particle hits a wall, bounce
it off, like a ball bouncing off a surface. That one little loop repeats hundreds of times to
produce the whole simulation."

No code yet — save it for the next section.

---

## 2. Baseline simulator and animation — ANSH + DEEPAK (1:30–3:30)

**Ansh:**
"The first thing our code does is figure out how far every particle is from every other
particle. Instead of writing a loop that checks each pair one at a time, which is slow, we
get NumPy to do the whole thing in one go. Let me actually walk through this function,
because it's the foundation everything else is built on."

[CODE: core.py, function `get_dist`]
```python
def get_dist(pos):
    diff = pos[:, None, :] - pos[None, :, :]
    dist = np.linalg.norm(diff, axis=-1)
    return dist, diff
```
"`pos` holds the x and y position of every particle. This first line takes every particle's
position and subtracts it from every other particle's position, all at once — so `diff`
ends up holding the x and y gap between every single pair of particles. The second line just
turns each of those x-y gaps into one actual distance number, using the regular distance
formula. So after these two lines, we have the distance from every particle to every other
particle, calculated in one shot, with no loop at all. That's the part that makes everything
downstream fast."

[CODE: core.py, function `verlet_step`]
"Now here's how we actually move the particles forward in time, step by step."
```python
forces, dist, mask = compute_forces(pos, rc, k, r0)
acc = forces / mass
vel_half = vel + 0.5 * dt * acc

new_pos = pos + dt * vel_half
new_pos, vel_half = bounce_walls(new_pos, vel_half, L)

forces2, dist2, mask2 = compute_forces(new_pos, rc, k, r0)
acc2 = forces2 / mass
new_vel = vel_half + 0.5 * dt * acc2
```
"First we calculate the force on every particle right now, and turn that into acceleration —
force divided by mass. Then we update the speed, but only by half a time-step, not a full
one — that's why we call it `vel_half`. Using that half-updated speed, we move every particle
to its new position, and check if anyone hit a wall and needs to bounce. Now that particles
are in their new spot, we recalculate the force all over again, because the force depends on
how far apart particles are, and that's just changed. And finally we use that new force to
finish updating the speed, the other half. So speed gets updated in two half-steps, with a
position update sandwiched in the middle — that's why it's called velocity-Verlet. The reason
we bother with this instead of something simpler is that it keeps the total energy of the
system stable instead of slowly drifting away, which we'll actually measure and show you in a
few minutes."

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

"Making a simulation look believable on screen isn't the same as proving it's correct. So we
ran five actual checks, with real numbers for each one, not just claims:
- The distance from particle A to B should equal the distance from B to A — that's just
  basic geometry. We checked it, and the error there is exactly zero.
- The distance from a particle to itself should be zero — it is.
- No particle should ever count itself as its own neighbor, because that would mean a
  particle pulling or pushing on itself, which makes no physical sense — we checked that too.
- Every particle stayed inside the box, for the entire run, every single step. Not one frame
  where someone escaped.
- And the big one — Newton's third law: every push or pull between two particles has to be
  equal and opposite, which means if you add up every single internal force in the whole
  system, it should cancel out to exactly zero. We actually measured that sum, and got a
  number so tiny — about 5 times 10 to the minus 16 — that it's basically zero. The only
  reason it's not perfectly, mathematically zero is the small rounding errors computers
  always carry around."

[CODE: core.py, function `get_neighbors`]
```python
def get_neighbors(dist, rc):
    mask = dist < rc
    np.fill_diagonal(mask, False)
    return mask
```
"This function decides which particles actually count as neighbors. The first line just says:
anyone closer than the cutoff radius counts as a neighbor, anyone farther doesn't — that's a
single comparison across every pair at once. The second line is what fixes the self-neighbor
problem: the diagonal of this grid is literally every particle compared to itself, and we
just force that whole diagonal to say 'false', so a particle is automatically excluded from
being its own neighbor. That's the exact line responsible for one of the five checks I just
showed you passing."

---

## 4. Accuracy and energy — PURUSHOTTAM (5:30–8:30)

[SHOW: task3_energy_vs_dt.png]

"A physics simulation like this should conserve energy — energy shouldn't just appear or
disappear on its own. But because we're taking discrete little time-steps instead of truly
continuous time, some drift is unavoidable. The question is how much, and whether making the
step smaller actually helps. So we ran the exact same starting setup four times, with four
different step sizes — 0.05 down to 0.005 — and tracked kinetic energy, potential energy, and
the total.

Here's how we actually measured 'how much it drifted':"

```python
E = K + U
drift = np.abs((E - E[0]) / E[0]).max()
```
"We add kinetic and potential together to get the total energy at every single step. Then we
take the very first value, `E[0]`, as our reference — that's what the energy 'should' stay at.
For every other step, we check how far away it got from that starting value, as a fraction,
and we take the absolute value so a drop and a rise both count the same way. Then we take the
single worst moment across the whole run with `.max()` — not the average, the worst case,
because that's the number you'd actually get burned by.

The result: drift goes from 8.1% at the biggest step size, down to about 5.4% once we shrink
the step to 0.01, and then barely improves any further at 0.005. So 0.01 is the point of
diminishing returns — going smaller still costs you more computing time without buying much
more accuracy."

[SHOW: task3_euler_vs_verlet.png]

"Step size isn't the only thing that matters — the method itself matters too. We compared two
ways of moving particles forward in time, at the exact same step size, so it's a fair fight."

```python
# inside euler_step:
new_pos = pos + dt * vel          # uses the OLD velocity, before updating it
new_vel = vel + dt * acc

# inside verlet_step:
vel_half = vel + 0.5 * dt * acc
new_pos = pos + dt * vel_half     # uses a HALF-updated velocity
```
"Euler is the simple way — it moves the particle using the velocity it already had, and only
updates the velocity afterward. Verlet does something slightly smarter: it updates the
velocity halfway first, moves the particle using that improved half-way velocity, and only
finishes updating the velocity after that. Both cost basically the same to compute — same
number of operations — but Euler drifted 10.6% at this step size, while Verlet only drifted
6.9%. Same cost, noticeably better accuracy. That's the whole reason we use Verlet everywhere
else in this project instead of the simpler method."

---

## 5. Dissipation and relaxation — SAJAL (8:30–11:00)

[SHOW: task4_dissipation.png]

"Everything so far has been conservative — energy goes up and down but never actually drains
away, like a frictionless world. Real systems lose energy to friction, so we added a drag
force to model that."

```python
forces = forces - gamma * vel
```
"This is just one extra line inside the same step function from before. We take the spring
force we already calculated, and subtract velocity times a constant we call gamma. Because
it's subtracting velocity, this force always points backwards, opposite to whichever way a
particle is already moving — that's exactly what drag or friction does in real life, it always
opposes motion, never helps it along. If gamma is zero, we're subtracting zero, so this line
does literally nothing and we're back to the original conservative version. As gamma gets
bigger, more energy visibly bleeds out of the system over time.

But 'it looks like it stopped' isn't good enough as a claim, so we defined an actual numeric
rule for when a system counts as relaxed:"

```python
def relaxation_time(speeds, dt, tol=SPEED_TOL):
    below = speeds < tol
    for t in range(len(below)):
        if below[t:].all():
            return t * dt
    return None
```
"`speeds` is the average particle speed at every single step of the run. `below` just marks
every step where that speed was under our tolerance. Then — and this is the important part —
we don't just check for one lucky slow moment, we check `below[t:].all()`, meaning 'from this
point onward, is the speed under the tolerance for literally every remaining step, no
exceptions.' The first time index where that's true is the real relaxation time; if it's never
true, we return `None`, meaning it never actually settled down during the run.

Only gamma equals 0.5 actually satisfied that strict condition, relaxing at t=19. For the
gentler drag values that didn't fully stop within our run, we measured something else instead
— how fast the energy curve was decaying overall, using the slope of its logarithm — and that
decay time constant drops from about 269 at gamma=0 down to about 2 at gamma=0.5, which is a
cleaner way of saying the same thing: more drag means it calms down dramatically faster."

---

## 6. Numerical precision — DEEPAK (11:00–13:30)

[SHOW: task5_precision.png]

"Every number in our simulation is stored as a float — but there are actually two common
sizes of float, float32 and float64. float64 uses twice as many bits per number, so it can
store way more decimal precision, but it also costs twice the memory. We wanted to know: for
our simulation, does that extra precision actually matter, and is the smaller one actually
faster?"

```python
for dtype in (np.float32, np.float64):
    pos, vel = core.init_state(N, L, dtype=dtype)
    mem_bytes = pos.nbytes + vel.nbytes
```
"Same exact simulation, same starting positions, we just cast the numbers to a different type
before running it. `.nbytes` just asks NumPy directly how many bytes of memory an array is
actually using, no guessing involved."

```python
eps_pos = np.linalg.norm(x32 - x64) / np.linalg.norm(x64)
mem_ratio = results[np.float64]["mem"] / results[np.float32]["mem"]
```
"We take the final position from the float32 run and the final position from the float64 run,
subtract them, and measure that gap relative to the actual size of the position — that's
`eps_pos`, our accuracy-loss number. For memory, we just divide one measured byte count by the
other.

The results: memory is exactly half for float32 — 256 bytes versus 512 — exactly what you'd
expect from using half as many bits per number. But the accuracy loss is tiny: final positions
only differ by about 6.6 times 10 to the minus 7, relatively — practically nothing. As for
speed, at our small particle count float32 wasn't actually faster, because at this scale the
overhead of Python itself calling functions dominates, not the raw number-crunching. But the
memory savings are real regardless, and we expected the speed benefit to show up more clearly
once N gets much bigger — which is exactly what the next section tests."

---

## 7. Efficiency, scaling, and memory — ABHIRAM + PURUSHOTTAM (13:30–16:30)

**Abhiram:**
[SHOW: task6_efficiency.png]

"Speed isn't just about NumPy versus plain Python — there's actually a third option too. We
compared three completely different ways of computing the same pair forces, to see how much
each layer of 'getting closer to the hardware' actually buys you."

```python
def forces_python_loop(pos, rc, k, r0):
    n = len(pos)
    forces = np.zeros((n, 2))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dx = pos[i, 0] - pos[j, 0]
            dy = pos[i, 1] - pos[j, 1]
            dist = (dx * dx + dy * dy) ** 0.5
            if dist >= rc:
                continue
            mag = -k * (dist - r0)
            safe = dist if dist != 0 else 1.0
            forces[i, 0] += mag * dx / safe
            forces[i, 1] += mag * dy / safe
    return forces
```
"This is the plain, obvious way — the way you'd write it in any beginner programming class.
Two nested loops checking every single pair one at a time, skip comparing a particle to
itself, work out the x and y gap, turn that into a distance, skip it if it's outside the
cutoff, and otherwise add this pair's push or pull straight into that particle's force. It's
completely correct, and completely slow, because Python has to re-interpret every single one
of these lines, for every single pair, one at a time."

```c
for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
        // same exact math, but compiled to machine code ahead of time
```
"And this is the exact same algorithm, just written in C and compiled before we ever run it,
instead of interpreted line by line while it runs. Before trusting any timing numbers at all,
we made all three methods — the loop, NumPy, and C — agree on the actual answer at every N we
tested, using `np.allclose`. Only once we knew they all computed the same forces did we trust
the stopwatch. At N=1000, NumPy comes out about 14 times faster than the plain loop, and C
comes out about 485 times faster. The loop's problem is pure interpreter overhead — Python
re-checking types and doing lookups on every tiny operation. NumPy still builds a full
N-squared temporary array even for pairs that end up outside the cutoff, so it's still doing
N-squared work, just in fast compiled code instead of the slow interpreter. C has neither
problem — no interpreter, and no wasted temporary arrays."

**Purushottam:**
[SHOW: REPORT Task 7 table]

"Abhiram just showed that the pair-force calculation costs N-squared time. It turns out it
also costs N-squared memory, and that second limit actually bites first."

```python
def theory_bytes(n, itemsize):
    return n * n * 2 * itemsize
```
"This is just the formula for how many bytes that one array of distances between every pair
should need — n times n pairs, times 2 for x and y, times however many bytes one number takes.
We didn't just trust the formula on faith though — we actually built the array in NumPy and
asked it directly how many bytes it used with `.nbytes`, and compared that measured number
against this formula's prediction. They matched exactly, every single time we tested it, which
means we can trust this formula even at sizes too big to safely build for real.

And that's exactly what we did at N=10,000: plugging into this same formula says that one
array alone would need about 1.6 gigabytes, and the actual force calculation needs several
arrays of roughly that same size in memory at the same time — distances, directions,
magnitudes, and more. So we didn't even attempt to allocate it for real at that size. Based on
both the formula and what we could safely measure, the fully vectorized NumPy approach stops
being practical somewhere between 5,000 and 10,000 particles — which is exactly the wall our
next section is built to break through."

---

## 8. Innovation — SAJAL (16:30–18:30)

[SHOW: task8_innovation.png]

"The whole problem with brute force is that every particle checks every other particle, even
ones that are way too far away to ever matter. Our fix: stop checking particles that are
obviously too far away, in the first place."

```python
cell_size = rc
ncells = max(1, int(L // cell_size) + 1)
cell_of = np.clip((pos // cell_size).astype(int), 0, ncells - 1)

cells = defaultdict(list)
for i in range(n):
    cells[(cell_of[i, 0], cell_of[i, 1])].append(i)
```
"First we chop the whole box into a grid of square cells, and we deliberately make each cell
exactly the size of the cutoff radius — that specific choice is what makes this work. Then for
every particle, we figure out which cell it falls into, and we build a lookup table, `cells`,
mapping each cell to the list of particle indices sitting inside it."

```python
for dcx in (-1, 0, 1):
    for dcy in (-1, 0, 1):
        for j in cells.get((cx + dcx, cy + dcy), ()):
            if j == i:
                continue
            # ... same distance and force math as before ...
```
"Here's the actual trick: because we made each cell exactly the cutoff radius in size, any
particle that could possibly be close enough to matter has to be in this particle's own cell,
or one of the 8 cells directly touching it — never farther away than that. So instead of
checking all N particles, each particle only checks the handful of particles in those 9
cells. For a box where particles are spread out at a roughly constant density, that turns an
N-squared calculation into something closer to just N.

Being faster doesn't matter if it's wrong, so first we proved correctness: at N=200, we
compared its answer directly against the brute-force result from Task 1, and the difference
was about 10 to the minus 15 — that's floating-point noise, not an approximation. It's not a
faster-but-slightly-wrong method, it's the same exact answer, just reached differently.

Then the actual speedup: 1.9 times faster at N=500, climbing to almost 22 times faster at
N=5000. And unlike brute force, it keeps running fine all the way out to N=10,000 — exactly
the size where Purushottam showed the old method runs out of memory."

---

## 9. Final recommendation — ABHIRAM (18:30–19:30)

[SHOW: REPORT Task 9 table]

"We've shown a lot of individual results — now let's actually turn that into one real
recommendation, setting by setting, with the reasoning behind each pick, not just the pick
itself.

Precision: float64 by default, and float32 only if you're genuinely tight on memory. We
measured the accuracy loss from float32 at basically nothing, but we also only saw its speed
benefit start to matter at bigger N than we could fully test here, so float64 stays the safe
default.

Timestep: 0.01. Not because smaller is always better — we specifically showed that going from
0.01 down to 0.005 barely improved the drift at all, so 0.01 is the largest step size that's
still genuinely accurate, and the smallest one that's not wasting computing time for nothing.

Integration method: velocity-Verlet over Euler, always. Same computational cost, meaningfully
better energy behavior — there's no real tradeoff here, so there's no reason to ever pick
Euler for a real run.

Force calculation method: plain NumPy for small particle counts, and our cell-list method
once you cross somewhere around a thousand particles. Below that size the brute-force method
is simple and fast enough; above it, the cell list is the only one that keeps scaling.

Cutoff radius: unchanged from the original value, because it already passed every single
verification check we ran in Task 1 — there was no actual evidence it needed changing.

Drag coefficient: 0.1, specifically because it gives a relaxation that's visible happening
over time, rather than either doing nothing at all or snapping to a stop instantly — useful
if you actually want to watch a system settle down, not just confirm that it eventually does.

And our one innovation, the cell list, is the single change that actually matters once you
scale up — everything else on this list is a sensible default, but this is the one thing that
turns an impossible problem back into a solvable one.

The real lesson from this whole project is bigger than any one of these settings: what works
well at N=16 isn't automatically the right choice at N=10,000. You don't get to assume that —
you only find out which method is actually right by measuring it directly, which is exactly
what we did at every single step of this project."

---

## Notes for recording

- **Recording separately, then editing together:** each person records ALL of their own lines
  back-to-back as one continuous clip, in the order they appear in the script — even if
  someone else's section falls in between yours. Example: Ansh records Section 1, then his two
  code lines in Section 2, then all of Section 3, straight through, without waiting for Deepak.
  Deepak separately records just his animation lines from Section 2. In editing, cut the clips
  together in the script's order (Ansh → Deepak's clip inserted → back to Ansh → next person).
  No one needs 2 separate video files just because a section is shared with someone else.
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
