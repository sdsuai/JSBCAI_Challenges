# Starter examples — what each one is for

Every file here shows the **mechanics** of one part of the assignment.
Read it, run it, then adapt it into your own system. Copy-pasting a file
unmodified will not satisfy the requirement it supports — the requirement
is always bigger than the example.

**Everything exists in both languages.** Same interfaces, same behaviour,
byte-identical numeric output. If you write C++ you are not working from a
Python reference, and vice versa.

## Quick index (by requirement)

| Supports | Python | C++ |
| -------- | ------ | --- |
| **Part C** — LED matrix, driver interface, half-block renderer | `python/matrix_sim.py` | `cpp/matrix_sim.hpp` |
| **Part C** — gamma / PWM vs perception | `python/gamma.py` | `cpp/gamma.hpp` |
| **Part C** — easing, delta-time animation | `python/easing.py` | `cpp/easing.hpp` |
| **Part C** — seizure-safety audit (flash rate) | `python/flash_audit.py` | *(use the Python tool; it reads a CSV either language can write)* |
| **Parts A/B/C** — replaying the canonical timeline | `python/scenario_player.py` | `cpp/scenario.hpp` |
| **Part A** — TUI mechanics: resize, too-small, NO_COLOR, non-blocking input | `python/tui_minimal.py` | `cpp/tui_minimal.cpp` |
| **Part B** — GUI mechanics: worker thread, five interaction states, spacing scale | `python/gui_minimal.py` | *(pick your own toolkit — see below)* |
| **Part 0 / accessibility** — WCAG contrast checking | `python/contrast.py` | `cpp/gamma.hpp` (`contrast_ratio`) |
| reference — how `scenario.jsonl` was produced | `python/make_scenario.py` | — |

## Start here

Before writing anything, confirm your terminal can do what this challenge needs:

```bash
# Python
cd examples/python && python3 matrix_sim.py --demo probe

# C++
cd examples/cpp && make && ./demo probe
```

You should see three colored bars. If you see raw escape sequences instead, your
terminal lacks 24-bit color — on Windows use Windows Terminal or WSL.

Then run the four demos. They take about a minute total and they are the
fastest way to understand what Part C is asking for:

```bash
python3 matrix_sim.py --demo sweep      # capability check + delta-time loop
python3 matrix_sim.py --demo gamma      # THE bug, and its fix, side by side
python3 matrix_sim.py --demo easing     # linear vs eased motion
python3 matrix_sim.py --demo alarm      # legibility at 3 metres

./demo sweep                            # identical, in C++
./demo gamma
./demo easing
./demo alarm
```

And see the timeline you will be building against:

```bash
python3 scenario_player.py --list       # every event, with timings
python3 scenario_player.py --at 58      # exact state at the E-STOP
./demo scenario                         # same, from C++
```

## Install

**Python** — the starters use only the standard library. There is no
`pip install` step for anything required.

- `gui_minimal.py` uses `tkinter`, bundled with Python on Windows and macOS.
  On Debian/Ubuntu/WSL: `sudo apt install python3-tk`.
- `tui_minimal.py` uses `curses`, bundled on macOS and Linux. On Windows:
  run it under WSL, or `pip install windows-curses`.
- `requirements.txt` lists only the OPTIONAL libraries some people prefer.

**C++** — a C++17 compiler. `make` builds `./demo` with no dependencies at all.
`make tui` additionally needs ncurses:

| | |
| --- | --- |
| Debian / Ubuntu / WSL | `sudo apt install build-essential libncurses-dev` |
| macOS | `xcode-select --install` (ncurses ships with it) |
| Windows | build under WSL, or use [FTXUI](https://github.com/ArthurSonzogni/FTXUI) — header-only, no ncurses, builds natively |

Only the TUI starter needs ncurses. If it fights you, it never blocks the
matrix work.

## You are not required to use any of this

These are conveniences, not constraints. Other perfectly good choices:

- **TUI** — Python: `rich`, `textual`, `blessed`. C++: ncurses, FTXUI, notcurses.
- **GUI** — Python: PySide6/PyQt, Dear PyGui, Kivy. C++: Qt, Dear ImGui, FLTK, raylib, nanogui.
- **Matrix** — any renderer you like, including a real panel if you own one
  (extra credit). Keep the driver interface so the simulator still works, because
  we have to be able to run your submission without your hardware.

What you may **not** do is skip the parts these files exist to make easy —
the resize handling, the worker thread, the gamma correction, the flash audit.
They are requirements, and the starters are there so they cost you an hour
instead of a weekend.
