# sim.py — baseline particle simulator (Task 1)

Quick notes on what `sim.py` does. Covers Task 1 only (baseline model + verification), not the full project.

## What it models

N particles in a 2D box, connected by spring-like forces to nearby particles, bouncing off the walls. Basically a toy "atoms connected by invisible springs" system.

## Params

```python
N = 16       # particles
L = 10.0     # box is L x L
rc = 3.0     # cutoff radius, ignore particles farther than this
k = 1.5      # spring stiffness
r0 = 2.5     # spring rest length
dt = 0.005   # timestep
steps = 500
mass = 1.0
```

`k`, `r0`, `dt` were tuned by hand. First attempt (`k=5, r0=1.2, dt=0.01`) blew up — ~1400% energy drift over the run, springs too stiff for that timestep. Current values keep drift around ~9%.

## Functions

- **`init_state`** — random starting positions (inside box, small margin) and random small velocities.
- **`get_dist(pos)`** — builds the full `(N,N)` pairwise distance matrix using broadcasting (`pos[:,None,:] - pos[None,:,:]`). Diagonal is 0 by construction, matrix is symmetric by construction.
- **`get_neighbors(dist)`** — `dist < rc`, then zeroes the diagonal so a particle is never its own neighbor.
- **`compute_forces(pos)`** — Hooke's law spring force per neighbor pair: `F = -k*(r - r0)` along the connecting direction. `safe_dist` just avoids a literal `0/0` on the diagonal (that entry gets masked out anyway).
- **`get_U` / `get_K`** — potential energy `0.5*k*(r-r0)²` (divided by 2, pairs are double-counted in the matrix) and kinetic energy `0.5*m*v²`.
- **`bounce_walls`** — flips velocity component and clamps position if a particle crosses a wall.
- **`one_step`** — velocity-Verlet integration: half-kick → move → recompute force → finish kick. More stable than plain Euler for spring systems.
- **`run_sim`** — runs `one_step` 500x, logs K and U each step.
- **`check_everything`** — the 5 required verification checks, printed as actual numbers:
  - distance matrix symmetry error
  - max diagonal distance
  - self-neighbor check
  - all particles inside box check
  - net internal force norm (should be ~0, Newton's third law)

## Sample output

```
N = 16, steps = 500
K0, U0, E0 = 0.7718 9.9135 10.6853
K_end, U_end, E_end = 8.3031 2.3839 10.6870
max energy drift: 0.0877

--- verification checks ---
distance matrix symmetric? err = 0.0
max diagonal dist (shud be 0): 0.0
self counted as neighbor anywhere? False
everyone inside the box? True
total force norm (~0 expected): 5.19e-16
```

## What's missing (rest of the project)

Task 1 is done. Not done yet: animation (Task 2), timestep/energy sweep (Task 3), dissipation + relaxation (Task 4), float32 vs float64 (Task 5), timing/scaling incl. C implementation (Task 6), memory/scalability (Task 7), innovation (Task 8), final recommendation (Task 9), report, video.

## How to run

```bash
cd atomic_toy_model
./venv/bin/python sim.py
```
