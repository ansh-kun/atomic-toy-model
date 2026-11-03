import numpy as np

np.random.seed(4)

N = 16
L = 10.0
rc = 3.0
k = 1.5
r0 = 2.5
dt = 0.005
steps = 500
mass = 1.0


def init_state(n, box):
    pos = np.random.uniform(0.5, box - 0.5, size=(n, 2))
    vel = np.random.uniform(-0.5, 0.5, size=(n, 2))
    return pos, vel


def get_dist(pos):
    diff = pos[:, None, :] - pos[None, :, :]
    dist = np.linalg.norm(diff, axis=-1)
    return dist, diff


def get_neighbors(dist):
    mask = dist < rc
    np.fill_diagonal(mask, False)  # khud apna neighbor nahi hota
    return mask


def compute_forces(pos):
    dist, diff = get_dist(pos)
    mask = get_neighbors(dist)

    safe_dist = np.where(dist == 0, 1.0, dist)  # taaki 0/0 na ho diagonal pe
    direction = diff / safe_dist[:, :, None]

    mag = -k * (dist - r0)
    mag = np.where(mask, mag, 0.0)

    f_pairs = mag[:, :, None] * direction
    forces = f_pairs.sum(axis=1)
    return forces, dist, mask


def get_U(dist, mask):
    u = 0.5 * k * (dist - r0) ** 2
    u = np.where(mask, u, 0.0)
    return u.sum() / 2.0  # matrix me har pair 2 baar aa raha hai isliye /2


def get_K(vel):
    return 0.5 * mass * np.sum(vel ** 2)


def bounce_walls(pos, vel):
    # simple wall bounce, velocity flip + clip position
    for d in range(2):
        low = pos[:, d] < 0
        high = pos[:, d] > L
        vel[low | high, d] *= -1
        pos[:, d] = np.clip(pos[:, d], 0, L)
    return pos, vel


def one_step(pos, vel):
    forces, dist, mask = compute_forces(pos)
    acc = forces / mass
    vel_half = vel + 0.5 * dt * acc

    new_pos = pos + dt * vel_half
    new_pos, vel_half = bounce_walls(new_pos, vel_half)

    forces2, dist2, mask2 = compute_forces(new_pos)
    acc2 = forces2 / mass
    new_vel = vel_half + 0.5 * dt * acc2

    return new_pos, new_vel, forces2, dist2, mask2


def run_sim():
    pos, vel = init_state(N, L)
    K_list = np.zeros(steps)
    U_list = np.zeros(steps)

    for t in range(steps):
        pos, vel, forces, dist, mask = one_step(pos, vel)
        K_list[t] = get_K(vel)
        U_list[t] = get_U(dist, mask)

    return K_list, U_list, pos, vel, forces, dist, mask


def check_everything(dist, mask, pos, forces):
    # not gonna just say "it works", putting actual numbers here
    print("--- verification checks ---")

    sym_err = np.linalg.norm(dist - dist.T)
    print("distance matrix symmetric? err =", sym_err)

    print("max diagonal dist (shud be 0):", np.diag(dist).max())

    print("self counted as neighbor anywhere?", np.diag(mask).any())

    inside_box = ((pos >= -1e-8) & (pos <= L + 1e-8)).all()
    print("everyone inside the box?", inside_box)

    net_f = np.linalg.norm(forces.sum(axis=0))
    print("total force norm (~0 expected):", net_f)


if __name__ == "__main__":
    K, U, pos, vel, forces, dist, mask = run_sim()
    E = K + U
    drift = np.abs((E - E[0]) / E[0]).max()

    print(f"N = {N}, steps = {steps}")
    print("K0, U0, E0 =", K[0], U[0], E[0])
    print("K_end, U_end, E_end =", K[-1], U[-1], E[-1])
    print("max energy drift:", drift)
    print()

    check_everything(dist, mask, pos, forces)
