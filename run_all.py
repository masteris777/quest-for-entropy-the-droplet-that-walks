"""Reproduce every number the article quotes, from scratch.

    python run_all.py

Runs the memory sweep of the walker toy (about a minute) and checks the numbers the
article states against the fresh run. Exits non-zero if anything drifted.

Needs numpy and scipy. Regenerating the gif additionally needs matplotlib and pillow:

    python walker_toy.py
"""
import sys

from walker_toy import run, speed_tail, straightness

# the published numbers: tail speed per memory value, from the article's sweep
EXPECTED = {2: 0.0000, 5: 0.0610, 10: 0.0698, 20: 0.0729, 40: 0.0742}

fails = []
print("running the memory sweep ...\n")
speeds = {}
for M, want in EXPECTED.items():
    traj = run(M)
    sp, sd = speed_tail(traj)
    speeds[M] = sp
    ok = abs(sp - want) <= 0.002
    print(f"  {'PASS' if ok else 'FAIL'}  M={M}: tail speed {sp:.4f} "
          f"(published {want:.4f}), steady to +/-{sd:.4f}")
    if not ok:
        fails.append(f"speed at M={M}")
    if sp > 0.01:
        wander = straightness(traj)
        ok = wander < 0.01
        print(f"  {'PASS' if ok else 'FAIL'}       walks straight "
              f"(direction wander {wander:.4f} rad)")
        if not ok:
            fails.append(f"straightness at M={M}")

print("\nthe two claims the article rests on:\n")

ok = speeds[2] < 1e-4
print(f"  {'PASS' if ok else 'FAIL'}  short memory sits still (M=2 speed {speeds[2]:.4f})")
if not ok:
    fails.append("short memory sits")

ok = speeds[5] > 0.05 and all(speeds[m] > 0.05 for m in (10, 20, 40))
print(f"  {'PASS' if ok else 'FAIL'}  the walk is a threshold, not a fade-in "
      f"(M=2 sits; M=5 already walks at {speeds[5]:.4f})")
if not ok:
    fails.append("walking threshold")

print("\n" + "-" * 62)
if fails:
    print(f"{len(fails)} CHECK(S) FAILED: {', '.join(fails)}")
    sys.exit(1)
print("all checks reproduced")
