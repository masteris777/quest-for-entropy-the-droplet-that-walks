"""A walking droplet in ~40 lines of physics: the standard path-memory model, as a toy.

    python walker_toy.py            # smoke sweep + render the gif
    python walker_toy.py sweep      # smoke sweep only (fast)

The model is the discrete path-memory picture the field itself uses (Fort et al., PNAS
2010; the continuous version is Oza, Rosales & Bush, J. Fluid Mech. 2013): each bounce
stamps a standing circular ripple J0(k r) on the bath; the ripples fade with age at the
memory rate; the droplet is kicked downhill off the summed surface, with drag.

    h(x) = sum over past bounces m of  exp(-(n-m)/M) * J0(k |x - x_m|)
    v   <- (1 - drag) * (v + C * sum_m exp(-(n-m)/M) * J1(k r_m) * rhat_m)
    x   <- x + v

One knob matters: M, the memory (bounces until a ripple has faded to 1/e).

WHAT THE TOY MUST SHOW (frozen before tuning was accepted)
  T1  Low memory: the droplet stays put - bouncing in place, rings fading, no walk.
  T2  High memory: the same droplet with the same nudge STARTS WALKING BY ITSELF, and the
      walk is steady and straight (speed settles to a constant; direction stops wandering).
  T3  The onset is a threshold in M, not a smooth fade-in.

This is a toy of the MECHANISM, not a calibrated reproduction of any experiment. No
number out of it is comparable to a lab number.
"""

import sys
from pathlib import Path

import numpy as np
from scipy.special import j0, j1

HERE = Path(__file__).resolve().parent
ASSETS = HERE                      # the gif is written beside this script

K = 2.0 * np.pi          # Faraday wavelength = 1
C = 0.004                # kick strength per bounce
DRAG = 0.10
NOISE = 2e-4             # tiny nudge, first 10 bounces only
N_BOUNCE = 900


def run(M, seed=7):
    rng = np.random.default_rng(seed)
    window = int(min(8 * M, 260))
    x = np.zeros(2)
    v = np.zeros(2)
    past = []
    traj = [x.copy()]
    for n in range(N_BOUNCE):
        f = np.zeros(2)
        for age, xm in enumerate(reversed(past[-window:])):
            d = x - xm
            r = float(np.hypot(*d))
            if r > 1e-9:
                f += np.exp(-age / M) * j1(K * r) * d / r
        v = (1.0 - DRAG) * (v + C * f)
        if n < 10:
            v += NOISE * rng.standard_normal(2)
        past.append(x.copy())
        x = x + v
        traj.append(x.copy())
    return np.array(traj)


def speed_tail(traj):
    steps = np.linalg.norm(np.diff(traj, axis=0), axis=1)
    tail = steps[-200:]
    return float(tail.mean()), float(tail.std())


def straightness(traj):
    seg = np.diff(traj[-300:], axis=0)
    seg = seg[np.linalg.norm(seg, axis=1) > 1e-12]
    if len(seg) < 10:
        return float("nan")
    ang = np.unwrap(np.arctan2(seg[:, 1], seg[:, 0]))
    return float(np.ptp(ang))


def field(x_grid, y_grid, past, M, n):
    window = int(min(8 * M, 260))
    h = np.zeros_like(x_grid)
    for age, xm in enumerate(reversed(past[max(0, n - window):n])):
        r = np.hypot(x_grid - xm[0], y_grid - xm[1])
        h += np.exp(-age / M) * j0(K * r)
    return h


def render(m_lo, m_hi):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    from matplotlib.colors import LinearSegmentedColormap

    oil = LinearSegmentedColormap.from_list(
        "oil", ["#0a1a33", "#123055", "#2a6a8f", "#7fc6cf", "#eafcff"])

    t_lo, t_hi = run(m_lo), run(m_hi)

    # FIXED cameras. A co-moving camera pins the droplet to frame centre, which hides the
    # one thing the gif exists to show (caught by the user on the first cut). Instead the
    # animation stops when the walker has crossed ~11 wavelengths, and its panel's window
    # is sized to that whole segment, so the dot visibly travels across the frame.
    n0 = 40
    disp = np.linalg.norm(t_hi - t_hi[n0], axis=1)
    beyond = np.nonzero(disp > 11.0)[0]
    n_end = int(beyond[0]) if len(beyond) else N_BOUNCE
    frames = range(n0, n_end, 4)

    seg = t_hi[n0:n_end]
    cx, cy = seg.mean(axis=0)
    hs = float(max(np.abs(seg - [cx, cy]).max() + 2.2, 5.0))
    grids = []
    for centre, half in (((0.0, 0.0), 4.2), ((cx, cy), hs)):
        g1 = np.linspace(centre[0] - half, centre[0] + half, 300)
        g2 = np.linspace(centre[1] - half, centre[1] + half, 300)
        Xg, Yg = np.meshgrid(g1, g2)
        grids.append((Xg, Yg, (g1[0], g1[-1], g2[0], g2[-1])))

    fig, ax = plt.subplots(1, 2, figsize=(9.6, 5.0), facecolor="#0a1024")
    for a, title in zip(ax, (f"short memory (M = {m_lo})\nit just sits there",
                             f"long memory (M = {m_hi})\nit walks - steadily, straight")):
        a.set_facecolor("#0a1024")
        a.set_xticks([]); a.set_yticks([])
        a.set_title(title, fontsize=10.5, color="#dce8ff")
        for s in a.spines.values():
            s.set_color("#2a3a5f")
    ims, dots, trails = [], [], []
    for a, (Xg, Yg, ext) in zip(ax, grids):
        ims.append(a.imshow(np.zeros_like(Xg), extent=ext,
                            origin="lower", cmap=oil, vmin=-2.2, vmax=2.6))
        trails.append(a.plot([], [], color="#ffd9a0", lw=1.4, alpha=0.9)[0])
        dots.append(a.plot([], [], "o", color="white", ms=7)[0])
    fig.suptitle("Same bath, same nudge - the only difference is how long ripples last",
                 fontsize=12, color="#eaf2ff")
    fig.tight_layout(rect=(0, 0, 1, 0.93))

    def draw(n):
        for (Xg, Yg, _), im, dot, trail, traj, M in (
                (grids[0], ims[0], dots[0], trails[0], t_lo, m_lo),
                (grids[1], ims[1], dots[1], trails[1], t_hi, m_hi)):
            im.set_data(field(Xg, Yg, list(traj), M, n))
            trail.set_data(traj[:n, 0], traj[:n, 1])
            dot.set_data([traj[n, 0]], [traj[n, 1]])
        return ims + dots + trails

    anim = FuncAnimation(fig, draw, frames=frames, blit=True)
    out = ASSETS / "walker_memory.gif"
    anim.save(out, writer=PillowWriter(fps=14))
    draw(frames[-1])
    fig.savefig(HERE / "walker_preview.png", dpi=110, facecolor="#0a1024")
    print(f"wrote {out} and walker_preview.png")


def main():
    print(f"{'M':>5} {'tail speed':>12} {'+/-':>8} {'angle wander (rad)':>20}")
    results = {}
    for M in (2, 5, 10, 20, 40):
        traj = run(M)
        sp, sd = speed_tail(traj)
        results[M] = sp
        print(f"{M:>5} {sp:>12.4f} {sd:>8.4f} {straightness(traj):>20.3f}")

    if "sweep" not in sys.argv:
        render(m_lo=2, m_hi=40)


if __name__ == "__main__":
    main()
