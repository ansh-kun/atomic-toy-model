"""
Task 2 - trajectory animation + using it as a diagnostic.
>=12 particles, >=500 steps, box visible, particle motion visible.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import core

N, L, rc, k, r0, dt, steps, mass = 16, 10.0, 3.0, 1.5, 2.5, 0.005, 500, 1.0

pos, vel = core.init_state(N, L)
out = core.run("verlet", pos, vel, steps, dt, L, rc, k, r0, mass, record_traj=True)
traj = out["traj"]  # (steps, N, 2)

# ---- diagnostics computed straight from the trajectory, not just "eyeballed" ----
print("--- animation diagnostics (Task 2) ---")

outside = (traj < -1e-6) | (traj > L + 1e-6)
print("any particle ever outside the box?", outside.any())

# a "stuck at wall" particle: sits within 0.05 of a wall for >80% of the run
near_wall = (traj < 0.05) | (traj > L - 0.05)
stuck = (near_wall.all(axis=2)).mean(axis=0) > 0.8
print("particles stuck at a wall >80% of the time:", np.where(stuck)[0].tolist())

# an "unrealistic jump": frame-to-frame displacement bigger than 10x the median
step_disp = np.linalg.norm(np.diff(traj, axis=0), axis=2)   # (steps-1, N)
med = np.median(step_disp)
jumps = step_disp > 10 * med
print(f"median step displacement: {med:.4f}, any jump >10x median? {jumps.any()}"
      f" (count={jumps.sum()})")

# "unexpected clustering": are particles bunching up more than they started?
final_dist, _ = core.get_dist(traj[-1])
init_dist, _ = core.get_dist(traj[0])
iu = np.triu_indices(N, k=1)
print(f"mean pairwise distance: start={init_dist[iu].mean():.2f}, "
      f"end={final_dist[iu].mean():.2f} (r0={r0}, so clustering tighter than "
      f"r0 would be suspicious)")

# ---- the animation itself ----
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(0, L)
ax.set_ylim(0, L)
ax.set_aspect("equal")
ax.set_title("Atomic Toy Model: 16 particles, 500 steps")
scat = ax.scatter(traj[0, :, 0], traj[0, :, 1], s=80, c="tab:blue")
frame_text = ax.text(0.02, 0.96, "", transform=ax.transAxes, va="top")


def update(frame):
    scat.set_offsets(traj[frame])
    frame_text.set_text(f"step {frame}/{steps}")
    return scat, frame_text


ani = animation.FuncAnimation(fig, update, frames=steps, interval=30, blit=True)
ani.save("task2_animation.gif", writer="pillow", fps=30)
print("saved task2_animation.gif")

# static snapshots too, since a PDF/report can't show a moving GIF
snap_frames = [0, steps // 3, 2 * steps // 3, steps - 1]
fig2, axs = plt.subplots(1, 4, figsize=(14, 3.6))
for ax2, f in zip(axs, snap_frames):
    ax2.set_xlim(0, L)
    ax2.set_ylim(0, L)
    ax2.set_aspect("equal")
    ax2.scatter(traj[f, :, 0], traj[f, :, 1], s=60, c="tab:blue")
    ax2.set_title(f"step {f}")
plt.tight_layout()
plt.savefig("task2_snapshots.png", dpi=130)
print("saved task2_snapshots.png")
