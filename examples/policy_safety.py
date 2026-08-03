"""
policy_safety.py — stopping a working policy from being a dangerous one.

Supports D3. Standard library only.

    python examples/policy_safety.py

A policy that reads the current detection and returns an action is correct on
clean data and unsafe on real data. Perception is noisy, intermittent, and
sometimes confidently wrong, and the policy is the last thing standing between
a bad detection and a moving robot.

Four mechanisms, all small, all required by D3:

  1. DEADBAND / HYSTERESIS
     A person standing exactly on your turn threshold makes a naive policy emit
     TURN_LEFT, ALIGNED, TURN_LEFT, ALIGNED at 30 Hz. On a real robot that is a
     motor buzzing itself to death. Use two thresholds instead of one: a wide
     one to START turning and a narrow one to STOP. Once you commit, you stay
     committed until clearly done.

  2. STALENESS WATCHDOG
     If the object has not been seen for a while, the policy must fall back to
     a safe action, NOT keep steering toward the last known position. It has to
     be measured in SECONDS, not frames: your frame rate varies (see D1/D2), so
     "10 frames" is 300 ms on a good run and 3 s on a bad one. Time is the
     thing that matters to the world; frame count is an implementation detail.

  3. MINIMUM DWELL TIME
     Even with a deadband, an action that can change every frame produces
     commands no actuator can follow. Hold each action for a minimum time
     before allowing another change.

  4. TRACK LOCK
     YOLO track IDs are not stable. When the ID you were following disappears
     and a new one appears, a naive policy silently starts following a
     different person. Lock onto an ID, notice when it goes, and treat the
     replacement as unconfirmed until it has been stable for a moment.

None of this makes the policy smarter. All of it stops it doing something
stupid quickly and confidently — which is the actual failure mode of robots.
"""

import argparse
import math
import random


class Deadband:
    """Two thresholds instead of one. `enter` to commit, `exit` to release."""

    def __init__(self, enter, exit_):
        assert enter > exit_, "enter threshold must be wider than exit"
        self.enter, self.exit = enter, exit_
        self.engaged = False

    def update(self, value):
        """value: signed error. Returns True while the band is engaged."""
        if self.engaged:
            if abs(value) < self.exit:
                self.engaged = False
        else:
            if abs(value) > self.enter:
                self.engaged = True
        return self.engaged


class StalenessWatchdog:
    """Time-based, deliberately. See note 2 above."""

    def __init__(self, timeout_s=0.5):
        self.timeout_s = timeout_s
        self._last_seen = None

    def saw_it(self, t):
        self._last_seen = t

    def age(self, t):
        return math.inf if self._last_seen is None else t - self._last_seen

    def is_stale(self, t):
        return self.age(t) > self.timeout_s


class ActionHold:
    """Refuses to change action more often than `min_dwell_s`."""

    def __init__(self, min_dwell_s=0.2, initial="STOP"):
        self.min_dwell_s = min_dwell_s
        self.action = initial
        self._since = -math.inf
        self.suppressed = 0

    def propose(self, action, t, force=False):
        """`force=True` bypasses the hold — use it for safety actions, which
        must never be delayed by a comfort mechanism."""
        if action == self.action:
            return self.action
        if force or (t - self._since) >= self.min_dwell_s:
            self.action = action
            self._since = t
        else:
            self.suppressed += 1
        return self.action


class TrackLock:
    """Follow one track ID; require a new one to be stable before adopting it."""

    def __init__(self, confirm_s=0.3):
        self.confirm_s = confirm_s
        self.locked_id = None
        self.switches = 0
        self._candidate = None
        self._candidate_since = None

    def update(self, visible_ids, t):
        """Returns the id to follow, or None if nothing is confirmed yet."""
        if self.locked_id in visible_ids:
            self._candidate = None
            return self.locked_id

        # our target is gone; pick the lowest visible id as a candidate
        if not visible_ids:
            self._candidate = None
            return None
        best = min(visible_ids)
        if best != self._candidate:
            self._candidate, self._candidate_since = best, t
            return None
        if t - self._candidate_since >= self.confirm_s:
            if self.locked_id is not None:
                self.switches += 1
            self.locked_id = best
            self._candidate = None
            return self.locked_id
        return None


# --------------------------------------------------------------------------
# Demo: the same scene, through a naive policy and a guarded one.
# --------------------------------------------------------------------------

def naive_policy(det, width):
    if det is None:
        return "TURN_LEFT"          # keeps steering on nothing. Very common.
    cx = det["cx"]
    off = cx - width / 2
    if abs(off) > 0.10 * width:
        return "TURN_LEFT" if off < 0 else "TURN_RIGHT"
    return "ALIGNED"


class GuardedPolicy:
    def __init__(self, width, fps):
        self.width = width
        self.band = Deadband(enter=0.12 * width, exit_=0.05 * width)
        self.dog = StalenessWatchdog(timeout_s=0.5)
        self.hold = ActionHold(min_dwell_s=0.20)
        self.lock = TrackLock(confirm_s=0.3)

    def step(self, det, t):
        ids = [det["id"]] if det else []
        follow = self.lock.update(ids, t)

        if det and follow == det["id"]:
            self.dog.saw_it(t)

        if self.dog.is_stale(t):
            # Safety action, forced past the dwell hold.
            return self.hold.propose("STOP_SEARCH", t, force=True)

        if det is None or follow is None:
            return self.hold.action          # coast on the last good action

        off = det["cx"] - self.width / 2
        if self.band.update(off):
            action = "TURN_LEFT" if off < 0 else "TURN_RIGHT"
        else:
            action = "ALIGNED"
        return self.hold.propose(action, t)


def synth_scene(n, fps, seed):
    """A person hovering right on the turn threshold, with a dropout.

    Both things happen constantly in real footage: jitter around a decision
    boundary, and the detector losing the object for a moment.
    """
    rng = random.Random(seed)
    W = 640
    for i in range(n):
        t = i / fps
        # sits near the +10% boundary, with detector jitter
        base = W / 2 + 0.105 * W
        cx = base + rng.gauss(0, 0.02 * W)
        # detector loses them for 1.2 s in the middle
        if 3.0 <= t < 4.2:
            yield t, None, W
        else:
            yield t, {"id": 1 if t < 5.0 else 2, "cx": cx}, W


def transitions(actions):
    return sum(1 for a, b in zip(actions, actions[1:]) if a != b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--seconds", type=float, default=7.0)
    ap.add_argument("--seed", type=int, default=3)
    args = ap.parse_args()

    n = int(args.fps * args.seconds)
    scene = list(synth_scene(n, args.fps, args.seed))

    naive = [naive_policy(d, w) for _, d, w in scene]

    guard = GuardedPolicy(640, args.fps)
    guarded = [guard.step(d, t) for t, d, _ in scene]

    blind = [(t, a) for (t, d, _), a in zip(scene, naive) if d is None]
    blind_g = [(t, a) for (t, d, _), a in zip(scene, guarded) if d is None]

    print(f"scene: {n} frames @ {args.fps:.0f} FPS, person on the turn threshold,")
    print("       detector drops out from t=3.0s to t=4.2s, track ID changes at t=5.0s\n")

    print(f"{'':<22}{'naive':>10}{'guarded':>10}")
    print("-" * 42)
    print(f"{'action changes':<22}{transitions(naive):>10}{transitions(guarded):>10}")
    print(f"{'changes per second':<22}{transitions(naive)/args.seconds:>10.1f}"
          f"{transitions(guarded)/args.seconds:>10.1f}")
    steer_blind = sum(1 for _, a in blind if a.startswith("TURN"))
    steer_blind_g = sum(1 for _, a in blind_g if a.startswith("TURN"))
    print(f"{'frames steering blind':<22}{steer_blind:>10}{steer_blind_g:>10}")
    print(f"{'suppressed by dwell':<22}{'-':>10}{guard.hold.suppressed:>10}")
    # The naive policy also changed identity at t=5.0 -- it just never noticed.
    # The guarded one required the new id to be stable before adopting it, so
    # the switch is a logged event rather than a silent substitution.
    print(f"{'ID switch':<22}{'silent':>10}{'confirmed':>10}")

    print("\nDuring the dropout the naive policy kept turning toward a person who")
    print("was no longer detected. The guarded one went to STOP_SEARCH and stayed")
    print("there until perception came back.\n")
    print("Sample around the dropout (t=2.9 - 4.4s):")
    print(f"  {'t':>6}  {'det':<5}{'naive':<12}{'guarded':<12}")
    for (t, d, _), a, b in zip(scene, naive, guarded):
        if 2.9 <= t <= 4.4 and abs((t * args.fps) % 6) < 1e-6:
            print(f"  {t:>6.2f}  {'yes' if d else 'NO':<5}{a:<12}{b:<12}")


if __name__ == "__main__":
    main()
