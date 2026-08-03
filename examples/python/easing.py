"""
easing.py — motion that reads as intentional instead of mechanical.

Linear motion is the tell of an animation nobody designed. Physical objects
have mass: they take time to start and time to stop. An easing function is
just a remap of normalized time t in [0,1] to normalized progress in [0,1],
and swapping one in costs you nothing.

Which curve you choose IS a design decision, and we will ask you to defend it:

    ease_out_*    fast start, gentle stop.  Feels responsive. Use for things
                  that appear because the USER just acted — the system is
                  reacting to them, so it should look eager.

    ease_in_*     gentle start, fast end.   Feels like something leaving or
                  being pulled away. Rarely right on its own for UI.

    ease_in_out_* gentle both ends.         Feels calm and mechanical, in a
                  good way. Use for continuous/ambient motion — a sweep, a
                  patrol, a breathing idle state.

    ease_out_back overshoots, settles back. Playful. Reads as "arrived with
                  confidence". Wrong for anything reporting a fault.

    ease_out_elastic  wobbles to rest.      Attention-grabbing and slightly
                  silly. If your BATTERY CRITICAL indicator wobbles, you have
                  told the operator it is not serious.

Everything here is dependency-free and identical to easing.hpp on the C++
side, so a mixed-language submission still moves the same way.
"""

import math


# --- the curves -------------------------------------------------------------

def linear(t: float) -> float:
    return t


def ease_in_quad(t: float) -> float:
    return t * t


def ease_out_quad(t: float) -> float:
    return 1.0 - (1.0 - t) * (1.0 - t)


def ease_in_out_quad(t: float) -> float:
    return 2.0 * t * t if t < 0.5 else 1.0 - ((-2.0 * t + 2.0) ** 2) / 2.0


def ease_in_cubic(t: float) -> float:
    return t * t * t


def ease_out_cubic(t: float) -> float:
    return 1.0 - (1.0 - t) ** 3


def ease_in_out_cubic(t: float) -> float:
    return 4.0 * t * t * t if t < 0.5 else 1.0 - ((-2.0 * t + 2.0) ** 3) / 2.0


def smoothstep(t: float) -> float:
    """The classic. Cheap, no overshoot, C1-continuous. When in doubt, this."""
    return t * t * (3.0 - 2.0 * t)


def ease_out_back(t: float) -> float:
    c1, c3 = 1.70158, 2.70158
    return 1.0 + c3 * (t - 1.0) ** 3 + c1 * (t - 1.0) ** 2


def ease_out_elastic(t: float) -> float:
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    c4 = (2.0 * math.pi) / 3.0
    return 2.0 ** (-10.0 * t) * math.sin((t * 10.0 - 0.75) * c4) + 1.0


def ease_out_bounce(t: float) -> float:
    n1, d1 = 7.5625, 2.75
    if t < 1.0 / d1:
        return n1 * t * t
    if t < 2.0 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375


EASINGS = {
    "linear": linear,
    "ease_in_quad": ease_in_quad,
    "ease_out_quad": ease_out_quad,
    "ease_in_out_quad": ease_in_out_quad,
    "ease_in_cubic": ease_in_cubic,
    "ease_out_cubic": ease_out_cubic,
    "ease_in_out_cubic": ease_in_out_cubic,
    "smoothstep": smoothstep,
    "ease_out_back": ease_out_back,
    "ease_out_elastic": ease_out_elastic,
    "ease_out_bounce": ease_out_bounce,
}


# --- helpers ----------------------------------------------------------------

def clamp01(t: float) -> float:
    return 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_rgb(c0, c1, t: float):
    """Interpolate two colors. NOTE: this blends in whatever space you hand it.
    Blending two saturated hues in sRGB drags the midpoint toward grey/mud.
    If your fault->nominal color transition looks dirty in the middle, that is
    why, and fixing it is worth extra credit."""
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c0, c1))


class Tween:
    """A single animated value driven by DELTA TIME, not by frame count.

    The bug this exists to prevent: `for i in range(60): draw(i/60); sleep(1/60)`
    runs at a different speed on a fast laptop than a slow one, and stutters
    the moment anything else blocks. Animate against a clock, always.

        fade = Tween(0.0, 1.0, duration=0.4, fn=easing.ease_out_cubic)
        while running:
            dt = now - last                # seconds, measured
            v = fade.update(dt)            # advance by real elapsed time
    """

    def __init__(self, start=0.0, end=1.0, duration=1.0, fn=smoothstep, loop=False):
        self.start, self.end = start, end
        self.duration = max(1e-9, float(duration))
        self.fn, self.loop = fn, loop
        self.elapsed = 0.0

    def update(self, dt: float) -> float:
        self.elapsed += dt
        if self.elapsed >= self.duration:
            if self.loop:
                self.elapsed %= self.duration
            else:
                self.elapsed = self.duration
        return self.value()

    def value(self) -> float:
        t = min(1.0, max(0.0, self.elapsed / self.duration))
        return lerp(self.start, self.end, self.fn(t))

    @property
    def done(self) -> bool:
        return (not self.loop) and self.elapsed >= self.duration

    def reset(self):
        self.elapsed = 0.0


def ping_pong(t: float) -> float:
    """Map a looping 0..1 onto 0..1..0 — for breathing/pulsing, so the loop
    does not snap back to the start."""
    return 1.0 - abs(2.0 * t - 1.0)


if __name__ == "__main__":
    print("Same 1.0s move, different curves. Read down each column.\n")
    names = ["linear", "ease_out_cubic", "ease_in_out_cubic", "ease_out_back"]
    print(f"{'t':>5} " + " ".join(f"{n:<22}" for n in names))
    for i in range(21):
        t = i / 20
        row = f"{t:>5.2f} "
        for n in names:
            v = EASINGS[n](t)
            pos = int(round(max(0.0, min(1.0, v)) * 20))
            row += ("." * pos + "O" + "." * (20 - pos))[:21].ljust(22) + " "
        print(row)
    print("\nNote how ease_out_back leaves the track and comes back — that is the")
    print("overshoot. Charming on a success state, alarming on an alarm.")
