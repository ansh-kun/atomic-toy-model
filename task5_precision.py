"""
Task 5 - float32 vs float64. Memory, speed, energy behaviour, trajectory
difference. Same initial config (same seed), just cast to different dtype.
"""

import time
import numpy as np
import matplotlib.pyplot as plt
import core

N, L, rc, k, r0, dt, mass = 16, 10.0, 3.0, 1.5, 2.5, 0.005, 1.0
steps = 500
REPEATS = 5

results = {}
for dtype in (np.float32, np.float64):
    pos, vel = core.init_state(N, L, dtype=dtype)
    mem_bytes = pos.nbytes + vel.nbytes

    # time it: repeat the whole run a few times, take the median
    times = []
    for _ in range(REPEATS):
        p, v = pos.copy(), vel.copy()
        t0 = time.perf_counter()
        out = core.run("verlet", p, v, steps, dtype(dt), L, rc, k, r0, mass, record_traj=True)
        times.append(time.perf_counter() - t0)
    median_time = float(np.median(times))

    E = out["K"] + out["U"]
    drift = float(np.abs((E - E[0]) / E[0]).max())

    results[dtype] = dict(mem=mem_bytes, time=median_time, drift=drift,
                           traj=out["traj"], E=E)
    print(f"{dtype.__name__}: pos+vel memory = {mem_bytes} bytes, "
          f"median run time over {REPEATS} = {median_time*1000:.2f} ms, "
          f"max energy drift = {drift:.2%}")

mem_ratio = results[np.float64]["mem"] / results[np.float32]["mem"]
print(f"\nmemory ratio (float64 / float32) for the state arrays: {mem_ratio:.2f}x "
      "(exactly 2x is expected: float64 is twice the bytes per number)")

x32 = results[np.float32]["traj"][-1].astype(np.float64)
x64 = results[np.float64]["traj"][-1]
eps_pos = np.linalg.norm(x32 - x64) / np.linalg.norm(x64)
print(f"final-position relative difference, eps_pos = {eps_pos:.3e}")

speedup = results[np.float64]["time"] / results[np.float32]["time"]
print(f"speed: float32 is {speedup:.2f}x the float64 run time "
      f"(>1 means float32 was faster)")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
t = np.arange(steps) * dt
for dtype, style in ((np.float32, "--"), (np.float64, "-")):
    axes[0].plot(t, results[dtype]["E"], style, label=dtype.__name__)
axes[0].set_title("E_total: float32 vs float64")
axes[0].set_xlabel("time")
axes[0].legend()

traj32 = results[np.float32]["traj"].astype(np.float64)
traj64 = results[np.float64]["traj"]
pos_err = np.linalg.norm(traj32 - traj64, axis=2).mean(axis=1)
axes[1].plot(t, pos_err)
axes[1].set_title("mean position difference (float32 vs float64) over time")
axes[1].set_xlabel("time")
axes[1].set_ylabel("|x32 - x64|")

plt.tight_layout()
plt.savefig("task5_precision.png", dpi=130)
print("saved task5_precision.png")
