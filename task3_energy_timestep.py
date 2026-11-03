"""
Task 3 - energy conservation and timestep accuracy.
Same initial config, several dt values, K/U/E_total each, max relative drift,
and simple (Euler) vs smoother (velocity-Verlet) integration.
"""

import numpy as np
import matplotlib.pyplot as plt
import core

N, L, rc, k, r0, mass = 16, 10.0, 3.0, 1.5, 2.5, 1.0
T = 2.5   # total simulated time, same for every dt so runs are comparable
dts = [0.05, 0.02, 0.01, 0.005]

fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharey=False)
drift_table = []

for ax, dt in zip(axes.flat, dts):
    pos, vel = core.init_state(N, L)   # same seed -> same start every time
    steps = int(round(T / dt))
    out = core.run("verlet", pos, vel, steps, dt, L, rc, k, r0, mass)
    K, U = out["K"], out["U"]
    E = K + U
    drift = np.abs((E - E[0]) / E[0]).max()
    drift_table.append((dt, steps, drift))

    t = np.arange(steps) * dt
    ax.plot(t, K, label="K", lw=1)
    ax.plot(t, U, label="U", lw=1)
    ax.plot(t, E, label="E_total", lw=1.5, color="k")
    ax.set_title(f"dt = {dt}  (max drift = {drift:.1%})")
    ax.set_xlabel("time")
    ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig("task3_energy_vs_dt.png", dpi=130)
print("saved task3_energy_vs_dt.png")

print("\n--- max relative energy drift, epsilon_E_max, per dt ---")
print(f"{'dt':>8} {'steps':>8} {'eps_E_max':>12}")
for dt, steps, drift in drift_table:
    print(f"{dt:>8} {steps:>8} {drift:>12.2%}")

# which is the largest defensible dt? pick the threshold and say so explicitly.
THRESH = 0.10
ok = [dt for dt, _, drift in drift_table if drift <= THRESH]
largest_ok = max(ok) if ok else None
print(f"\nusing a {THRESH:.0%} drift threshold, the largest defensible dt here is: "
      f"{largest_ok}")

# ---- Euler vs Verlet, same dt, same start ----
dt_compare = 0.02
steps_compare = int(round(T / dt_compare))
results = {}
for method in ("euler", "verlet"):
    pos, vel = core.init_state(N, L)
    out = core.run(method, pos, vel, steps_compare, dt_compare, L, rc, k, r0, mass)
    E = out["K"] + out["U"]
    results[method] = E

t = np.arange(steps_compare) * dt_compare
plt.figure(figsize=(7, 4.5))
for method, E in results.items():
    drift = np.abs((E - E[0]) / E[0]).max()
    plt.plot(t, E, label=f"{method} (max drift {drift:.1%})")
plt.xlabel("time")
plt.ylabel("E_total")
plt.title(f"Euler vs velocity-Verlet, dt = {dt_compare}")
plt.legend()
plt.tight_layout()
plt.savefig("task3_euler_vs_verlet.png", dpi=130)
print("saved task3_euler_vs_verlet.png")

for method, E in results.items():
    drift = np.abs((E - E[0]) / E[0]).max()
    print(f"{method}: max drift at dt={dt_compare} is {drift:.2%}")
