import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.xkcd(scale=1, length=100, randomness=2)

fig, ax = plt.subplots(figsize=(6, 12))
ax.set_xlim(0, 6)
ax.set_ylim(0, 24)
ax.axis("off")

steps = [
    "Start",
    "Set up particles\n(random positions,\nrandom velocities)",
    "Find distance between\nevery pair of particles",
    "Who's a neighbor?\n(cutoff radius, no self)",
    "Add up spring forces\nfrom neighbors",
    "Move everyone one\ntiny time step\n(velocity-Verlet)",
    "Hit a wall?\nBounce back",
    "Save K, U, E\nfor this step",
    "Done 500 steps?",
    "Plot energy,\ncheck the numbers",
    "End",
]

np.random.seed(7)
n = len(steps)
ys = np.linspace(22, 1, n)
cx = 3

for i, (text, y) in enumerate(zip(steps, ys)):
    is_decision = "?" in text
    is_end = text in ("Start", "End")
    if is_end:
        box = dict(boxstyle="round,pad=0.6,rounding_size=1.0", fc="#fff7cc", ec="black", lw=2.5)
    elif is_decision:
        box = dict(boxstyle="round,pad=0.5,rounding_size=0.3", fc="#e8f4ff", ec="black", lw=2)
    else:
        box = dict(boxstyle="round,pad=0.5,rounding_size=0.6", fc="white", ec="black", lw=2)
    ax.text(cx, y, text, ha="center", va="center", fontsize=12, bbox=box, zorder=3, family="fantasy")

# arrows straight down, a little wobble
for i in range(n - 1):
    y1, y2 = ys[i] - 0.9, ys[i + 1] + 0.9
    x = cx + np.random.uniform(-0.05, 0.05)
    ax.annotate("", xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle="->", lw=2, color="black",
                                connectionstyle="arc3,rad=0.02"))

# loop-back arrow from "Done 500 steps?" (index 8) back up to "Find distance..." (index 2) when "no"
y_from = ys[8]
y_to = ys[2]
x_loop = cx + 1.7
ax.plot([cx + 1.3, x_loop, x_loop, cx + 1.3],
        [y_from, y_from, y_to, y_to],
        color="black", lw=2)
ax.annotate("", xy=(cx + 1.05, y_to), xytext=(cx + 1.2, y_to),
            arrowprops=dict(arrowstyle="->", lw=2, color="black"))
ax.text(x_loop + 0.15, (y_from + y_to) / 2, "no, keep\ngoing", fontsize=10,
        family="fantasy", rotation=90, ha="center", va="center")
ax.text(cx + 1.0, y_from - 0.55, "yes", fontsize=10, family="fantasy")

ax.text(cx, 0.2, "Atomic Toy Model — one simulation step", ha="center", fontsize=10,
        style="italic", family="fantasy")

plt.tight_layout()
plt.savefig("/Users/ansh/atomic_toy_model/flowchart.png", dpi=150, facecolor="white")
print("saved")
