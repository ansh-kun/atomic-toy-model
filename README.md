# Atomic Toy Model — Project Submission

Fundamentals of Scientific Computing: Computational Thinking Project
Instructors: Prof. Anuj Goyal and Prof. Saswata Bhattacharyya
Group 8

## Details of members

| Name | Roll Number |
|------|------|
| Ansh Dadhore | CO26BTECH11003 |
| Deepak Kumar Singhadiya | CO26BTECH11005 |
| Purushottam Narayan | MS26BTECH11027 |
| Sajal Bajaj | MS26BTECH11029 |
| Boyanapelli Abhiram Rao | CO26BTECH11004 |

## Sequence of videos

- Video-1 Ansh.mp4
- Video-2 Deepak.mp4
- Video-3 Purushottam.mp4
- Video-4 Sajal.mp4
- Video-5 Abhiram.mp4

## Roles and responsibilities

- Ansh — Baseline simulator and verification (Task 1): particle model, wall reflection, forces, velocity-Verlet integration, and the numerical correctness checks
- Deepak — Trajectory animation (Task 2) and numerical precision study (Task 5): float32 vs float64
- Purushottam — Energy and timestep accuracy (Task 3) and memory/scalability analysis (Task 7)
- Sajal — Dissipation and relaxation (Task 4) and the innovation feature (Task 8)
- Abhiram — Computational efficiency and scaling (Task 6) and the final engineering recommendation (Task 9), plus report assembly

## Acknowledgment of AI usage

Which AI tools have been used and for what purpose

Claude — for code development and debugging

## Files shared

- README (this file)
- `REPORT.pdf` / `REPORT.docx` / `REPORT.html` — the full project report (Word + PDF): model, all 9 tasks, plots, tables, final recommendation
- `sim.py` — Task 1 baseline simulator (standalone, matches the report's Task 1 numbers)
- `core.py` — shared physics used by every task script, so the model is identical everywhere
- `task2_animation.py` ... `task8_innovation.py` — one script per task, each runs standalone and regenerates its own plot(s)
- `task9_final_recommendation.md` — Task 9 writeup
- `pair_forces.c` / `libpairforces.dylib` — the C implementation used in Task 6 (recompile with `cc -O2 -shared -fPIC -o libpairforces.dylib pair_forces.c` if needed)
- `mindmap.png`, `flowchart.png` — project plan visuals
- `Atomic-Toy-Model-Project-Plan.pptx/.pdf` — project plan slides
- `concepts.md`, `sim.md` — supporting notes
- Video files — not yet recorded
- Prompts and recorded AI sessions — not yet compiled

### How to run

```bash
cd atomic_toy_model
./venv/bin/pip install -r requirements.txt   # numpy, matplotlib, pillow
./venv/bin/python sim.py                     # Task 1
./venv/bin/python task2_animation.py         # ... through task8_innovation.py
./venv/bin/python build_report.py && soffice --headless --convert-to pdf REPORT.html
./venv/bin/python build_docx_report.py   # REPORT.docx
```
