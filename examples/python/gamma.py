"""
gamma.py — the difference between "the number you chose" and "the light you get".

This is the single most important 30 lines in the LED part of this challenge.

An LED panel is driven by PWM: duty cycle 50% means the LED is physically on
half the time, so it emits half the *photons*. Linear in light.

Your eye is not linear in light. Halving the photons does not look "half as
bright" — it looks roughly 73% as bright. Perception follows a power law with
an exponent near 1/2.2.

So there are two different 0-255 scales, and confusing them is the classic
LED-animation bug:

    PERCEPTUAL (sRGB)   what you pick in a color picker, what a monitor eats.
                        128 looks like "half brightness".

    LINEAR (duty)       what a HUB75 panel eats. 128 IS half the photons,
                        which LOOKS like ~73% brightness.

If you write a linear 0 -> 255 ramp straight to a panel, your "smooth fade"
rushes to bright in the first third and then barely changes. Everybody hits
this. The fix is to gamma-encode before handing bytes to the panel:

    duty = 255 * (srgb / 255) ** 2.2

`TerminalMatrix(panel="led")` in matrix_sim.py reproduces this faithfully, so
you can see the artifact and the fix on a laptop with no hardware.

Note: real sRGB is a piecewise curve with a small linear segment near black.
A pure power law is what actual LED libraries use and it is what we use here,
so `srgb_to_duty` and `duty_to_srgb` are exact inverses.
"""

GAMMA = 2.2


def srgb_to_duty(c: float, gamma: float = GAMMA) -> int:
    """Perceptual 0-255 -> linear PWM duty 0-255. Apply this before the panel."""
    c = 0.0 if c < 0 else (255.0 if c > 255 else float(c))
    return int(round(255.0 * (c / 255.0) ** gamma))


def duty_to_srgb(d: float, gamma: float = GAMMA) -> int:
    """Linear PWM duty 0-255 -> perceptual 0-255. The simulator uses this to
    show you what a real panel would actually look like."""
    d = 0.0 if d < 0 else (255.0 if d > 255 else float(d))
    return int(round(255.0 * (d / 255.0) ** (1.0 / gamma)))


def build_lut(gamma: float = GAMMA):
    """256-entry lookup table. Build it once at startup, index it per pixel.

    Doing `x ** 2.2` for 64*32*3 channels every frame is 6144 pow() calls per
    frame; a list index is free. Real panel drivers all ship a LUT.
    """
    return [srgb_to_duty(i, gamma) for i in range(256)]


def apply_lut(rgb, lut):
    """(r, g, b) perceptual -> (r, g, b) duty, through a prebuilt LUT."""
    r, g, b = rgb
    return (lut[int(r)], lut[int(g)], lut[int(b)])


def relative_luminance(rgb) -> float:
    """WCAG relative luminance, 0.0 (black) to 1.0 (white). Needs LINEAR light,
    which is why the sRGB values get decoded first. Used by contrast.py and by
    flash_audit.py."""
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


if __name__ == "__main__":
    print("srgb -> duty (what you must send a real panel)")
    print(f"{'srgb':>6} {'duty':>6}  {'bar (perceived)':<24}")
    for v in (0, 16, 32, 64, 96, 128, 160, 192, 224, 255):
        d = srgb_to_duty(v)
        bar = "#" * int(round(v / 255 * 24))
        print(f"{v:>6} {d:>6}  {bar:<24}")
    print()
    print("Read the middle row: to LOOK 50% bright, a panel needs only 21% duty.")
    print("Send it 50% duty instead and it looks ~73% bright — the fade is ruined.")
    print()
    print("Try:  python matrix_sim.py --demo gamma")
