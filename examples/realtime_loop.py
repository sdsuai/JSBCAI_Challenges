"""
realtime_loop.py — why a robot must DROP frames, not queue them.

Supports D2. Standard library only. Run it before you touch your own pipeline:

    python examples/realtime_loop.py

THE SITUATION
-------------
Your camera produces frames at a fixed rate. Your pipeline consumes them more
slowly — YOLO does not care that the camera is at 30 FPS. Something has to give,
and you only get two choices:

    QUEUE EVERYTHING    Nothing is lost. The backlog grows forever, and every
                        frame you process is older than the last. After a
                        minute the robot is reacting to a minute ago.

    DROP THE OLDEST     You process fewer frames. Every frame you DO process is
                        the newest one available, so the age stays bounded no
                        matter how long you run.

For a recording pipeline, queueing is right — you want every frame.
For a robot, dropping is right, and it is not a compromise: **a stale frame has
negative value.** Acting on where the person was four seconds ago is worse than
not acting, because you will confidently steer into the past.

YOU HAVE SEEN THIS BUG BEFORE
-----------------------------
This is C2's memory leak one layer up. There, an unbounded list between a fast
producer and a slow consumer ate RAM. Here, an unbounded queue between a fast
producer and a slow consumer eats TIME. Same shape, different resource:

    unbounded buffer + producer faster than consumer = something grows forever

The general rule is that every queue between a producer and a consumer you do
not control needs a bound AND a documented policy for what happens when it is
full. "It will never fill up" is not a policy.

IN YOUR OWN PIPELINE
--------------------
With OpenCV, `cap.read()` pulls from a driver-side buffer that queues for you,
so a slow loop silently accumulates lag. The fix is the same idea as below: a
reader thread that keeps only the latest frame.

    latest = LatestFrame()                       # capacity of exactly one
    threading.Thread(target=reader, args=(cap, latest), daemon=True).start()
    while running:
        frame, captured_at = latest.get()        # always the newest
        age_ms = (time.perf_counter() - captured_at) * 1000
"""

import argparse
import queue
import threading
import time


class LatestFrame:
    """A one-slot mailbox. Writing replaces whatever was there.

    This is the whole idea: capacity one, newest wins, no backlog possible.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._item = None
        self._event = threading.Event()
        self.dropped = 0

    def put(self, item):
        with self._lock:
            if self._item is not None:
                self.dropped += 1      # we are overwriting an unread frame
            self._item = item
            self._event.set()

    def get(self, timeout=None):
        if not self._event.wait(timeout):
            return None
        with self._lock:
            item, self._item = self._item, None
            self._event.clear()
            return item


def run(mode, fps, work_ms, seconds):
    """Produce at `fps`, consume taking `work_ms` each, for `seconds`."""
    stop = threading.Event()
    ages = []
    processed = 0

    if mode == "queue":
        q = queue.Queue()                       # UNBOUNDED — the bug
    else:
        q = LatestFrame()                       # bounded at 1 — the fix

    def producer():
        period = 1.0 / fps
        idx = 0
        nxt = time.perf_counter()
        while not stop.is_set():
            now = time.perf_counter()
            if now >= nxt:
                q.put((idx, now))
                idx += 1
                nxt += period
            else:
                time.sleep(min(0.002, nxt - now))

    t = threading.Thread(target=producer, daemon=True)
    t.start()

    t_end = time.perf_counter() + seconds
    samples = []
    while time.perf_counter() < t_end:
        item = q.get(timeout=0.5) if mode != "queue" else _q_get(q, 0.5)
        if item is None:
            continue
        idx, captured = item
        age_ms = (time.perf_counter() - captured) * 1000.0
        ages.append(age_ms)
        processed += 1
        samples.append((time.perf_counter(), age_ms))
        # simulate inference
        end = time.perf_counter() + work_ms / 1000.0
        while time.perf_counter() < end:
            pass

    stop.set()
    t.join(timeout=1.0)
    dropped = q.dropped if mode != "queue" else 0
    backlog = q.qsize() if mode == "queue" else 0
    return ages, processed, dropped, backlog, samples


def _q_get(q, timeout):
    try:
        return q.get(timeout=timeout)
    except queue.Empty:
        return None


def summarize(label, ages, processed, dropped, backlog, seconds):
    if not ages:
        print(f"{label}: no frames processed")
        return
    first = ages[: max(1, len(ages) // 10)]
    last = ages[-max(1, len(ages) // 10):]
    print(f"\n{label}")
    print(f"  frames processed        {processed}  ({processed/seconds:.1f}/s)")
    print(f"  frames dropped          {dropped}")
    print(f"  backlog still queued    {backlog}")
    print(f"  age of data, first 10%  {sum(first)/len(first):8.1f} ms")
    print(f"  age of data, last 10%   {sum(last)/len(last):8.1f} ms")
    print(f"  worst age               {max(ages):8.1f} ms")
    growth = (sum(last)/len(last)) - (sum(first)/len(first))
    verdict = "GROWING WITHOUT BOUND" if growth > 100 else "stable"
    print(f"  drift over the run      {growth:+8.1f} ms   <-- {verdict}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=float, default=30.0, help="camera rate")
    ap.add_argument("--work-ms", type=float, default=60.0,
                    help="per-frame inference cost (make it slower than 1/fps)")
    ap.add_argument("--seconds", type=float, default=6.0)
    args = ap.parse_args()

    period_ms = 1000.0 / args.fps
    print(f"camera: {args.fps:.0f} FPS (a frame every {period_ms:.1f} ms)")
    print(f"pipeline: {args.work_ms:.0f} ms per frame "
          f"-> {args.work_ms/period_ms:.1f}x slower than real time")
    print(f"running each mode for {args.seconds:.0f}s")

    a = run("queue", args.fps, args.work_ms, args.seconds)
    summarize("UNBOUNDED QUEUE  (process every frame, fall behind forever)", *a[:4], args.seconds)

    b = run("latest", args.fps, args.work_ms, args.seconds)
    summarize("DROP-OLDEST      (capacity 1, always the newest frame)", *b[:4], args.seconds)

    print("""
Read the 'drift over the run' lines together.

The unbounded queue processed every single frame and its data got steadily
older the whole time — run it for an hour and the robot is an hour behind.
Nothing errors. Nothing warns you. Throughput looks fine.

Drop-oldest threw frames away and the age never moved. Fewer frames, all of
them current.

Now plot both for your own pipeline (D2) and put the two curves on one axis.
""")


if __name__ == "__main__":
    main()
