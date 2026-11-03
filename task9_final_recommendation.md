# Task 9 — Final computational engineering recommendation

Every choice below is backed by a number produced in Tasks 3–8, not a guess.

| Choice | Recommendation | Evidence |
|---|---|---|
| Precision | **float64** for correctness-critical runs; float32 is fine if memory-constrained | Task 5: eps_pos = 6.6e-7 (float32 loses almost nothing in accuracy), memory exactly halves, but at N=16 there was no measured speed advantage — the win from float32 only shows up at the larger N where Task 6/7's O(N²) memory and bandwidth costs start to bite |
| Timestep (dt) | **dt = 0.01** | Task 3: drift was 8.1% at dt=0.05, 6.9% at dt=0.02, 5.4% at dt=0.01, and barely changed (5.4%) going to dt=0.005 — 0.01 is the largest step before you stop gaining accuracy for the extra compute |
| Integration method | **velocity-Verlet**, not Euler | Task 3: at the same dt=0.02, Euler drifted 10.6% vs Verlet's 6.9% — Verlet is free (same cost) and clearly better behaved |
| Force-calculation method | **NumPy vectorized up to a few hundred particles; cell list beyond that** | Task 6: NumPy is ~14x faster than a Python loop; Task 8: the cell list is ~22x faster than NumPy's own brute-force approach by N=5000, and is the only one of the three that still runs comfortably at N=10000 |
| Cutoff radius | **rc = 3.0** (kept as given) | Task 1 verification already confirms this cutoff gives a symmetric, self-exclusive neighbor set with net internal force ≈ 0; no evidence in later tasks suggested changing it |
| Dissipation parameter | **gamma = 0.1** for a visible, non-instant relaxation; gamma = 0.5 only if you want it visibly stopped inside a short demo | Task 4: gamma=0 barely decays (tau≈269), gamma=0.1 gives tau≈8.4 (settles in a demonstrable but not instant way), gamma=0.5 fully relaxes by t≈19 — 0.1 is the middle ground that still shows K↔U exchange before damping it out |
| Innovation | **cell-linked neighbor list** | Task 8: exact same forces as brute force (max difference 1.8e-15), but O(N) instead of O(N²) — directly fixes the N≈5,000–10,000 wall Task 7 identified for the vectorized approach |

## One-paragraph summary

For a system this size (tens to low hundreds of particles), float64 with dt=0.01, velocity-Verlet, and the plain NumPy vectorized force calculation is the simplest correct and fast-enough choice. The moment N climbs into the thousands, two things from Task 7 become real problems — the O(N²) memory for the pairwise array and the O(N²) time — and the cell-linked list from Task 8 is what actually fixes both, at no cost in accuracy. That is the central engineering lesson of this project: a method that looks fine at N=16 is not automatically the right method at N=10,000, and you only find out which one to use by actually measuring, not by guessing.
