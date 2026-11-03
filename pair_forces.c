/* Task 6 - the same pair-force calculation as core.py's compute_forces,
 * written as a plain O(N^2) double loop in C, for a fair three-way speed
 * comparison (Python loop vs NumPy vs this). */
#include <math.h>

void pair_forces(const double *pos, int n, double rc, double k, double r0,
                  double *forces) {
    for (int i = 0; i < n; i++) {
        forces[2 * i] = 0.0;
        forces[2 * i + 1] = 0.0;
    }
    for (int i = 0; i < n; i++) {
        double xi = pos[2 * i], yi = pos[2 * i + 1];
        for (int j = 0; j < n; j++) {
            if (i == j) continue;
            double dx = xi - pos[2 * j];
            double dy = yi - pos[2 * j + 1];
            double dist = sqrt(dx * dx + dy * dy);
            if (dist >= rc) continue;
            double mag = -k * (dist - r0);
            double safe = dist == 0.0 ? 1.0 : dist;
            forces[2 * i]     += mag * dx / safe;
            forces[2 * i + 1] += mag * dy / safe;
        }
    }
}
