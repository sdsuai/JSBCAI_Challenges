"""
latency_probe.py — where does the time actually go, and how bad is the tail?

Supports D1. Standard library only, so you can run and understand it before
YOLO is anywhere near your machine.

    python examples/latency_probe.py          # self-demo with synthetic stages

WHY PERCENTILES AND NOT AVERAGES
--------------------------------
"My tracker runs at 30 FPS" is an average, and averages hide exactly the thing
a robot cares about. If 99 frames take 20 ms and one takes 900 ms, the mean is
a healthy 29 ms and the robot still drove blind for almost a second.

The number that matters is the TAIL: p95, p99, and the single worst frame. A
control loop is only as good as its worst-case delay, because that is when it
was still steering on stale information.

THE NUMBER THAT REALLY MATTERS
------------------------------
Not how long inference takes — **how old the data was when the policy acted on
it.** That is the sum of every stage, plus any time the frame sat in a queue:

    capture ──▶ decode ──▶ inference ──▶ track ──▶ relations ──▶ policy ──▶ action
    │                                                                        │
    └──────────────────── this whole span is the age ───────────────────────┘

At 0.5 m/s, 300 ms of age means the robot commits to a turn based on where the
person was 15 cm ago. Whether that matters is a design decision — but you
cannot make it if you never measured the number.

USAGE IN YOUR PIPELINE
----------------------
    probe = LatencyProbe()

    for frame_idx, frame in enumerate(source):
        probe.begin_frame()
        with probe.stage("decode"):     img = decode(frame)
        with probe.stage("inference"):  result = model(img)
        with probe.stage("track"):      tracks = update_tracks(result)
        with probe.stage("policy"):     action = robot_policy(tracks, W, H)
        probe.end_frame()

    probe.report()
    probe.to_csv("latency.csv")
"""

import argparse
import csv
import random
import statistics
import time
from contextlib import contextmanager


def percentile(values, pct):
    """Nearest-rank percentile. No numpy needed, and it is exact for the
    "which observed sample is the p99" question, which is what you want when
    reporting a worst case rather than smoothing one."""
    if not values:
        return 0.0
    s = sorted(values)
    k = max(0, min(len(s) - 1, int(round((pct / 100.0) * len(s) + 0.5)) - 1))
    return s[k]


class LatencyProbe:
    def __init__(self):
        self.stages = {}        # name -> [durations in ms]
        self.frames = []        # end-to-end ms per frame
        self._order = []        # stage names, first-seen order
        self._t_frame = None
        self._rows = []

    def begin_frame(self):
        self._t_frame = time.perf_counter()
        self._current = {}

    @contextmanager
    def stage(self, name):
        if name not in self.stages:
            self.stages[name] = []
            self._order.append(name)
        t0 = time.perf_counter()
        try:
            yield
        finally:
            dt = (time.perf_counter() - t0) * 1000.0
            self.stages[name].append(dt)
            self._current[name] = dt

    def end_frame(self, extra_age_ms=0.0):
        """extra_age_ms: time the frame spent waiting BEFORE you picked it up —
        queue delay. If you are not measuring that, your end-to-end number is
        optimistic. See D2."""
        total = (time.perf_counter() - self._t_frame) * 1000.0 + extra_age_ms
        self.frames.append(total)
        row = dict(self._current)
        row["queue_wait"] = extra_age_ms
        row["end_to_end"] = total
        self._rows.append(row)

    # -- output -----------------------------------------------------------

    def report(self):
        print()
        print(f"{'stage':<14}{'n':>6}{'mean':>9}{'p50':>9}{'p95':>9}{'p99':>9}{'max':>9}")
        print("-" * 65)
        for name in self._order:
            v = self.stages[name]
            print(f"{name:<14}{len(v):>6}{statistics.fmean(v):>9.1f}"
                  f"{percentile(v,50):>9.1f}{percentile(v,95):>9.1f}"
                  f"{percentile(v,99):>9.1f}{max(v):>9.1f}")
        if self.frames:
            v = self.frames
            print("-" * 65)
            print(f"{'END-TO-END':<14}{len(v):>6}{statistics.fmean(v):>9.1f}"
                  f"{percentile(v,50):>9.1f}{percentile(v,95):>9.1f}"
                  f"{percentile(v,99):>9.1f}{max(v):>9.1f}")
            print()
            print(f"  effective FPS (from p50): {1000.0/max(1e-9,percentile(v,50)):.1f}")
            print(f"  worst single frame      : {max(v):.1f} ms")
            print(f"  p99 / p50 ratio         : {percentile(v,99)/max(1e-9,percentile(v,50)):.1f}x")
            print()
            print("  The last line is the one to explain in your write-up. A ratio near")
            print("  1 means a predictable loop. A large ratio means the robot")
            print("  occasionally acts on much older data than the average suggests.")
        print()

    def to_csv(self, path):
        if not self._rows:
            return
        cols = self._order + ["queue_wait", "end_to_end"]
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in self._rows:
                w.writerow({c: round(r.get(c, 0.0), 3) for c in cols})
        print(f"wrote {path} ({len(self._rows)} frames)")


# --------------------------------------------------------------------------

def _demo(n_frames, seed):
    """Synthetic stand-in for a real pipeline. `inference` occasionally spikes,
    the way a real one does when the GPU is busy or a frame is complex — which
    is precisely the behaviour an average would hide from you."""
    rng = random.Random(seed)
    probe = LatencyProbe()

    def burn(ms):
        end = time.perf_counter() + ms / 1000.0
        while time.perf_counter() < end:
            pass

    for i in range(n_frames):
        probe.begin_frame()
        with probe.stage("decode"):
            burn(rng.uniform(1.0, 2.0))
        with probe.stage("inference"):
            # 1 frame in 25 takes ~8x as long. Mean barely moves; p99 explodes.
            burn(rng.uniform(9.0, 12.0) if rng.random() > 0.04 else rng.uniform(70.0, 90.0))
        with probe.stage("track"):
            burn(rng.uniform(0.3, 0.8))
        with probe.stage("policy"):
            burn(rng.uniform(0.05, 0.2))
        probe.end_frame()

    probe.report()
    return probe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--csv", default="")
    args = ap.parse_args()
    print("Synthetic pipeline: inference spikes on ~4% of frames.")
    print("Watch what that does to p99 while the mean stays respectable.")
    probe = _demo(args.frames, args.seed)
    if args.csv:
        probe.to_csv(args.csv)


if __name__ == "__main__":
    main()
