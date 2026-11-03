"""
Shared physics, same model as sim.py (Task 1), but with everything passed in
as arguments instead of hardcoded globals. Tasks 2-9 import this so the model
is identical everywhere and we don't copy-paste bugs around.

Defaults below match sim.py exactly, so Task 1's numbers reproduce if you
call these with no overrides.
"""

import numpy as np

DEFAULTS = dict(N=16, L=10.0, rc=3.0, k=1.5, r0=2.5, dt=0.005, steps=500, mass=1.0)


def init_state(n, box, seed=4, vel_scale=0.5, margin=0.5, dtype=np.float64):
    rng = np.random.default_rng(seed)
    pos = rng.uniform(margin, box - margin, size=(n, 2)).astype(dtype)
    vel = rng.uniform(-vel_scale, vel_scale, size=(n, 2)).astype(dtype)
    return pos, vel


def get_dist(pos):
    diff = pos[:, None, :] - pos[None, :, :]
    dist = np.linalg.norm(diff, axis=-1)
    return dist, diff


def get_neighbors(dist, rc):
    mask = dist < rc
    np.fill_diagonal(mask, False)
    return mask


def compute_forces(pos, rc, k, r0):
    dist, diff = get_dist(pos)
    mask = get_neighbors(dist, rc)
    safe_dist = np.where(dist == 0, 1.0, dist)
    direction = diff / safe_dist[:, :, None]
    mag = -k * (dist - r0)
    mag = np.where(mask, mag, 0.0)
    forces = (mag[:, :, None] * direction).sum(axis=1)
    return forces, dist, mask


def get_U(dist, mask, k, r0):
    u = 0.5 * k * (dist - r0) ** 2
    u = np.where(mask, u, 0.0)
    return u.sum() / 2.0


def get_K(vel, mass):
    return 0.5 * mass * np.sum(vel ** 2)


def bounce_walls(pos, vel, L):
    for d in range(2):
        low = pos[:, d] < 0
        high = pos[:, d] > L
        vel[low | high, d] *= -1
        pos[:, d] = np.clip(pos[:, d], 0, L)
    return pos, vel


def verlet_step(pos, vel, dt, L, rc, k, r0, mass, gamma=0.0):
    """Velocity-Verlet, with an optional viscous drag -gamma*v added to the
    spring force (Task 4). gamma=0 reproduces Task 1's integrator exactly."""
    forces, dist, mask = compute_forces(pos, rc, k, r0)
    forces = forces - gamma * vel
    acc = forces / mass
    vel_half = vel + 0.5 * dt * acc

    new_pos = pos + dt * vel_half
    new_pos, vel_half = bounce_walls(new_pos, vel_half, L)

    forces2, dist2, mask2 = compute_forces(new_pos, rc, k, r0)
    forces2 = forces2 - gamma * vel_half
    acc2 = forces2 / mass
    new_vel = vel_half + 0.5 * dt * acc2

    return new_pos, new_vel, forces2, dist2, mask2


def euler_step(pos, vel, dt, L, rc, k, r0, mass, gamma=0.0):
    """Plain (forward) Euler: for Task 3's integrator comparison."""
    forces, dist, mask = compute_forces(pos, rc, k, r0)
    forces = forces - gamma * vel
    acc = forces / mass
    new_pos = pos + dt * vel
    new_vel = vel + dt * acc
    new_pos, new_vel = bounce_walls(new_pos, new_vel, L)
    return new_pos, new_vel, forces, dist, mask


def run(method, pos, vel, steps, dt, L, rc, k, r0, mass, gamma=0.0, record_traj=False):
    """Runs `steps` steps of the given method ("verlet" or "euler"), logging
    K, U each step. Returns K, U arrays and (optionally) the trajectory."""
    step_fn = verlet_step if method == "verlet" else euler_step
    K = np.zeros(steps)
    U = np.zeros(steps)
    traj = np.zeros((steps, *pos.shape)) if record_traj else None
    for t in range(steps):
        pos, vel, forces, dist, mask = step_fn(pos, vel, dt, L, rc, k, r0, mass, gamma)
        K[t] = get_K(vel, mass)
        U[t] = get_U(dist, mask, k, r0)
        if record_traj:
            traj[t] = pos
    out = dict(K=K, U=U, pos=pos, vel=vel, forces=forces, dist=dist, mask=mask)
    if record_traj:
        out["traj"] = traj
    return out
