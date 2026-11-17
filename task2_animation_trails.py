"""
Fancier version of the Task 2 animation, for the video only — not a graded
deliverable, task2_animation.py (the plain version) already satisfies that.
Particles colored by speed, with a short fading trail behind each one.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import core

N, L, rc, k, r0, dt, steps, mass = 16, 10.0, 3.0, 1.5, 2.5, 0.005, 500, 1.0
TRAIL = 25  # how many past frames to keep visible, fading out

pos, vel = core.init_state(N, L)
out = core.run("verlet", pos, vel, steps, dt, L, rc, k, r0, mass, record_traj=True)
traj = out["traj"]  # (steps, N, 2)

# speed per particle per frame, for coloring (finite difference of position)
speeds = np.linalg.norm(np.diff(traj, axis=0, prepend=traj[:1]), axis=2) / dt
vmax = speeds.max()

cmap = plt.cm.plasma
fig, ax = plt.subplots(figsize=(6, 6))


def style_axes():
    ax.set_facecolor("#0b0b12")
    fig.patch.set_facecolor("#0b0b12")
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("#333333")


def update(frame):
    ax.clear()
    style_axes()

    start = max(0, frame - TRAIL + 1)
    idxs = np.arange(start, frame + 1)
    n_t = len(idxs)

    pts = traj[idxs].reshape(-1, 2)                       # (n_t*N, 2)
    sp = speeds[idxs]                                      # (n_t, N)
    colors = cmap(np.clip(sp / vmax, 0, 1))                # (n_t, N, 4)

    age = (idxs - idxs.min()) / max(1, idxs.max() - idxs.min())   # 0 old -> 1 new
    colors[..., 3] = (0.05 + 0.9 * age)[:, None]           # fade older points out
    sizes = np.repeat(15 + 55 * age, N)                     # newer points drawn bigger

    ax.scatter(pts[:, 0], pts[:, 1], c=colors.reshape(-1, 4), s=sizes, linewidths=0)
    ax.text(0.02, 0.96, f"step {frame}/{steps}", transform=ax.transAxes,
            color="white", va="top", fontsize=9)
    return []


style_axes()
ani = animation.FuncAnimation(fig, update, frames=steps, interval=30)
ani.save("task2_animation_trails.gif", writer="pillow", fps=30)
print("saved task2_animation_trails.gif")
