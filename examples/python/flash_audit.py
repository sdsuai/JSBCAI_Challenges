"""
flash_audit.py — does your matrix animation flash at a rate that can trigger a
photosensitive seizure?

This is the one requirement in the challenge that is not about taste.

Roughly 1 in 4000 people has photosensitive epilepsy, and the trigger is
well characterised: large-area luminance flashing between about 3 Hz and
60 Hz, worst around 15-20 Hz. WCAG 2.3.1 states the general threshold as no
more than three flashes per second over any significant area. An LED matrix
is a small display, but it is also bright, high-contrast, and often mounted
where people cannot look away -- which is exactly the bad combination.

The rule for this challenge: NO FULL-FIELD FLASHING BETWEEN 3 Hz AND 60 Hz.
Pulse an alarm slowly (<= 2 Hz) or move something instead. A slow pulse also
reads as more serious, so this constraint costs you nothing and you should
not think of it as a tax.

How to use it -- record a trace, then audit it:

    # in your animation code
    m = TerminalMatrix(64, 32, luma_log="trace.csv")
    ...
    python flash_audit.py trace.csv

Method: the recorded mean panel luminance is a 1-D signal over time. A "flash"
is a swing between a relative light state and a relative dark state, which WCAG
defines as a change of at least 10% of max luminance where the darker state is
below 0.80. We count those transitions with hysteresis (so noise around the
threshold does not register as flashing) and report the rate.

This measures FULL-FIELD luminance, which is the right thing. A single blinking
pixel is not a seizure risk; the whole panel strobing is.
"""

import argparse
import csv
import sys

SAFE_MAX_HZ = 3.0        # WCAG general flash threshold
DANGER_LO, DANGER_HI = 3.0, 60.0


def load(path):
    ts, ls = [], []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            ts.append(float(row["t"]))
            ls.append(float(row["mean_luminance"]))
    if len(ts) < 4:
        raise SystemExit(f"{path}: need at least 4 samples, got {len(ts)}")
    return ts, ls


def count_flashes(ts, ls):
    """Count light->dark->light cycles using WCAG's own definition."""
    lmax = max(ls)
    if lmax <= 0:
        return 0, 0.0, []
    swing = 0.10 * lmax                    # >=10% of max luminance
    hi_th = lmax - swing * 0.5
    lo_th = lmax - swing * 1.5             # hysteresis band
    dark_limit = 0.80 * lmax               # darker state must be below this

    state = "hi" if ls[0] >= hi_th else "lo"
    transitions = []
    for t, v in zip(ts, ls):
        if state == "hi" and v <= lo_th and v <= dark_limit:
            state = "lo"
            transitions.append(t)
        elif state == "lo" and v >= hi_th:
            state = "hi"
            transitions.append(t)
    duration = ts[-1] - ts[0]
    flashes = len(transitions) / 2.0       # a flash is a full down-up cycle
    return flashes, (flashes / duration if duration > 0 else 0.0), transitions


def peak_rate(transitions, window=1.0):
    """Worst one-second window -- an average hides a short dangerous burst."""
    if len(transitions) < 2:
        return 0.0
    worst = 0.0
    for i, t0 in enumerate(transitions):
        n = sum(1 for t in transitions[i:] if t <= t0 + window)
        worst = max(worst, n / 2.0 / window)
    return worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trace", help="CSV from TerminalMatrix(luma_log=...)")
    ap.add_argument("--window", type=float, default=1.0)
    args = ap.parse_args()

    ts, ls = load(args.trace)
    flashes, rate, transitions = count_flashes(ts, ls)
    peak = peak_rate(transitions, args.window)
    dur = ts[-1] - ts[0]

    print(f"trace          {args.trace}")
    print(f"duration       {dur:.2f}s, {len(ts)} frames ({len(ts)/dur:.1f} fps)")
    print(f"luminance      min {min(ls):.4f}  max {max(ls):.4f}  mean {sum(ls)/len(ls):.4f}")
    print(f"full-field flashes  {flashes:.1f}")
    print(f"average rate   {rate:.2f} Hz")
    print(f"peak rate      {peak:.2f} Hz  (worst {args.window:.0f}s window)")
    print()

    if peak <= SAFE_MAX_HZ:
        print(f"PASS — peak {peak:.2f} Hz is at or below the {SAFE_MAX_HZ:.0f} Hz threshold.")
        sys.exit(0)
    if DANGER_LO < peak < DANGER_HI:
        print(f"FAIL — {peak:.2f} Hz is inside the {DANGER_LO:.0f}-{DANGER_HI:.0f} Hz "
              f"photosensitive band.")
        print("Fix it: slow the pulse to <= 2 Hz, shrink the flashing area, reduce the")
        print("luminance swing, or convey the state with motion or shape instead.")
    else:
        print(f"FAIL — peak {peak:.2f} Hz exceeds the {SAFE_MAX_HZ:.0f} Hz threshold.")
    sys.exit(1)


if __name__ == "__main__":
    main()
