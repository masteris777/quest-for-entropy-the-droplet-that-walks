# Quest for Entropy #6 — The Droplet That Walks

Companion code for the article *The Droplet That Walks*.

The article reads the walking-droplet experiments (Couder, Fort, Bush and colleagues) and
sits them down for a quantum exam; the laboratory results it grades live in the published
papers cited in the article. The one runnable thing the article shows is a toy of the
walker's mechanism, and this repo is that toy.

`walker_toy.py` implements the standard path-memory picture in its simplest discrete form:
each bounce stamps a circular ripple, ripples fade at the memory rate, the droplet is
kicked by the summed slope, with drag. One knob — the memory M, how many bounces a ripple
survives — separates two behaviours: below a threshold the droplet bounces in place
forever; above it, the droplet starts walking by itself, steadily and dead straight.

## Run it

```
pip install -r requirements.txt
python run_all.py
```

About a minute. It re-runs the memory sweep and checks the numbers the article quotes,
then exits non-zero if anything drifted. To regenerate the article's gif as well
(a few minutes):

```
python walker_toy.py
```

## What is in here

| file | what it is |
|---|---|
| `walker_toy.py` | the path-memory model: sweep + the two-panel gif |
| `run_all.py` | reproduction check of the published sweep numbers |
| `expected_output/` | the gif's final frame as published |
| `article.md`, `assets/` | the article as published, with its figures |

## Honest notes about the toy

**Every parameter is made up.** The kick strength, the drag, the noise and the memory
values were chosen so the mechanism shows itself clearly. The toy demonstrates that the
walk exists and that memory is the knob — nothing in it is calibrated to a laboratory
number, and none of its outputs can be compared to one.

**The run is deterministic.** The tiny starting nudge comes from a seeded generator, so
the sweep reproduces to the printed digits on the same library versions, and to the stated
tolerance across versions.

**What the toy does not contain:** walls, a second droplet, or any tuning toward the
experiments the article grades. It is the mechanism of steps 1-4 of the article's
five-step loop, and step 5 (the corral) is deliberately not simulated here.

## Licence

Code MIT. Article text CC BY 4.0.
