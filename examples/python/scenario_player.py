"""
scenario_player.py — replays scenario/scenario.jsonl against a wall clock.

All three of your surfaces read the same timeline through something like this,
which is what makes them comparable to each other and to every other
candidate's submission.

The player is PULL-BASED on purpose. It does not own a loop, it does not call
you back, it does not sleep. Your render loop stays in charge and asks "what is
true now?" once per frame:

    player = ScenarioPlayer("scenario/scenario.jsonl", speed=1.0)
    last = time.monotonic()
    while player.running:
        now = time.monotonic(); dt = now - last; last = now
        tick = player.poll()              # latest state at the current time
        for note in player.drain_notes(): # discrete events since last poll
            log.append(note)
        render(tick, dt)

Why this shape matters for grading: it forces you to separate
    STATE  (what is true now — drives the layout)  from
    EVENTS (what just happened — drives the log and the animations).
A design that conflates them either loses transient faults or animates things
that did not change. The 3.5-second comms dropout at t=26 is the test case.

CLI:
    python scenario_player.py --list           # every event, with timings
    python scenario_player.py --speed 4        # watch it replay as text
    python scenario_player.py --at 58          # what is true at t=58?
"""

import argparse
import json
import time


class Tick(dict):
    """A single 5 Hz sample. Plain dict, plus attribute access for readability."""

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)

    # -- Convenience only. NOTE: we deliberately do NOT hand you an "alarm"
    # -- field or a severity ranking. Deciding what counts as an alarm, how to
    # -- rank two simultaneous ones, and what the operator sees first IS the
    # -- design work being assessed. These are just the raw predicates.

    @property
    def sensors_down(self):
        return [n for n in ("lidar", "imu", "comms") if self[n] == "down"]

    @property
    def sensors_degraded(self):
        return [n for n in ("lidar", "imu", "comms") if self[n] == "degraded"]

    @property
    def moving(self):
        return self["speed"] > 0.01


class ScenarioPlayer:
    def __init__(self, path, speed=1.0, loop=False, start=0.0):
        with open(path, "r") as f:
            self.ticks = [Tick(json.loads(line)) for line in f if line.strip()]
        if not self.ticks:
            raise ValueError(f"{path} is empty")
        self.speed = speed
        self.loop = loop
        self.duration = self.ticks[-1]["t"]
        self._start_offset = start
        self._t0 = time.monotonic()
        self._idx = 0
        self._pending_notes = []
        self._finished = False

    # -- clock -------------------------------------------------------------

    @property
    def scenario_time(self):
        el = (time.monotonic() - self._t0) * self.speed + self._start_offset
        if self.loop and self.duration > 0:
            el %= self.duration
        return el

    @property
    def running(self):
        return not self._finished

    def restart(self):
        self._t0 = time.monotonic()
        self._idx = 0
        self._pending_notes.clear()
        self._finished = False

    # -- data --------------------------------------------------------------

    def poll(self):
        """Latest tick at or before the current scenario time.

        Advances through every intervening tick so no note is skipped, even if
        your frame rate is lower than the 5 Hz data rate — or if you stalled.
        """
        now = self.scenario_time
        if self.loop and self._idx > 0 and self.ticks[self._idx]["t"] > now:
            self._idx = 0  # wrapped
        while self._idx + 1 < len(self.ticks) and self.ticks[self._idx + 1]["t"] <= now:
            self._idx += 1
            note = self.ticks[self._idx]["note"]
            if note:
                self._pending_notes.append((self.ticks[self._idx]["t"], note))
        if not self.loop and now >= self.duration:
            self._finished = True
        return self.ticks[self._idx]

    def drain_notes(self):
        """Discrete events since the previous call. Returns [(t, text), ...]
        and empties the queue — call it exactly once per frame."""
        out, self._pending_notes = self._pending_notes, []
        return out

    def at(self, t):
        """State at an arbitrary scenario time. Handy for unit tests and for
        screenshotting a specific moment for your DESIGN.md."""
        lo, hi = 0, len(self.ticks) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.ticks[mid]["t"] <= t:
                lo = mid
            else:
                hi = mid - 1
        return self.ticks[lo]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="../../scenario/scenario.jsonl")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--list", action="store_true", help="print every event and exit")
    ap.add_argument("--at", type=float, help="print state at time T and exit")
    args = ap.parse_args()

    p = ScenarioPlayer(args.file, speed=args.speed, loop=args.loop)

    if args.list:
        print(f"{len(p.ticks)} ticks, {p.duration:.1f}s\n")
        print(f"{'t':>7}  {'state':<9} {'batt':>6}  {'lidar':<9}{'imu':<7}{'comms':<7} event")
        for tk in p.ticks:
            if tk["note"]:
                print(f"{tk['t']:>7.1f}  {tk['state']:<9} {tk['battery_pct']:>5.1f}%  "
                      f"{tk['lidar']:<9}{tk['imu']:<7}{tk['comms']:<7} {tk['note']}")
        return

    if args.at is not None:
        print(json.dumps(p.at(args.at), indent=2))
        return

    print(f"replaying {args.file} at {args.speed}x — Ctrl+C to stop\n")
    try:
        while p.running:
            tk = p.poll()
            for t, note in p.drain_notes():
                print(f"  [{t:>6.1f}] * {note}")
            print(f"\r  t={tk['t']:>6.1f}  {tk['state']:<9} batt={tk['battery_pct']:>5.1f}%  "
                  f"pos=({tk['x']:>6.2f},{tk['y']:>6.2f})  spd={tk['speed']:.2f}  "
                  f"lidar={tk['lidar']:<9} comms={tk['comms']:<6} estop={tk['estop']}",
                  end="", flush=True)
            time.sleep(1 / 30)
    except KeyboardInterrupt:
        pass
    print("\ndone.")


if __name__ == "__main__":
    main()
