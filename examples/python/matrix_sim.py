"""
matrix_sim.py — a 64x32 RGB LED matrix, simulated in your terminal.

You are not assumed to own an LED panel. This renders one using Unicode
half-block characters: the glyph U+2580 "UPPER HALF BLOCK" paints its
foreground color on the top half of the cell and its background color on the
bottom half. So ONE terminal character = TWO vertically stacked pixels, and a
64x32 matrix fits in 64 columns x 16 rows — comfortably inside a default
terminal, with no windowing library, no pygame, no SDL, nothing to install.

    +----------------+
    |  fg color      |  <- pixel (x, y)      one cell, character U+2580
    |  bg color      |  <- pixel (x, y+1)
    +----------------+

WHAT MATTERS FOR THE ASSIGNMENT
-------------------------------
`Matrix` is an abstract driver interface — set_pixel / fill / show / close.
`TerminalMatrix` is one backend. A real HUB75 panel would be another backend
behind the same four methods, and your animation code must not care which one
it is holding. Write to the interface, not to this file.

    panel="srgb"  (default) The buffer holds perceptual sRGB values and is
                  displayed as-is. This is "what a monitor does". Good for
                  developing your composition and layout.

    panel="led"   The buffer is interpreted as LINEAR PWM DUTY, exactly like a
                  real HUB75 panel, and converted for display. This is the
                  honest mode. Run your fade here and watch it rush to bright
                  and plateau — then fix it with gamma.build_lut(). See
                  gamma.py, and Part C of the README.

USAGE
-----
    python matrix_sim.py --demo sweep      # is my terminal capable? start here
    python matrix_sim.py --demo gamma      # the gamma bug and its fix
    python matrix_sim.py --demo easing     # linear vs eased motion
    python matrix_sim.py --demo alarm      # a legibility test at 3 metres

    from matrix_sim import TerminalMatrix
    with TerminalMatrix(64, 32, panel="led") as m:
        m.fill(0, 0, 0)
        m.set_pixel(10, 4, 255, 40, 40)
        m.show()

REQUIREMENTS: Python 3.8+, and a terminal that supports 24-bit color
(Windows Terminal, iTerm2, macOS Terminal, GNOME Terminal, Konsole, Alacritty,
kitty, WSL). Older terminals: see --probe.
"""

import argparse
import math
import os
import shutil
import signal
import sys
import time

import easing
import gamma as gammalib

UPPER_HALF = "▀"

ESC = "\x1b"
ALT_SCREEN_ON = f"{ESC}[?1049h"
ALT_SCREEN_OFF = f"{ESC}[?1049l"
CURSOR_HIDE = f"{ESC}[?25l"
CURSOR_SHOW = f"{ESC}[?25h"
CURSOR_HOME = f"{ESC}[H"
RESET = f"{ESC}[0m"


def _enable_windows_vt():
    """Windows consoles need ANSI escape processing switched on explicitly.
    Harmless no-op everywhere else. Without this you see raw escape codes."""
    if os.name != "nt":
        return
    try:
        import ctypes
        k = ctypes.windll.kernel32
        for handle_id in (-11, -12):  # stdout, stderr
            h = k.GetStdHandle(handle_id)
            mode = ctypes.c_uint32()
            if k.GetConsoleMode(h, ctypes.byref(mode)):
                k.SetConsoleMode(h, mode.value | 0x0004)
    except Exception:
        pass


# --------------------------------------------------------------------------
# The driver interface. Your animation code should only ever see this.
# --------------------------------------------------------------------------

class Matrix:
    """Abstract LED matrix driver.

    Implement these four methods against real hardware and every animation you
    wrote for the simulator keeps working, unchanged. That is the point of
    having an interface, and it is worth marks in Part C.
    """

    def __init__(self, width: int = 64, height: int = 32):
        if height % 2 != 0:
            raise ValueError("height must be even (two pixels share one cell)")
        self.width = width
        self.height = height

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        raise NotImplementedError

    def fill(self, r: int = 0, g: int = 0, b: int = 0) -> None:
        raise NotImplementedError

    def show(self) -> None:
        """Push the framebuffer to the display. Call once per frame, never
        per pixel."""
        raise NotImplementedError

    def close(self) -> None:
        pass

    # convenience built on top of the four primitives ----------------------

    def rect(self, x, y, w, h, r, g, b, filled=True):
        if filled:
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    self.set_pixel(xx, yy, r, g, b)
        else:
            for xx in range(x, x + w):
                self.set_pixel(xx, y, r, g, b)
                self.set_pixel(xx, y + h - 1, r, g, b)
            for yy in range(y, y + h):
                self.set_pixel(x, yy, r, g, b)
                self.set_pixel(x + w - 1, yy, r, g, b)

    def hline(self, x, y, w, r, g, b):
        for xx in range(x, x + w):
            self.set_pixel(xx, y, r, g, b)

    def vline(self, x, y, h, r, g, b):
        for yy in range(y, y + h):
            self.set_pixel(x, yy, r, g, b)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


class TerminalMatrix(Matrix):
    """Half-block terminal backend."""

    def __init__(self, width=64, height=32, panel="srgb", gamma_value=gammalib.GAMMA,
                 origin_row=1, origin_col=1, luma_log=None, alt_screen=True):
        super().__init__(width, height)
        if panel not in ("srgb", "led"):
            raise ValueError("panel must be 'srgb' or 'led'")
        self.panel = panel
        self.origin_row = origin_row
        self.origin_col = origin_col
        self.alt_screen = alt_screen
        self._buf = bytearray(width * height * 3)
        self._closed = False
        self._frames = 0
        self._t0 = time.monotonic()

        # panel="led": buffer is linear duty, so decode it for the sRGB display.
        self._display_lut = [gammalib.duty_to_srgb(i, gamma_value) for i in range(256)] \
            if panel == "led" else None

        # optional flash-safety trace, consumed by flash_audit.py
        self._luma_log = open(luma_log, "w", buffering=1) if luma_log else None
        if self._luma_log:
            self._luma_log.write("t,mean_luminance\n")

        _enable_windows_vt()
        self._check_terminal_size()
        out = []
        if alt_screen:
            out.append(ALT_SCREEN_ON)
        out.append(CURSOR_HIDE)
        sys.stdout.write("".join(out))
        sys.stdout.flush()

        self._prev_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self._on_sigint)

    # -- lifecycle ---------------------------------------------------------

    def _check_terminal_size(self):
        cols, rows = shutil.get_terminal_size((80, 24))
        need_cols = self.width + self.origin_col - 1
        need_rows = self.height // 2 + self.origin_row + 1
        if cols < need_cols or rows < need_rows:
            sys.stderr.write(
                f"\nTerminal is {cols}x{rows}; this matrix needs at least "
                f"{need_cols}x{need_rows}.\n"
                f"Make the window bigger (or zoom out with Ctrl+-) and rerun.\n\n")
            raise SystemExit(2)

    def _on_sigint(self, signum, frame):
        self.close()
        signal.signal(signal.SIGINT, self._prev_sigint)
        raise KeyboardInterrupt

    def close(self):
        if self._closed:
            return
        self._closed = True
        tail = [RESET, CURSOR_SHOW]
        if self.alt_screen:
            tail.append(ALT_SCREEN_OFF)
        sys.stdout.write("".join(tail))
        sys.stdout.flush()
        if self._luma_log:
            self._luma_log.close()

    # -- framebuffer -------------------------------------------------------

    def set_pixel(self, x, y, r, g, b):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return  # silently clip; an off-panel write is not an error
        i = (y * self.width + x) * 3
        self._buf[i] = r & 0xFF
        self._buf[i + 1] = g & 0xFF
        self._buf[i + 2] = b & 0xFF

    def get_pixel(self, x, y):
        i = (y * self.width + x) * 3
        return self._buf[i], self._buf[i + 1], self._buf[i + 2]

    def fill(self, r=0, g=0, b=0):
        if r == g == b:
            self._buf[:] = bytes([r & 0xFF]) * len(self._buf)
        else:
            self._buf[:] = bytes([r & 0xFF, g & 0xFF, b & 0xFF]) * (self.width * self.height)

    # -- render ------------------------------------------------------------

    def show(self, t=None):
        """One frame -> one write() call.

        `t` optionally overrides the timestamp written to the luma log. Pass
        your animation clock when you want a deterministic, reproducible trace
        for flash_audit.py; leave it None to use the wall clock.

        Two things make this fast enough to be smooth at 60fps in Python:
          1. Build the whole frame as a single string and write it once.
             Per-cell writes make the terminal flush 1024 times and it crawls.
          2. Only emit a color escape when the color actually changes from the
             previous cell. Large flat regions collapse to a few bytes.
        """
        lut = self._display_lut
        buf = self._buf
        w = self.width
        out = [f"{ESC}[{self.origin_row};{self.origin_col}H"]
        last_fg = last_bg = None

        for row in range(self.height // 2):
            top = row * 2 * w * 3
            bot = (row * 2 + 1) * w * 3
            for x in range(w):
                ti, bi = top + x * 3, bot + x * 3
                fr, fg_, fb = buf[ti], buf[ti + 1], buf[ti + 2]
                br, bg_, bb = buf[bi], buf[bi + 1], buf[bi + 2]
                if lut is not None:
                    fr, fg_, fb = lut[fr], lut[fg_], lut[fb]
                    br, bg_, bb = lut[br], lut[bg_], lut[bb]
                fg = (fr, fg_, fb)
                bg = (br, bg_, bb)
                if fg != last_fg:
                    out.append(f"{ESC}[38;2;{fr};{fg_};{fb}m")
                    last_fg = fg
                if bg != last_bg:
                    out.append(f"{ESC}[48;2;{br};{bg_};{bb}m")
                    last_bg = bg
                out.append(UPPER_HALF)
            out.append(f"{RESET}{ESC}[{self.origin_row + row + 1};{self.origin_col}H")
            last_fg = last_bg = None

        sys.stdout.write("".join(out))
        sys.stdout.flush()
        self._frames += 1

        if self._luma_log:
            stamp = t if t is not None else time.monotonic() - self._t0
            self._luma_log.write(f"{stamp:.4f},{self.mean_luminance():.6f}\n")

    def mean_luminance(self) -> float:
        """Average WCAG relative luminance of the whole panel, 0..1.

        Sampled every 4th pixel — this runs per frame and exactness buys you
        nothing here. Used for the seizure-safety check: it is the FULL-FIELD
        luminance swing over time that matters, not any single pixel."""
        buf, total, n = self._buf, 0.0, 0
        for i in range(0, len(buf), 12):
            total += gammalib.relative_luminance((buf[i], buf[i + 1], buf[i + 2]))
            n += 1
        return total / max(1, n)

    def status(self, text: str, row_offset: int = 1):
        """Print a line of ordinary text under the panel. This is a DEV AID.
        Your matrix design may not rely on it — a real panel has no caption."""
        r = self.origin_row + self.height // 2 + row_offset
        sys.stdout.write(f"{ESC}[{r};{self.origin_col}H{ESC}[2K{text}")
        sys.stdout.flush()

    @property
    def fps(self) -> float:
        dt = time.monotonic() - self._t0
        return self._frames / dt if dt > 0 else 0.0


# --------------------------------------------------------------------------
# Demos — run these before you write a line of your own code.
# --------------------------------------------------------------------------

def demo_sweep(args):
    """Capability check: color, half-blocks, and a delta-time animation loop."""
    with TerminalMatrix(args.width, args.height, panel=args.panel) as m:
        last = time.monotonic()
        t = 0.0
        while t < args.seconds:
            now = time.monotonic()
            dt = now - last
            last = now
            t += dt
            m.fill(0, 0, 0)
            for x in range(m.width):
                hue = (x / m.width + t * 0.15) % 1.0
                r, g, b = _hsv(hue, 1.0, 1.0)
                h = int(2 + 14 * (0.5 + 0.5 * math.sin(t * 2.0 + x * 0.2)))
                for y in range(m.height // 2 - h // 2, m.height // 2 + h // 2):
                    m.set_pixel(x, y, r, g, b)
            m.show()
            m.status(f"sweep  panel={args.panel}  {m.fps:5.1f} fps   Ctrl+C to quit")
            time.sleep(max(0.0, 1.0 / args.fps - (time.monotonic() - now)))


def demo_gamma(args):
    """The whole point of gamma.py, made visible.

    Two identical ramps, 0 -> 255 left to right.
      TOP    raw linear values written straight to the panel
      BOTTOM the same values pushed through the gamma LUT first

    Run with --panel led (the default for this demo). The top ramp reaches
    "bright" about a third of the way across and then stops changing. The
    bottom one fades evenly. That is the bug and that is the fix.
    """
    lut = gammalib.build_lut()
    with TerminalMatrix(args.width, args.height, panel="led") as m:
        m.fill(0, 0, 0)
        for x in range(m.width):
            v = int(round(255 * x / max(1, m.width - 1)))
            for y in range(2, 13):
                m.set_pixel(x, y, v, v, v)               # raw -> wrong
            for y in range(19, 30):
                c = lut[v]
                m.set_pixel(x, y, c, c, c)               # gamma-encoded -> right
        for x in range(m.width):
            m.set_pixel(x, 15, 20, 20, 30)
            m.set_pixel(x, 16, 20, 20, 30)
        m.show()
        m.status("TOP = raw linear duty (bunches up, then plateaus)")
        sys.stdout.write(f"\n  BOTTOM = gamma-encoded (even fade)  --  Enter to quit")
        sys.stdout.flush()
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass


def demo_easing(args):
    """Same distance, same duration, four different curves. Watch the stops."""
    curves = ["linear", "ease_out_cubic", "ease_in_out_cubic", "ease_out_back"]
    colors = [(120, 120, 120), (80, 200, 255), (120, 255, 140), (255, 170, 60)]
    with TerminalMatrix(args.width, args.height, panel=args.panel) as m:
        last = time.monotonic()
        t = 0.0
        period = 2.2
        while t < args.seconds:
            now = time.monotonic()
            dt = now - last
            last = now
            t += dt
            m.fill(4, 4, 8)
            phase = (t % period) / period
            p = easing.ping_pong(phase)
            for i, (name, col) in enumerate(zip(curves, colors)):
                v = easing.EASINGS[name](p)
                x = int(round(2 + v * (m.width - 8)))
                band = 3 + i * 7
                for yy in range(band, band + 4):
                    for xx in range(x, x + 4):
                        m.set_pixel(xx, yy, *col)
            m.show()
            m.status("linear / ease_out_cubic / ease_in_out_cubic / ease_out_back")
            time.sleep(max(0.0, 1.0 / args.fps - (time.monotonic() - now)))


def demo_alarm(args):
    """A legibility probe, not a design to copy.

    Stand up and walk 3 metres away from your screen. Squint. Can you still
    tell these three states apart? That is the bar your Part C has to clear,
    and it is why color alone will not save you: the shapes and the MOTION
    differ too, so the states survive both distance and colorblindness.

    Note the pulse rate: 1.2 Hz. Deliberately far below the 3-60 Hz band that
    can trigger photosensitive seizures. See README Part C.
    """
    states = [
        ("NOMINAL",  (40, 200, 120), 0.30, "steady"),
        ("DEGRADED", (240, 170, 40), 1.20, "pulse"),
        ("FAULT",    (255, 60, 50),  1.20, "sweep"),
    ]
    with TerminalMatrix(args.width, args.height, panel=args.panel) as m:
        last = time.monotonic()
        t = 0.0
        while t < args.seconds:
            now = time.monotonic()
            dt = now - last
            last = now
            t += dt
            idx = int(t / 3.0) % len(states)
            name, col, hz, kind = states[idx]
            m.fill(2, 2, 4)
            phase = (t * hz) % 1.0
            if kind == "steady":
                k = 1.0
            elif kind == "pulse":
                k = 0.35 + 0.65 * easing.smoothstep(easing.ping_pong(phase))
            else:
                k = 1.0
            c = tuple(int(v * k) for v in col)

            if kind == "steady":
                m.rect(24, 12, 16, 8, *c)
            elif kind == "pulse":
                m.rect(22, 10, 20, 12, *c, filled=False)
                m.rect(26, 14, 12, 4, *c)
            else:
                m.rect(20, 8, 24, 16, *c, filled=False)
                for i in range(-6, 7):
                    m.set_pixel(32 + i, 16 + i, *c)
                    m.set_pixel(32 + i, 16 - i, *c)
                x = int(easing.ease_in_out_cubic(easing.ping_pong(phase)) * (m.width - 1))
                m.vline(x, 0, m.height, 90, 20, 20)
            m.show()
            m.status(f"{name:<9} — walk 3 m back. Still unambiguous?")
            time.sleep(max(0.0, 1.0 / args.fps - (time.monotonic() - now)))


def demo_probe(args):
    """No alt-screen, no animation. If this prints three colored blocks, your
    terminal can do everything this challenge needs."""
    _enable_windows_vt()
    print("If you see a red, a green and a blue block below, you are good:")
    for (r, g, b) in ((220, 60, 50), (60, 200, 110), (70, 130, 240)):
        sys.stdout.write(f"{ESC}[38;2;{r};{g};{b}m" + UPPER_HALF * 20 + RESET + "\n")
    print("\nIf you see escape sequences as literal text instead, your terminal")
    print("does not have 24-bit color. On Windows use Windows Terminal or WSL.")
    cols, rows = shutil.get_terminal_size((80, 24))
    print(f"\nTerminal size: {cols}x{rows}  (need >= {args.width}x{args.height // 2 + 2})")


def _hsv(h, s, v):
    i = int(h * 6.0)
    f = h * 6.0 - i
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    r, g, b = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i % 6]
    return int(r * 255), int(g * 255), int(b * 255)


DEMOS = {
    "sweep": demo_sweep,
    "gamma": demo_gamma,
    "easing": demo_easing,
    "alarm": demo_alarm,
    "probe": demo_probe,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", choices=sorted(DEMOS), default="sweep")
    ap.add_argument("--width", type=int, default=64)
    ap.add_argument("--height", type=int, default=32)
    ap.add_argument("--panel", choices=("srgb", "led"), default="srgb",
                    help="'led' simulates real linear-PWM hardware (see gamma.py)")
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--seconds", type=float, default=1e9)
    args = ap.parse_args()
    try:
        DEMOS[args.demo](args)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
