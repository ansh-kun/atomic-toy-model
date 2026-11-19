import matplotlib.pyplot as plt
import numpy as np

plt.xkcd(scale=1, length=100, randomness=2)

fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis("off")

center = (7, 5)

branches = [
    ("Baseline sim\n(positions, walls,\nforces, energy)", 2.0, 8.3),
    ("Check it works\n(distances, neighbors,\nforces ~0)", 5.3, 9.3),
    ("Animation\n(watch it run,\nspot bugs)", 9.3, 9.1),
    ("Energy + dt\n(K, U, E_total,\ntry different dt)", 12.3, 7.3),
    ("Add friction\n(drag force,\ndoes it settle?)", 12.6, 3.6),
    ("float32 vs float64\n(speed vs accuracy)", 9.6, 1.2),
    ("Speed test\n(loop vs numpy\nvs C)", 5.8, 0.6),
    ("Memory check\n(when does it\nget too big?)", 2.1, 1.9),
    ("Our own twist\n(one upgrade,\nprove it helps)", 0.9, 5.0),
]

def wobble_line(ax, p1, p2, color="black", lw=2):
    x1, y1 = p1
    x2, y2 = p2
    xm, ym = (x1 + x2) / 2 + np.random.uniform(-0.3, 0.3), (y1 + y2) / 2 + np.random.uniform(-0.3, 0.3)
    t = np.linspace(0, 1, 30)
    x = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * xm + t ** 2 * x2
    y = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * ym + t ** 2 * y2
    ax.plot(x, y, color=color, lw=lw, zorder=1)

np.random.seed(3)
for text, bx, by in branches:
    wobble_line(ax, center, (bx, by))

for i, (text, bx, by) in enumerate(branches):
    box = dict(boxstyle="round,pad=0.5,rounding_size=0.8", fc="white", ec="black", lw=2)
    ax.text(bx, by, text, ha="center", va="center", fontsize=12, bbox=box, zorder=3,
            family="fantasy")

center_box = dict(boxstyle="round,pad=0.7,rounding_size=0.9", fc="#fff7cc", ec="black", lw=2.5)
ax.text(*center, "ATOMIC TOY\nMODEL", ha="center", va="center", fontsize=18,
        weight="bold", bbox=center_box, zorder=4, family="fantasy")

ax.text(7, 0.05, "SciComp project · particles in a box", ha="center", fontsize=10,
        style="italic", family="fantasy")

plt.tight_layout()
plt.savefig(__import__("pathlib").Path(__file__).resolve().parent / "mindmap.png", dpi=150, facecolor="white")
print("saved")
