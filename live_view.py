"""
Live view — opens a real window and runs the simulation in real time, instead
of saving to a GIF first. Close the window (or Ctrl+C in the terminal) to stop.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import core

N, L, rc, k, r0, dt, mass = 16, 10.0, 3.0, 1.5, 2.5, 0.005, 1.0

pos, vel = core.init_state(N, L)

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(0, L)
ax.set_ylim(0, L)
ax.set_aspect("equal")
ax.set_title("Atomic Toy Model — live")
scat = ax.scatter(pos[:, 0], pos[:, 1], s=80, c="tab:blue")
step_text = ax.text(0.02, 0.96, "", transform=ax.transAxes, va="top")

state = {"pos": pos, "vel": vel, "step": 0}


STEPS_PER_FRAME = 8  # run several physics steps between redraws, so motion looks faster


def update(frame):
    for _ in range(STEPS_PER_FRAME):
        out = core.verlet_step(state["pos"], state["vel"], dt, L, rc, k, r0, mass)
        state["pos"], state["vel"] = out[0], out[1]
        state["step"] += 1
    scat.set_offsets(state["pos"])
    step_text.set_text(f"step {state['step']}")
    return scat, step_text


ani = animation.FuncAnimation(fig, update, interval=15, blit=True, cache_frame_data=False)
plt.show()
