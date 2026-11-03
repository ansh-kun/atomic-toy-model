"""
Task 6 - how fast is the pair-force calculation, three ways:
Python double loop, NumPy vectorized, compiled C.
Same positions for every method at a given N. 5 repeats, report the median.
"""

import ctypes
import time
import numpy as np
import matplotlib.pyplot as plt
import core

rc, k, r0 = 3.0, 1.5, 2.5
Ns = [50, 200, 500, 1000]
REPEATS = 5

lib = ctypes.CDLL("./libpairforces.dylib")
lib.pair_forces.argtypes = [
    ctypes.POINTER(ctypes.c_double), ctypes.c_int,
    ctypes.c_double, ctypes.c_double, ctypes.c_double,
    ctypes.POINTER(ctypes.c_double),
]


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


def forces_numpy(pos, rc, k, r0):
    forces, _, _ = core.compute_forces(pos, rc, k, r0)
    return forces


def forces_c(pos, rc, k, r0):
    n = len(pos)
    pos_flat = np.ascontiguousarray(pos, dtype=np.float64)
    out = np.zeros(2 * n, dtype=np.float64)
    lib.pair_forces(
        pos_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), n,
        rc, k, r0,
        out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
    )
    return out.reshape(n, 2)


def median_time(fn, pos, repeats=REPEATS):
    ts = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn(pos, rc, k, r0)
        ts.append(time.perf_counter() - t0)
    return float(np.median(ts))


methods = [("python loop", forces_python_loop), ("numpy", forces_numpy), ("C", forces_c)]
table = {name: [] for name, _ in methods}

print(f"{'N':>6} " + " ".join(f"{name:>16}" for name, _ in methods) +
      "    (seconds, median of 5)")
for N in Ns:
    pos, _ = core.init_state(N, 10.0 * (N / 16) ** 0.5)  # keep density roughly similar
    row = []
    # correctness check: all three must agree on this N before we trust the timing
    f_loop = forces_python_loop(pos, rc, k, r0)
    f_np = forces_numpy(pos, rc, k, r0)
    f_c = forces_c(pos, rc, k, r0)
    assert np.allclose(f_loop, f_np, atol=1e-8), "python loop vs numpy mismatch!"
    assert np.allclose(f_np, f_c, atol=1e-6), "numpy vs C mismatch!"

    for name, fn in methods:
        mt = median_time(fn, pos)
        table[name].append(mt)
        row.append(mt)
    print(f"{N:>6} " + " ".join(f"{v:>16.5f}" for v in row))

print("\nall three methods agree on the forces at every N (checked before timing)")

print("\n--- speedup relative to the python loop ---")
print(f"{'N':>6} {'numpy speedup':>15} {'C speedup':>12}")
for i, N in enumerate(Ns):
    base = table["python loop"][i]
    print(f"{N:>6} {base/table['numpy'][i]:>15.1f}x {base/table['C'][i]:>12.1f}x")

plt.figure(figsize=(6.5, 4.5))
for name, _ in methods:
    plt.plot(Ns, table[name], "o-", label=name)
plt.xlabel("N (number of particles)")
plt.ylabel("time (s, median of 5)")
plt.yscale("log")
plt.title("Pair-force calculation: wall-clock time vs N")
plt.legend()
plt.tight_layout()
plt.savefig("task6_efficiency.png", dpi=130)
print("saved task6_efficiency.png")

print("\n--- bottleneck ---")
print("python loop: the interpreter overhead of ~N^2 individual Python-level "
      "operations (attribute lookups, bounds checks) per call, not the actual math.")
print("numpy: builds a full (N,N,2) temporary array even for the pairs outside "
      "the cutoff, so it does ~N^2 work and allocates ~N^2 memory every call, "
      "just in fast compiled code instead of the Python interpreter.")
print("C: no python/numpy overhead at all, and no wasted temporaries; it's "
      "limited only by the raw N^2 floating point work.")
