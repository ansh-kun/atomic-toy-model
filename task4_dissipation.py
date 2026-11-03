"""
Task 4 - add a viscous drag force, see how gamma affects relaxation.
gamma=0 should look conservative (matches Task 3); gamma>0 should bleed
energy and settle down. We define a real, numeric "relaxed" criterion
instead of eyeballing the animation.
"""

import numpy as np
import matplotlib.pyplot as plt
import core

N, L, rc, k, r0, dt, mass = 16, 10.0, 3.0, 1.5, 2.5, 0.005, 1.0
steps = 4000   # longer run so slow-gamma cases have time to settle
gammas = [0.0, 0.05, 0.1, 0.5]

# relaxation criterion: average particle speed stays below this for the rest
# of the run (not just one lucky instant)
SPEED_TOL = 1e-2


def relaxation_time(speeds, dt, tol=SPEED_TOL):
    """First time index after which speed never again exceeds tol.
    Returns None if it never relaxes by tol within the run."""
    below = speeds < tol
    for t in range(len(below)):
        if below[t:].all():
            return t * dt
    return None


fig, axes = plt.subplots(2, 2, figsize=(11, 8))
relax_table = []

for ax, gamma in zip(axes.flat, gammas):
    pos, vel = core.init_state(N, L)
    K = np.zeros(steps)
    U = np.zeros(steps)
    speed = np.zeros(steps)
    for t in range(steps):
        pos, vel, forces, dist, mask = core.verlet_step(pos, vel, dt, L, rc, k, r0, mass, gamma)
        K[t] = core.get_K(vel, mass)
        U[t] = core.get_U(dist, mask, k, r0)
        speed[t] = np.linalg.norm(vel, axis=1).mean()
    E = K + U

    t_relax = relaxation_time(speed, dt)
    relax_table.append((gamma, t_relax, E[-1]))

    tt = np.arange(steps) * dt
    ax.plot(tt, E, color="k", lw=1.3)
    ax.set_title(f"gamma = {gamma}" +
                 (f"  (relaxed at t={t_relax:.2f})" if t_relax else "  (did not relax)"))
    ax.set_xlabel("time")
    ax.set_ylabel("E_total")
    if t_relax:
        ax.axvline(t_relax, color="tab:orange", ls="--", lw=1)

plt.tight_layout()
plt.savefig("task4_dissipation.png", dpi=130)
print("saved task4_dissipation.png")

print(f"\n--- relaxation (speed must stay below {SPEED_TOL} for good) ---")
print(f"{'gamma':>8} {'relax time':>12} {'E_final':>10}")
for gamma, t_relax, e_final in relax_table:
    rt = f"{t_relax:.2f}" if t_relax else f"never (by t={steps*dt:.0f})"
    print(f"{gamma:>8} {rt:>12} {e_final:>10.2f}")

# A second, gentler measure for the gammas that don't fully stop moving within
# the run: how fast is E_total decaying overall? (slope of ln E vs t). This
# answers "how does gamma affect relaxation" even when nothing's fully static.
print("\n--- overall energy decay rate (slope of ln E vs t; steeper = faster) ---")
for gamma, t_relax, e_final in relax_table:
    pos, vel = core.init_state(N, L)
    E_hist = np.zeros(steps)
    for t in range(steps):
        pos, vel, forces, dist, mask = core.verlet_step(pos, vel, dt, L, rc, k, r0, mass, gamma)
        E_hist[t] = core.get_K(vel, mass) + core.get_U(dist, mask, k, r0)
    tt = np.arange(steps) * dt
    slope, intercept = np.polyfit(tt, np.log(E_hist), 1)
    tau = -1 / slope if slope < 0 else float("inf")
    print(f"gamma={gamma}: d(ln E)/dt = {slope:.4f}  ->  decay time constant tau ~ {tau:.2f}")
