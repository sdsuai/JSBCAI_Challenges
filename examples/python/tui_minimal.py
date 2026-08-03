"""
tui_minimal.py — the mechanics of a TUI that does not fall apart.

This is NOT a design. It is deliberately ugly. It exists so you never have to
debug the four things that make people give up on curses, and can spend your
time on the part we are actually grading.

The four things:

  1. RESIZE. Terminals change size while you are running. curses delivers
     KEY_RESIZE; if you ignore it your layout is corrupt for the rest of the
     session. Handled in `_on_resize`. Drag your terminal edge while this runs.

  2. TOO SMALL. At some point the window cannot hold your layout. Garbling is
     not acceptable and neither is crashing. Say so, in words, and recover the
     moment there is room again. See `_draw_too_small`.

  3. NO COLOR. `NO_COLOR=1 python tui_minimal.py` must still be fully usable,
     and so must a monochrome terminal. This is not just accessibility
     box-ticking: roughly 1 in 12 men has a color vision deficiency, and your
     operator may be on a washed-out projector. Every state here carries a
     TEXT marker as well as a color. Never encode meaning in color alone.

  4. INPUT LATENCY. `nodelay(True)` makes getch() non-blocking so the render
     loop never stalls waiting for a keypress. A TUI that pauses its animation
     while you hold a key feels broken.

Run:
    python tui_minimal.py
    NO_COLOR=1 python tui_minimal.py
    python tui_minimal.py --speed 4

Keys: q quit,  ? help,  space pause,  r restart

Windows note: the stdlib `curses` module is not bundled with Python on
Windows. Either run this under WSL, or `pip install windows-curses`, or write
your TUI with a cross-platform library. Python options that need no curses:
`rich` / `textual`. C++ options: ncursesw, or FTXUI (header-only, builds on
Windows). Any of these is fine for your submission.
"""

import argparse
import curses
import os
import time

from scenario_player import ScenarioPlayer

# Semantic names, not color names. When you decide FAULT should be orange
# instead of red you change one line, and nothing else in the file mentions
# a color. This is the smallest possible version of a design-token file --
# yours will be bigger and SHARED WITH ALL THREE SURFACES.
TOKENS = {
    "nominal":  {"pair": 1, "fg": curses.COLOR_GREEN,  "mark": "[ OK ]"},
    "degraded": {"pair": 2, "fg": curses.COLOR_YELLOW, "mark": "[WARN]"},
    "fault":    {"pair": 3, "fg": curses.COLOR_RED,    "mark": "[FAIL]"},
    "muted":    {"pair": 4, "fg": curses.COLOR_CYAN,   "mark": "      "},
}

MIN_W, MIN_H = 60, 16


class App:
    def __init__(self, stdscr, player):
        self.scr = stdscr
        self.player = player
        self.paused = False
        self.show_help = False
        self.log = []
        self.use_color = curses.has_colors() and not os.environ.get("NO_COLOR")

        curses.curs_set(0)
        stdscr.nodelay(True)          # (4) never block the loop on input
        stdscr.keypad(True)
        if self.use_color:
            curses.start_color()
            curses.use_default_colors()
            for tok in TOKENS.values():
                curses.init_pair(tok["pair"], tok["fg"], -1)
        self._on_resize()

    # -- (1) resize --------------------------------------------------------

    def _on_resize(self):
        self.h, self.w = self.scr.getmaxyx()
        self.scr.clear()

    def attr(self, token):
        if not self.use_color:
            return curses.A_BOLD if token == "fault" else curses.A_NORMAL
        return curses.color_pair(TOKENS[token]["pair"])

    def put(self, y, x, text, token="muted", bold=False):
        """Clipped write. curses raises if you touch the last cell of the last
        line, and it raises if you write off-screen at all -- so clip, always."""
        if y < 0 or y >= self.h:
            return
        text = text[: max(0, self.w - x - 1)]
        if not text:
            return
        a = self.attr(token) | (curses.A_BOLD if bold else 0)
        try:
            self.scr.addstr(y, x, text, a)
        except curses.error:
            pass

    # -- rendering ---------------------------------------------------------

    def _draw_too_small(self):
        """(2) Honest degradation. Not a crash, not a garbled screen."""
        self.scr.erase()
        msg = f"Window too small: {self.w}x{self.h}, need {MIN_W}x{MIN_H}"
        self.put(max(0, self.h // 2), max(0, (self.w - len(msg)) // 2), msg, "degraded", bold=True)
        hint = "resize the terminal or press q"
        self.put(max(0, self.h // 2) + 1, max(0, (self.w - len(hint)) // 2), hint, "muted")
        self.scr.refresh()

    def sensor_token(self, value):
        return {"ok": "nominal", "degraded": "degraded", "down": "fault", "lost": "fault"}.get(value, "muted")

    def draw(self, tick, dt):
        self.scr.erase()

        # header
        self.put(0, 0, "─" * (self.w - 1), "muted")
        self.put(0, 2, f" ROVER-01  {tick['state']} ", "muted", bold=True)
        clock = f" t={tick['t']:6.1f}s {'[PAUSED]' if self.paused else ''} "
        self.put(0, max(0, self.w - len(clock) - 2), clock, "muted")

        # (3) every state gets a TEXT marker as well as a color
        batt = tick["battery_pct"]
        btok = "fault" if batt < 8 else ("degraded" if batt < 20 else "nominal")
        bar_w = max(10, min(30, self.w - 34))
        filled = int(round(bar_w * batt / 100))
        self.put(2, 2, f"BATTERY {TOKENS[btok]['mark']} {batt:5.1f}%", btok, bold=(btok == "fault"))
        self.put(2, 30, "█" * filled + "░" * (bar_w - filled), btok)

        y = 4
        for name in ("lidar", "imu", "comms"):
            v = tick[name]
            tok = self.sensor_token(v)
            self.put(y, 2, f"{name.upper():<6} {TOKENS[tok]['mark']} {v}", tok)
            y += 1

        y += 1
        self.put(y, 2, f"TASK    {tick['task'] or '(none)'}", "muted")
        if tick["task_total"]:
            self.put(y + 1, 2, f"        {tick['task_idx']}/{tick['task_total']}", "muted")
        self.put(y + 2, 2, f"POSE    x={tick['x']:6.2f}  y={tick['y']:6.2f}  "
                           f"hdg={tick['heading']:5.1f}  v={tick['speed']:.2f}", "muted")

        if tick["estop"]:
            self.put(y + 4, 2, "  *** EMERGENCY STOP ENGAGED ***  ", "fault", bold=True)

        # event log -- the discrete half of the data
        ly = y + 6
        self.put(ly, 2, "EVENTS", "muted", bold=True)
        for i, (t, note) in enumerate(self.log[-max(1, self.h - ly - 3):]):
            self.put(ly + 1 + i, 2, f"{t:>6.1f}  {note}", "muted")

        self.put(self.h - 1, 2, "q quit   ? help   space pause   r restart", "muted")

        if self.show_help:
            self._draw_help()
        self.scr.refresh()

    def _draw_help(self):
        lines = ["KEYS", "", "  q      quit", "  ?      toggle this help",
                 "  space  pause / resume", "  r      restart scenario", "",
                 "  Esc or ? closes this overlay."]
        bw = max(len(s) for s in lines) + 4
        bh = len(lines) + 2
        y0, x0 = max(0, (self.h - bh) // 2), max(0, (self.w - bw) // 2)
        for i in range(bh):
            self.put(y0 + i, x0, " " * bw, "muted")
        for i, s in enumerate(lines):
            self.put(y0 + 1 + i, x0 + 2, s, "muted", bold=(i == 0))

    # -- loop --------------------------------------------------------------

    def run(self):
        last = time.monotonic()
        pause_started = None
        while True:
            now = time.monotonic()
            dt = now - last
            last = now

            ch = self.scr.getch()
            while ch != -1:
                if ch == curses.KEY_RESIZE:
                    self._on_resize()
                elif ch in (ord("q"), ord("Q")):
                    return
                elif ch == ord("?"):
                    self.show_help = not self.show_help
                elif ch == 27:                      # Esc always backs out
                    self.show_help = False
                elif ch == ord(" "):
                    self.paused = not self.paused
                    if self.paused:
                        pause_started = time.monotonic()
                    elif pause_started:
                        self.player._t0 += time.monotonic() - pause_started
                elif ch in (ord("r"), ord("R")):
                    self.player.restart()
                    self.log.clear()
                ch = self.scr.getch()

            if self.w < MIN_W or self.h < MIN_H:
                self._draw_too_small()
                time.sleep(1 / 20)
                continue

            if not self.paused:
                tick = self.player.poll()
                self.log.extend(self.player.drain_notes())
            else:
                tick = self.player.ticks[self.player._idx]

            self.draw(tick, dt)
            time.sleep(max(0.0, 1 / 30 - (time.monotonic() - now)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="../../scenario/scenario.jsonl")
    ap.add_argument("--speed", type=float, default=1.0)
    args = ap.parse_args()
    player = ScenarioPlayer(args.file, speed=args.speed, loop=True)
    curses.wrapper(lambda scr: App(scr, player).run())


if __name__ == "__main__":
    main()
