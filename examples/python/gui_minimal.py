"""
gui_minimal.py — the mechanics of a desktop GUI that never freezes.

Again: NOT a design. It is plain on purpose. It exists to hand you the three
things that sink student GUI submissions.

  1. THE FROZEN WINDOW. A GUI has exactly one thread allowed to touch widgets.
     If you do work on it -- a sleep, a socket read, a file parse, a scenario
     loop -- the window stops redrawing, ignores clicks, and the OS greys it
     out and offers to kill it. Here the scenario runs on a WORKER thread and
     hands data to the UI thread through a Queue, drained by `after()`. Any
     long operation in your submission must do the same, and it must show
     progress while it runs. A spinner is not optional politeness; it is the
     only thing distinguishing "working" from "crashed".

  2. INTERACTION STATES. Every control has five, and shipping only one is the
     most common way a GUI feels amateur:
         default   hover   focus(keyboard)   active(pressed)   disabled
     `StateButton` below implements all five, including a visible focus ring
     that is NOT the same as hover -- a keyboard user must be able to see
     where they are. Tab through this window without touching the mouse.

  3. A SPACING SCALE. Every pad and gap here is a multiple of SPACE (8 px).
     Sizes come from TYPE. Nothing is a number somebody eyeballed once. When a
     reviewer asks "why is that gap 13 pixels?" the answer must not be "it
     looked right". Two or three sizes, consistently applied, read as designed;
     nine arbitrary ones read as accidental, even when nobody can say why.

Uses only tkinter from the standard library, so there is nothing to install on
Windows or macOS. On Debian/Ubuntu: `sudo apt install python3-tk`.

You are NOT required to use tkinter. Qt (PySide6/PyQt), Dear PyGui, or on the
C++ side Qt, Dear ImGui, FLTK, raylib, or nanogui are all welcome and several
are nicer. Whatever you pick, these three problems are still yours to solve.

Run:  python gui_minimal.py
"""

import argparse
import queue
import threading
import time
import tkinter as tk
from tkinter import font as tkfont

from scenario_player import ScenarioPlayer

# --- design tokens ----------------------------------------------------------
# One place. Shared, in your submission, with the TUI and the matrix.
SPACE = 8
BG        = "#12141a"
SURFACE   = "#1b1f28"
TEXT      = "#e6e9ef"
TEXT_DIM  = "#8b93a7"
NOMINAL   = "#39c07a"
DEGRADED  = "#e0a12c"
FAULT     = "#e04b45"
FOCUS     = "#5aa9ff"

SEVERITY = {"ok": (NOMINAL, "OK"), "degraded": (DEGRADED, "WARN"),
            "down": (FAULT, "FAIL"), "lost": (FAULT, "LOST")}


class StateButton(tk.Frame):
    """(2) One control, five visible states, keyboard-reachable."""

    def __init__(self, master, text, command=None, danger=False, **kw):
        super().__init__(master, bg=BG, highlightthickness=2,
                         highlightbackground=BG, highlightcolor=FOCUS, **kw)
        self.command = command
        self.danger = danger
        self.enabled = True
        self._hover = False
        self._pressed = False
        self.label = tk.Label(self, text=text, bg=SURFACE, fg=TEXT,
                              padx=SPACE * 2, pady=SPACE, cursor="hand2")
        self.label.pack(fill="both", expand=True)

        self.bind("<FocusIn>", lambda e: self._paint())
        self.bind("<FocusOut>", lambda e: self._paint())
        self.bind("<Return>", self._activate)      # keyboard activation
        self.bind("<space>", self._activate)
        for w in (self, self.label):
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)
            w.bind("<ButtonPress-1>", self._press)
            w.bind("<ButtonRelease-1>", self._release)
        self.configure(takefocus=True)
        self._paint()

    def set_enabled(self, on: bool):
        self.enabled = on
        self.configure(takefocus=bool(on))
        self._paint()

    def _enter(self, _=None):
        self._hover = True; self._paint()

    def _leave(self, _=None):
        self._hover = self._pressed = False; self._paint()

    def _press(self, _=None):
        if self.enabled:
            self._pressed = True; self.focus_set(); self._paint()

    def _release(self, _=None):
        was = self._pressed
        self._pressed = False
        self._paint()
        if was and self.enabled and self.command:
            self.command()

    def _activate(self, _=None):
        if self.enabled and self.command:
            self.command()

    def _paint(self):
        base = FAULT if self.danger else SURFACE
        if not self.enabled:
            # Disabled must look unavailable AND stop responding. Greying it
            # out while it still fires is worse than not greying it at all.
            self.label.configure(bg=SURFACE, fg=TEXT_DIM, cursor="")
        elif self._pressed:
            self.label.configure(bg=_shade(base, -0.25), fg=TEXT, cursor="hand2")
        elif self._hover:
            self.label.configure(bg=_shade(base, 0.18), fg=TEXT, cursor="hand2")
        else:
            self.label.configure(bg=base, fg=TEXT, cursor="hand2")
        # Focus ring is distinct from hover on purpose.
        focused = self.focus_get() is self
        self.configure(highlightbackground=FOCUS if focused else BG,
                       highlightcolor=FOCUS if focused else BG)


def _shade(hex_color, amount):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    if amount >= 0:
        r, g, b = (int(c + (255 - c) * amount) for c in (r, g, b))
    else:
        r, g, b = (int(c * (1 + amount)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


class Dashboard(tk.Tk):
    def __init__(self, player):
        super().__init__()
        self.title("ROVER-01  (mechanics demo — not a design)")
        self.configure(bg=BG)
        self.geometry("560x420")
        self.minsize(420, 320)

        # (3) sizes come from a scale, not from taste-per-widget
        self.f_big = tkfont.Font(family="TkDefaultFont", size=22, weight="bold")
        self.f_mid = tkfont.Font(family="TkDefaultFont", size=12)
        self.f_small = tkfont.Font(family="TkDefaultFont", size=9)

        self.q = queue.Queue()
        self.player = player
        self.stop_flag = threading.Event()
        self.latest = player.ticks[0]

        self._build()
        # (1) worker produces, UI thread consumes. The worker NEVER touches a
        # widget -- doing so from a non-UI thread is undefined behaviour in
        # every GUI toolkit, and in tkinter it hangs at random.
        threading.Thread(target=self._worker, daemon=True).start()
        self.after(33, self._pump)
        self.protocol("WM_DELETE_WINDOW", self._quit)

    def _build(self):
        pad = dict(padx=SPACE * 2, pady=SPACE)
        head = tk.Frame(self, bg=BG); head.pack(fill="x", **pad)
        self.state_lbl = tk.Label(head, text="—", font=self.f_big, bg=BG, fg=TEXT)
        self.state_lbl.pack(side="left")
        self.clock_lbl = tk.Label(head, text="", font=self.f_small, bg=BG, fg=TEXT_DIM)
        self.clock_lbl.pack(side="right")

        self.batt_lbl = tk.Label(self, text="", font=self.f_mid, bg=BG, fg=TEXT, anchor="w")
        self.batt_lbl.pack(fill="x", **pad)
        self.batt_canvas = tk.Canvas(self, height=SPACE * 2, bg=SURFACE,
                                     highlightthickness=0)
        self.batt_canvas.pack(fill="x", padx=SPACE * 2)

        self.sensor_lbls = {}
        row = tk.Frame(self, bg=BG); row.pack(fill="x", **pad)
        for name in ("lidar", "imu", "comms"):
            cell = tk.Frame(row, bg=BG); cell.pack(side="left", padx=(0, SPACE * 3))
            tk.Label(cell, text=name.upper(), font=self.f_small,
                     bg=BG, fg=TEXT_DIM).pack(anchor="w")
            lbl = tk.Label(cell, text="—", font=self.f_mid, bg=BG, fg=TEXT)
            lbl.pack(anchor="w")
            self.sensor_lbls[name] = lbl

        self.task_lbl = tk.Label(self, text="", font=self.f_mid, bg=BG,
                                 fg=TEXT_DIM, anchor="w")
        self.task_lbl.pack(fill="x", **pad)

        btns = tk.Frame(self, bg=BG); btns.pack(fill="x", **pad)
        self.b_pause = StateButton(btns, "Pause", command=self._toggle_pause)
        self.b_pause.pack(side="left", padx=(0, SPACE))
        self.b_restart = StateButton(btns, "Restart", command=self._restart)
        self.b_restart.pack(side="left", padx=(0, SPACE))
        self.b_estop = StateButton(btns, "E-STOP", command=self._estop, danger=True)
        self.b_estop.pack(side="right")

        tk.Label(self, text="Tab / Shift-Tab to move focus, Enter or Space to activate.",
                 font=self.f_small, bg=BG, fg=TEXT_DIM).pack(pady=(0, SPACE))
        self.paused = False

    # -- (1) threading -----------------------------------------------------

    def _worker(self):
        """Runs off the UI thread. Only ever puts plain data on a Queue."""
        while not self.stop_flag.is_set():
            if not self.paused:
                tick = self.player.poll()
                self.q.put(("tick", tick))
                for note in self.player.drain_notes():
                    self.q.put(("note", note))
            time.sleep(1 / 30)

    def _pump(self):
        """Runs ON the UI thread, scheduled by tkinter. Safe to touch widgets."""
        try:
            while True:
                kind, payload = self.q.get_nowait()
                if kind == "tick":
                    self.latest = payload
        except queue.Empty:
            pass
        self._render(self.latest)
        self.after(33, self._pump)

    # -- render ------------------------------------------------------------

    def _render(self, tick):
        self.state_lbl.configure(text=tick["state"],
                                 fg=FAULT if tick["estop"] else TEXT)
        self.clock_lbl.configure(text=f"t = {tick['t']:.1f}s" +
                                      ("   PAUSED" if self.paused else ""))
        batt = tick["battery_pct"]
        col = FAULT if batt < 8 else (DEGRADED if batt < 20 else NOMINAL)
        word = "CRITICAL" if batt < 8 else ("LOW" if batt < 20 else "OK")
        self.batt_lbl.configure(text=f"Battery  {batt:.1f}%   {word}", fg=col)
        c = self.batt_canvas
        c.delete("all")
        w = max(1, c.winfo_width())
        c.create_rectangle(0, 0, w * batt / 100, SPACE * 2, fill=col, width=0)

        for name, lbl in self.sensor_lbls.items():
            colr, word = SEVERITY.get(tick[name], (TEXT_DIM, "?"))
            lbl.configure(text=f"{word}  ({tick[name]})", fg=colr)

        self.task_lbl.configure(
            text=(f"{tick['task']}   {tick['task_idx']}/{tick['task_total']}"
                  if tick["task"] else "no active task"))
        self.b_estop.set_enabled(not tick["estop"])

    # -- commands ----------------------------------------------------------

    def _toggle_pause(self):
        self.paused = not self.paused
        self.b_pause.label.configure(text="Resume" if self.paused else "Pause")

    def _restart(self):
        self.player.restart()

    def _estop(self):
        # Left as a question, not an answer: should this confirm first?
        # See Part B of the README. Whatever you decide, defend it.
        self.state_lbl.configure(text="ESTOP (demo)", fg=FAULT)

    def _quit(self):
        self.stop_flag.set()
        self.destroy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="../../scenario/scenario.jsonl")
    ap.add_argument("--speed", type=float, default=1.0)
    args = ap.parse_args()
    Dashboard(ScenarioPlayer(args.file, speed=args.speed, loop=True)).mainloop()


if __name__ == "__main__":
    main()
