"""
Task 7 - memory cost of the vectorized (N,N,2) displacement array, theory vs
measured, and where it stops being practical.
"""

import time
import numpy as np
import core

Ns = [100, 1000, 5000, 10000]


def theory_bytes(n, itemsize):
    return n * n * 2 * itemsize


print(f"{'N':>7} {'dtype':>9} {'theory (MB)':>13} {'measured (MB)':>15} {'match?':>8}")
rows = []
for N in Ns:
    for dtype in (np.float32, np.float64):
        itemsize = np.dtype(dtype).itemsize
        theory = theory_bytes(N, itemsize)
        if N <= 5000:
            # actually build the array and read numpy's own nbytes
            pos = np.zeros((N, 2), dtype=dtype)
            diff = pos[:, None, :] - pos[None, :, :]
            measured = diff.nbytes
            match = measured == theory
            del diff
        else:
            # 10000^2 * 2 * 8 bytes = 1.6 GB just for this one array, and the
            # force calc needs several more temporaries alongside it (dist,
            # mask, direction, mag...) at the same time - too much to safely
            # allocate here, so this row is theoretical only.
            measured, match = None, "n/a"
        rows.append((N, dtype.__name__, theory, measured, match))
        m_str = f"{measured/1e6:>15.1f}" if measured is not None else f"{'(not built)':>15}"
        print(f"{N:>7} {dtype.__name__:>9} {theory/1e6:>13.1f} {m_str} {str(match):>8}")

print("\n--- timing the actual force calculation at increasing N, until it hurts ---")
print(f"{'N':>7} {'time (s)':>10} {'approx RAM for temporaries (MB)':>32}")
for N in (100, 500, 1000, 2000, 4000):
    pos, _ = core.init_state(N, 10.0 * (N / 16) ** 0.5)
    t0 = time.perf_counter()
    core.compute_forces(pos, 3.0, 1.5, 2.5)
    dt_ = time.perf_counter() - t0
    # compute_forces builds: diff (N,N,2), dist (N,N), mask (N,N bool),
    # safe_dist (N,N), direction (N,N,2), mag (N,N) - roughly 6x an (N,N) float64
    approx_ram = (2 * N * N * 8) + 4 * (N * N * 8) + (N * N * 1)
    print(f"{N:>7} {dt_:>10.4f} {approx_ram/1e6:>32.1f}")

print("\nconclusion: memory grows as N^2, not N. Doubling N roughly quadruples "
      "both the memory and the time for the fully vectorized approach. On this "
      "machine, N=10000 would need ~1.6 GB just for the displacement array, "
      "plus several more same-sized temporaries during compute_forces - that's "
      "when the fully vectorized method stops being practical, well before any "
      "single array hits a hardware limit.")
