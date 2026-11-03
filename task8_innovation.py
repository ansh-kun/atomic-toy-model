"""
Task 8 - innovation: a cell-linked neighbor list.

Task 7 showed the brute-force (N,N,2) approach is O(N^2) in both memory and
time, and gets impractical around N~5000-10000 on this machine. A cell list
fixes that: split the box into cells the size of the cutoff radius, and only
check each particle against the ~9 cells around it, instead of every other
particle. For a fixed particle density that makes it ~O(N) instead of O(N^2).
"""

import time
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import core

rc, k, r0 = 3.0, 1.5, 2.5


def cell_list_forces(pos, rc, k, r0, L):
    n = len(pos)
    cell_size = rc   # cells this size guarantee every pair within rc is found
                      # by checking only the 3x3 block of cells around each point
    ncells = max(1, int(L // cell_size) + 1)
    cell_of = np.clip((pos // cell_size).astype(int), 0, ncells - 1)

    cells = defaultdict(list)
    for i in range(n):
        cells[(cell_of[i, 0], cell_of[i, 1])].append(i)

    forces = np.zeros((n, 2))
    for i in range(n):
        cx, cy = cell_of[i]
        xi, yi = pos[i]
        fx = fy = 0.0
        for dcx in (-1, 0, 1):
            for dcy in (-1, 0, 1):
                for j in cells.get((cx + dcx, cy + dcy), ()):
                    if j == i:
                        continue
                    dx = xi - pos[j, 0]
                    dy = yi - pos[j, 1]
                    dist = (dx * dx + dy * dy) ** 0.5
                    if dist >= rc:
                        continue
                    mag = -k * (dist - r0)
                    safe = dist if dist != 0 else 1.0
                    fx += mag * dx / safe
                    fy += mag * dy / safe
        forces[i, 0] = fx
        forces[i, 1] = fy
    return forces


# ---- correctness: must match the brute-force result, not just be fast ----
pos, _ = core.init_state(200, 10.0 * (200 / 16) ** 0.5)
L_check = 10.0 * (200 / 16) ** 0.5
f_brute, _, _ = core.compute_forces(pos, rc, k, r0)
f_cell = cell_list_forces(pos, rc, k, r0, L_check)
err = np.abs(f_brute - f_cell).max()
print(f"correctness check (N=200): max force difference vs brute force = {err:.2e}")
assert err < 1e-8, "cell list doesn't match brute force!"
print("matches exactly (as it should: cell size == cutoff radius misses nothing)\n")

# ---- speed, at a fixed particle density so this is a fair O(N) vs O(N^2) test ----
Ns = [500, 1000, 2000, 5000, 10000]
REPEATS = 3
rows = []
for N in Ns:
    L = 10.0 * (N / 16) ** 0.5   # same density as every other task's N=16 baseline
    pos, _ = core.init_state(N, L)

    cell_times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        cell_list_forces(pos, rc, k, r0, L)
        cell_times.append(time.perf_counter() - t0)
    t_cell = float(np.median(cell_times))

    if N <= 5000:   # brute force beyond this risks the memory blowup from Task 7
        brute_times = []
        for _ in range(REPEATS):
            t0 = time.perf_counter()
            core.compute_forces(pos, rc, k, r0)
            brute_times.append(time.perf_counter() - t0)
        t_brute = float(np.median(brute_times))
    else:
        t_brute = None

    rows.append((N, t_cell, t_brute))
    if t_brute is not None:
        print(f"N={N:>6}: cell list = {t_cell:.4f}s, brute force = {t_brute:.4f}s, "
              f"speedup = {t_brute/t_cell:.1f}x")
    else:
        print(f"N={N:>6}: cell list = {t_cell:.4f}s, brute force = skipped "
              "(Task 7: too much memory to safely allocate here)")

plt.figure(figsize=(6.5, 4.5))
plt.plot([r[0] for r in rows], [r[1] for r in rows], "o-", label="cell list (ours)")
brute_Ns = [r[0] for r in rows if r[2] is not None]
brute_ts = [r[2] for r in rows if r[2] is not None]
plt.plot(brute_Ns, brute_ts, "o-", label="brute force (Task 1/6 method)")
plt.xlabel("N (particles, density held fixed)")
plt.ylabel("time (s, median of 3)")
plt.yscale("log")
plt.xscale("log")
plt.title("Innovation: cell list vs brute force")
plt.legend()
plt.tight_layout()
plt.savefig("task8_innovation.png", dpi=130)
print("\nsaved task8_innovation.png")

n5000 = next(r for r in rows if r[0] == 5000)
print(f"\nat N=5000: speedup = {n5000[2]/n5000[1]:.1f}x "
      "(and the cell list keeps running fine all the way to N=10000, "
      "right where Task 7 found the brute-force array becomes impractical)")
