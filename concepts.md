# NumPy & Python basics — build up from zero, then see it in sim.py

Rule for this doc: every concept gets a tiny standalone example FIRST (just 2-3 numbers, nothing to do with particles). Only AFTER you get the tiny example do we show the same idea inside `sim.py`.

---

## PART 1 — Python basics (no NumPy yet)

### 1.1 Variables
A variable is just a labeled box holding a value.
```python
x = 5
name = "atom"
```
`x` now means 5 until you change it.

### 1.2 Lists
A list is an ordered bunch of values in square brackets.
```python
scores = [10, 20, 30]
scores[0]   # 10  <- indexing starts at 0, not 1
scores[1]   # 20
```

### 1.3 Functions
A function is a mini recipe you can reuse. You give it inputs, it gives back an output.
```python
def double(x):
    return x * 2

double(5)   # 10
double(7)   # 14
```
Same recipe, different input, different output. That's the whole point — write it once, use it many times.

### 1.4 Loops
A loop repeats code without retyping it.
```python
for i in range(3):
    print(i)
# prints 0, then 1, then 2
```
`range(3)` just means "count 0, 1, 2" (3 numbers, starting at 0).

### 1.5 `for` over a list
```python
for s in scores:
    print(s)
# prints 10, then 20, then 30
```

That's it for plain Python — nothing fancy. Now the actual topic.

---

## PART 2 — NumPy from absolute zero

### 2.1 Why NumPy exists at all
A plain Python list is bad at math. Watch:
```python
a = [1, 2, 3]
a * 2        # [1, 2, 3, 1, 2, 3]   <- NOT what you want!
```
It just repeated the list. Python lists don't know how to "do math to every item" automatically.

NumPy fixes this. A NumPy array DOES know how to do math to every item at once.
```python
import numpy as np

a = np.array([1, 2, 3])
a * 2        # array([2, 4, 6])    <- yes! this is what you want
```
That's the ENTIRE reason NumPy exists: so you can write `a * 2` and have it apply to every number, instead of writing a loop yourself.

### 2.2 Making an array
```python
a = np.array([1, 2, 3])
```
Just wrap a normal Python list in `np.array(...)` and now it's a NumPy array.

### 2.3 Doing math on a whole array at once
```python
a = np.array([1, 2, 3])
a + 10      # array([11, 12, 13])   -> added 10 to every element
a * 2       # array([2, 4, 6])      -> multiplied every element by 2
a ** 2      # array([1, 4, 9])      -> squared every element
```
No loop written by you. NumPy loops internally, you just say what math to do.

### 2.4 Two arrays together
```python
a = np.array([1, 2, 3])
b = np.array([10, 20, 30])
a + b       # array([11, 22, 33])   -> adds them position by position
```
1 pairs with 10, 2 pairs with 20, 3 pairs with 30. Same-position elements combine.

### 2.5 Shape — rows and columns
A 1D array is just a single line of numbers:
```python
a = np.array([1, 2, 3])
a.shape     # (3,)   -> 3 numbers in a single row
```
A 2D array is a grid — rows and columns, like a spreadsheet:
```python
b = np.array([[1, 2],
              [3, 4],
              [5, 6]])
b.shape     # (3, 2)  -> 3 rows, 2 columns
```
Read shape `(3, 2)` as "3 rows, 2 columns." In `sim.py`, positions are stored as shape `(N, 2)` — N rows (one per particle), 2 columns (x and y). So particle 0's position is `pos[0]` → `[x0, y0]`.

### 2.6 Indexing — grabbing pieces
```python
b = np.array([[1, 2],
              [3, 4],
              [5, 6]])

b[0]        # array([1, 2])   -> row 0, the whole first row
b[0, 0]     # 1                -> row 0, column 0
b[:, 0]     # array([1, 3, 5]) -> ALL rows, column 0 only
b[:, 1]     # array([2, 4, 6]) -> ALL rows, column 1 only
```
The `:` means "give me everything along this direction." `b[:, 0]` reads as "every row, but only column 0."

This is exactly how `sim.py` pulls out just the x-coordinates or just the y-coordinates:
```python
pos[:, 0]   # every particle's x position
pos[:, 1]   # every particle's y position
```

### 2.7 `axis` — which direction to squash when adding things up
```python
b = np.array([[1, 2],
              [3, 4],
              [5, 6]])

b.sum()            # 21           -> adds absolutely everything
b.sum(axis=0)      # [9, 12]      -> adds DOWN each column (1+3+5, 2+4+6)
b.sum(axis=1)      # [3, 7, 11]   -> adds ACROSS each row (1+2, 3+4, 5+6)
```
Memory trick: `axis=0` squashes rows together (goes down), `axis=1` squashes columns together (goes across). You pick the axis based on "which direction do I want to collapse into one number per row/column."

In `sim.py`, `forces.sum(axis=1)` adds up, for each particle (each row), all the force contributions coming from every other particle (the columns) — giving one final force per particle.

### 2.8 Boolean masks — True/False filters
Comparing an array to a number gives you True/False for each element:
```python
a = np.array([1, 5, 2, 8, 3])
mask = a > 3
mask        # array([False, True, False, True, False])
```
You can use that mask to grab only the matching values:
```python
a[mask]     # array([5, 8])
```
Or use `np.where` to pick between two options based on the mask:
```python
np.where(mask, a, 0)     # array([0, 5, 0, 8, 0])
```
Reads as: "wherever mask is True, keep the real value from `a`; wherever False, use 0 instead."

In `sim.py`:
```python
mask = dist < rc          # True where two particles are close enough to matter
mag = np.where(mask, mag, 0.0)   # keep the real force if neighbors, else force = 0
```

### 2.9 `np.fill_diagonal` — editing just the diagonal
The "diagonal" of a square grid is the line from top-left to bottom-right (row 0/col 0, row 1/col 1, row 2/col 2...).
```python
m = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])
np.fill_diagonal(m, 0)
m
# [[0, 2, 3],
#  [4, 0, 6],
#  [7, 8, 0]]
```
It replaced 1, 5, 9 (the diagonal) with 0, left everything else untouched.

In `sim.py`, the diagonal of the distance grid is "particle compared to itself" (always distance 0). We force those diagonal spots to `False` in the neighbor mask so a particle never counts itself as its own neighbor.

### 2.10 `np.clip` — keeping numbers inside a range
```python
a = np.array([-5, 3, 20, 8])
np.clip(a, 0, 10)     # array([0, 3, 10, 8])
```
Anything below 0 gets pushed up to 0. Anything above 10 gets pushed down to 10. Everything in between is untouched.

In `sim.py`, this keeps a particle's position from ever showing as outside the box, after a wall bounce.

### 2.11 Broadcasting — the trickiest one, so we build it slowly

**Step A — the easy broadcasting you already saw:**
```python
a = np.array([1, 2, 3])
a + 10      # array([11, 12, 13])
```
`10` isn't an array, it's just one number, but NumPy "stretches" it to match `a`'s shape and adds it to every element. That stretching behavior is called **broadcasting**.

**Step B — a small 2D example, no particles yet.**
Say you have 3 people's heights and you want the height DIFFERENCE between every pair of people (person i vs person j), all at once — not one pair at a time with a loop.
```python
heights = np.array([160, 170, 180])   # shape (3,)

col = heights[:, None]    # shape (3, 1) -> stretched into a column
row = heights[None, :]    # shape (1, 3) -> stretched into a row

diff = col - row
diff
# [[  0, -10, -20],
#  [ 10,   0, -10],
#  [ 20,  10,   0]]
```
`heights[:, None]` takes the flat list and stands it up as a column. `heights[None, :]` lays the same flat list across as a row. When you subtract a column-shape from a row-shape, NumPy lines up every row against every column and fills in the ENTIRE grid at once — that's every pairwise difference, computed in one line, with zero loops.

`diff[i, j]` = height of person i minus height of person j. Check: `diff[0,1] = 160-170 = -10`. Matches the grid above.

**Step C — now the real thing in `sim.py`:**
```python
diff = pos[:, None, :] - pos[None, :, :]
```
Same exact trick as Step B, just with (x, y) pairs instead of single height numbers. `pos` has shape `(N, 2)`. `pos[:, None, :]` becomes shape `(N, 1, 2)` (stood up as a column of points), `pos[None, :, :]` becomes shape `(1, N, 2)` (laid across as a row of points). Subtracting gives shape `(N, N, 2)` — for every pair (i, j), the full (x, y) difference vector, all computed in one shot.

Then:
```python
dist = np.linalg.norm(diff, axis=-1)
```
`np.linalg.norm` turns an (x, y) vector into a single length number (Pythagoras: `sqrt(x² + y²)`). `axis=-1` tells it "the (x,y) pair is the LAST axis of this array, squash just that into one number." Do that for every cell in the `(N, N, 2)` grid and you get an `(N, N)` grid of plain distances.

**Why this replaces a loop:** without broadcasting, you'd write:
```python
for i in range(N):
    for j in range(N):
        dist[i, j] = distance between particle i and particle j
```
Broadcasting does the exact same computation, just handed to NumPy's fast internal code instead of a slow Python double-loop.

### 2.12 Returning multiple values from a function
```python
def split(x):
    return x - 1, x + 1

a, b = split(10)
a   # 9
b   # 11
```
Python lets a function hand back several values at once, separated by commas, and you can "unpack" them into separate variable names on the other side.

In `sim.py`:
```python
def one_step(pos, vel):
    ...
    return new_pos, new_vel, forces2, dist2, mask2

pos, vel, forces, dist, mask = one_step(pos, vel)
```
Same idea, just 5 things coming back instead of 2.

---

## PART 3 — the one-sentence summary

Every "loop-shaped" task in `sim.py` (comparing every particle to every other particle, filtering by distance, adding up forces) got written as a whole-array NumPy operation instead of a nested loop. That's called **vectorization**, and it's faster because NumPy does the repetition in fast internal code instead of Python doing it one number at a time.

If Part 2 makes sense, go re-read `sim.py` — every line should now map back to one of the sections above.
