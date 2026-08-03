# 🎛 One System, Two Surfaces — UX & Interface Design Challenge · Grade 1

**JSBCAI / Robotics Lab — Interface & Interaction Design Task · Grade 1**

> This is the **Grade 1** variant: two surfaces (TUI and LED matrix).
> Grade 2 is the same challenge with a third surface (a desktop GUI) and a
> gamma-correction requirement. If you were sent here directly, this is the
> one to do — do not go looking for the other branch.

This challenge evaluates your ability to **design an interface**, not just build
one. Specifically:

* Information hierarchy under hard constraints
* TUI design (terminal, keyboard-only)
* LED matrix animation design (64×32 RGB, no text, viewed from across a room)
* Animation timing and easing
* Accessibility and failure states
* Cross-surface consistency via shared design tokens
* Being able to **defend your decisions out loud**

Most coding challenges tell you whether someone can build what they were told
to build. This one is designed to tell us whether you can *decide what to
build* when nobody specifies the layout — because that is the job.

**You are allowed to use the internet and AI assistants (ChatGPT, Claude,
Copilot, Gemini, etc.).** What matters is your **design decisions**, your
**implementation**, and the **video explanation** you submit. Use whatever gets
you there.

---

## ‼️ Important — read this whole section

* **You must code in Python and/or C++.** We prefer C++ — our lab's rendering
  and hardware work is C++ — but **a Python submission is graded on exactly the
  same rubric with no penalty and no bonus.** Choose the language you can design
  best in. Every starter we ship exists in both.
* **You do not need an LED matrix.** You are not assumed to own any hardware at
  all. The matrix is simulated in your terminal with zero dependencies (see
  Part B). If you *do* own a panel, that is extra credit — never a requirement.
* **This runs on any laptop — macOS, Linux, or Windows.** No GPU, no network, no
  accounts, nothing to buy, no dev boards. Everything is local. If your machine
  can run a terminal and either Python or a C++ compiler, you can do all of
  this. See [Platform support](#-platform-support) below for the details.
* **This task requires you to run your code from your machine's OS terminal.**
  On Windows that is PowerShell (there's another shell too, I think); on macOS
  and Linux a common one is bash. Your OS might use a different terminal from
  what I mentioned, or might have several — doesn't matter, just use one.
* **On Windows, we recommend you work in WSL** (Windows Subsystem for Linux).
  Not required — everything here runs natively on Windows too — but WSL gives
  you the same environment the lab actually runs on, makes both TUI starters
  work with no extra packages, and means every install command in this repo is
  the one you'll type. If you plan to volunteer here, you will end up using
  Linux anyway; setting it up now is an hour well spent. `wsl --install` in an
  admin PowerShell, then use Windows Terminal.
* **After completing this task you will need to screen record a video** showing
  that your code works and you explaining how it works. Obviously, in the screen
  recording you MUST run your programs from the terminal.
* **Create a GitHub repo containing your code and the video.** Name it something
  like `JSB_ux_design_challenge` so it's identifiable.
* **You may freely use any tool available to you** to accomplish this task. The
  internet, ChatGPT, Claude, Copilot, anything. What we assess is your *design
  judgment*, your *implementation*, and your *video explanation*. Be aware that
  AI tools are quite bad at the specific thing we are testing here: they will
  happily hand you a layout that shows everything at once, which is exactly the
  failure mode this challenge is built to detect.
* **You may use the starter code in `examples/` to get going** if you choose. It
  shows the mechanics; the requirements are always bigger than the examples.

### 📮 Submission — READ THE ENTIRE BULLET

* **Submit a pull request to this repo** so we have your GitHub username and can
  find your work. **Do not do your actual work in the public forked repo** —
  others can copy it.
* **Make a private clone** (or however you make things private) of the fork and
  do your real work there.
* **Send an invite to the private repo to `philipamadasun1@gmail.com`** so we can
  get access.
* **Put your email address in your README.** Please don't make us go looking.
* Name the repo something identifiable, e.g. `JSB_ux_design_challenge`.

---

## ⏱ Time commitment — 5 to 7 days

**This problem set is scoped to 5–7 days of real, active work.** Not five to
seven calendar days with the tab open — five to seven days of actually sitting
down and grinding on it.

That window is deliberate, and meeting it is part of what we are measuring.

Volunteering in this lab means taking real time out of your weeknights and your
weekends, consistently, for work you have been assigned. That *is* the role. If
you can carve out that time for this challenge, you can carve it out for the
tasks we hand you once you are here. If you cannot, the fit is wrong — and it is
far better for both of us to learn that now than three weeks into a project that
is sitting blocked on you.

To be direct, because you deserve to know what you are signing up for: this is
not a role that works for someone who can look at their assignment once every
two weeks. That is not a judgment about you or your priorities. Plenty of
capable people are genuinely committed elsewhere — coursework, a job, family —
and that is completely legitimate. It is simply not compatible with the pace
this lab runs at, and pretending otherwise wastes your semester as well as ours.

**If you cannot make the window, email `philipamadasun1@gmail.com` *before* it
runs out**, explain why, and ask for more time. Real reasons exist — exam weeks,
illness, work shifts, a laptop that died. Ask and explain, and I will decide
whether the explanation warrants an extension. **Asking is never held against
you.** Going quiet and surfacing late with no word is a different thing
entirely, and it tells us what working with you would be like.

If you are running out of time, **ship two finished surfaces that each do one
thing well** rather than two half-built ones attempting everything. Say what
you cut and why in your write-up. Scoping under pressure is a design skill and
we grade it as one.

---

## 💻 Platform support

Everything in this challenge runs on **macOS, Linux, and Windows** (including
WSL). There are no third-party dependencies in any starter — the Python files
import only the standard library, and the C++ headers need only a C++17
compiler. The LED matrix simulator includes the Windows console setup
(virtual-terminal mode and UTF-8) needed for it to render correctly there.

| | macOS | Linux / WSL | Windows |
| --- | --- | --- | --- |
| Matrix simulator, gamma, easing, scenario player (both languages) | ✅ | ✅ | ✅ |
| `contrast.py`, `flash_audit.py`, `make_scenario.py` | ✅ | ✅ | ✅ |
| `tui_minimal.py` (curses) | ✅ | ✅ | ⚠️ `pip install windows-curses`, or use WSL |
| `tui_minimal.cpp` (ncurses) | ✅ | ⚠️ `sudo apt install libncurses-dev` | ⚠️ build under WSL, or use [FTXUI](https://github.com/ArthurSonzogni/FTXUI) |

The two ⚠️ TUI rows are the only real friction, they affect the *starter* rather
than the assignment, and each has a one-line fix. Your own TUI may use any
library you like — `rich`/`textual` (Python) and FTXUI (C++) are fully
cross-platform with no system packages at all.

### 🪟 Windows users: WSL is recommended

Every ⚠️ in the Windows column disappears under WSL, and there is a bigger
reason than convenience: **the lab runs on Linux.** If you join us, that is the
environment you will be working in, so the hour you spend setting up WSL now is
an hour you were going to spend eventually — and it means every install command
in this repo is exactly the one you type.

```powershell
wsl --install          # admin PowerShell, then reboot
```

Then open Ubuntu from Windows Terminal and work from there.

To be clear: **this is a recommendation, not a requirement.** Native Windows is
fully supported, the simulator handles the console setup for you, and a native
Windows submission is graded identically. If WSL fights you, drop it and move on
— finishing the challenge matters far more than which shell you finished it in.

**Terminal requirement:** you need 24-bit ("truecolor") support, which every
current terminal has — Windows Terminal, iTerm2, macOS Terminal, GNOME Terminal,
Konsole, Alacritty, kitty. Confirm yours in ten seconds with
`python3 matrix_sim.py --demo probe` (or `./demo probe`). The one thing to avoid
is the legacy Windows `conhost` console; use Windows Terminal instead.

**Pick whichever platform you already have.** No part of this challenge is
easier or harder to score well on depending on your OS, and we do not care which
one you use.

---

## 📦 Overview

You will build **one robot status-and-control console, twice**:

| Part | Surface | Constraint that makes it interesting |
| ---- | ------- | ------------------------------------ |
| **Part 0** | Design intent + wireframes | Decide before you build |
| **Part A** | **TUI** — terminal, keyboard-only | Monospace cells, resizes under you, may have no color at all |
| **Part B** | **LED matrix** — 64×32 RGB | 2048 pixels. No text. Viewed from 3 metres |
| **Part C** | Write-up and video | Defend it |

Both read **the same canonical timeline** — `scenario/scenario.jsonl`, a
106-second replay of a rover's mission that includes a transient fault, two
simultaneous faults, an emergency stop, and a recovery. Every candidate is
graded on the same events, so submissions are directly comparable.

### Why two surfaces

Because the interesting part is the **translation**.

Anybody can put fifteen numbers on a screen. The skill we are hiring for shows
up when the screen is 64×32 pixels, has no room for text, and is being looked at
from across a lab by someone holding a controller — and you have to decide what
survives.

A candidate who shrinks their TUI layout onto the matrix fails visibly. A
candidate who re-encodes the state into color, shape, and motion — and can
explain why they dropped the other twelve numbers — is who we are looking for.

> **The single most common way to fail this challenge is to show everything.**
> Two surfaces that both display the same twelve fields at different sizes are
> not two designs. They are one design, rendered twice, and it means the
> hierarchy decisions were never made.

---

## 🚀 Start here (about 10 minutes)

```bash
git clone <your private repo>
cd <repo>

# 1. Can your terminal do this? (three colored bars = yes)
cd examples/python && python3 matrix_sim.py --demo probe
#   ...or C++:
cd examples/cpp && make && ./demo probe

# 2. The four demos. Run all of them — they ARE the brief for Part B.
python3 matrix_sim.py --demo sweep     #   ./demo sweep
python3 matrix_sim.py --demo gamma     #   ./demo gamma     <-- especially this
python3 matrix_sim.py --demo easing    #   ./demo easing
python3 matrix_sim.py --demo alarm     #   ./demo alarm

# 3. The timeline you will design against
python3 scenario_player.py --list      #   ./demo scenario
```

Then read [`scenario/SCHEMA.md`](scenario/SCHEMA.md) and
[`examples/README.md`](examples/README.md).

---

## 🎯 Deliverables

1. **A GitHub repository** containing:
   * Source for both surfaces
   * A **shared design-token file** consumed by both
   * `DESIGN.md` (Part 0 — start from [`templates/DESIGN.md`](templates/DESIGN.md))
   * `README.md` with setup + run instructions **and your email address**
   * `run.sh` / `run.ps1` / `make run` that launches each surface

2. **A 6–12 minute walkthrough video** (screen recording with your voice):
   * Run both surfaces from a terminal, replaying the scenario **at 1× speed**
   * **Resize your terminal while the TUI is running**, live
   * **Run the TUI with `NO_COLOR=1`**, live
   * Show the matrix during the **E-STOP at t=58** and during **two-faults-at-once at t=55**
   * Walk 3 metres back from the screen with the matrix running, on camera
   * For each surface, say **what you chose to leave out, and why**
   * Demonstrate any extra credit you did

3. **A write-up** (in your README or `WRITEUP.md`) answering the Part C questions.

You may use AI tools throughout — but your submission must reflect **your own
design decisions, structure, debugging, and judgment**. The video is where that
becomes obvious, in both directions: a candidate who leaned on AI and
understands every choice they shipped does great, and a candidate who cannot
explain why their own matrix pulses at 1.2 Hz does not.

---

## 📐 Part 0 — Design before code *(required)*

Before you write any implementation code, produce **`DESIGN.md`**. Copy
[`templates/DESIGN.md`](templates/DESIGN.md) and fill in every section.

It must contain:

* **A viewer model per surface.** Who is looking, from how far, for how long,
  in what lighting, and what else are their hands and eyes doing. Be physical
  and specific.
* **The 300 ms question, answered once per surface.** What is the ONE thing
  legible before the viewer has focused? One thing. Not a list.
* **What you sacrificed** to make that thing primary. Something must have gotten
  smaller or dimmer. Name it.
* **Wireframes**, one per surface. Photos of paper sketches are ideal and
  explicitly preferred over polished mockups. **Sketch the matrix on an actual
  64×32 grid** — graph paper or a spreadsheet with square cells. This will save
  you a day.
* **Your severity model.** The scenario deliberately gives you *no* alarm or
  priority field (see [SCHEMA.md](scenario/SCHEMA.md)). Define what counts as an
  alarm, and how you rank two that fire at once.

Then build. Then, at the end, add the **"What changed"** section honestly —
where the plan met the screen and lost. We can tell the difference between a
design doc written first and one retro-fitted afterwards, and the honest one
scores higher even when the plan was wrong.

> Part 0 is 15 points. It is the highest points-per-hour in the challenge and
> the section most people skip. Do not skip it.

---

## ⌨️ Part A — The TUI *(required)*

A terminal interface, driven **entirely by keyboard**, replaying the scenario.

### Requirements

1. **Survives resize.** Handle terminal resize (`KEY_RESIZE` / `SIGWINCH`) and
   reflow. Dragging the window edge must never leave the layout corrupt. *We
   will do this while watching your video.*
2. **Degrades honestly when too small.** Below your minimum usable size, say so
   in words and recover the instant there is room. A garbled screen and a crash
   both score zero.
3. **Works with no color at all.** `NO_COLOR=1` must produce a fully usable
   interface, and so must a monochrome terminal. **No state may be conveyed by
   color alone** — every severity needs a text, shape, or position cue too.
   Roughly 1 in 12 men has a color vision deficiency; your operator may also be
   on a washed-out projector in daylight.
4. **Never blocks.** Non-blocking input; the display keeps updating while a key
   is held. Input to visible feedback under ~100 ms.
5. **Discoverable keys.** A `?` help overlay. `Esc` always backs out of whatever
   you are in. Consistent bindings — if `q` quits at the top level it does not
   mean something else three screens down.
6. **State and events are visually distinct.** Current state and the event log
   are different things (see SCHEMA.md) and must not look identical.
7. **Fits and works at 80×24.** It may use more space well, but 80×24 must be
   usable, not merely non-crashing.
8. **An E-STOP control.** A key the operator presses to halt the robot. Whether
   it asks for confirmation first is **your call** — see Part C. Whatever you
   decide, the video must show it and you must defend it.

Starter mechanics for all of this: `examples/python/tui_minimal.py`,
`examples/cpp/tui_minimal.cpp`. They are deliberately ugly — they solve the
plumbing so you can spend your time on the design.

---

## 💡 Part B — The LED matrix *(required — the heart of the challenge)*

A **64×32 RGB** animated display. **2048 pixels. No text.** Assume it is
mounted on the rover and read from **3 metres away** by someone who is doing
something else.

**You do not need hardware.** `matrix_sim.py` / `matrix_sim.hpp` render a matrix
in your terminal using Unicode half-blocks — the glyph `▀` paints its foreground
color on the top half of a character cell and its background on the bottom, so
one character is two pixels and a 64×32 panel fits in 64 columns × 16 rows of an
ordinary terminal. No windowing library, no pygame, no SDL, nothing to install.

### Requirements

1. **A driver interface.** Your animation code talks to
   `set_pixel / fill / show / close` and must not know whether it is holding the
   simulator or a real HUB75 panel. Swapping the backend must require zero
   changes to your animation code.
2. **Frame-rate-independent animation.** Animate against a measured clock and a
   real delta time. `for i in range(60): draw(i/60); sleep(1/60)` runs at a
   different speed on every machine and stutters whenever anything else blocks.
3. **Real easing.** At least three different curves, each chosen for a reason
   you state in `DESIGN.md`. Linear motion everywhere is the tell of an
   animation nobody designed.
4. **No color-only encoding.** Assume your viewer is colorblind, or that the
   panel's reds have drifted. Every state must also differ in **shape or
   motion**. A greyscale screenshot of your matrix must still be readable.
5. **Flash safety — this is a hard requirement, not a style note.** **No
   full-field luminance flashing between 3 Hz and 60 Hz.** Photosensitive
   seizures are triggered in exactly that band, worst around 15–20 Hz, and WCAG
   2.3.1 sets the threshold at three flashes per second. Pulse alarms at ≤2 Hz,
   or convey urgency with motion or shape instead. Record a trace and audit it:

   ```python
   m = TerminalMatrix(64, 32, luma_log="trace.csv")   # then, after your run:
   ```
   ```bash
   python3 examples/python/flash_audit.py trace.csv   # must PASS
   ```

   Paste the output in `DESIGN.md`. A slow pulse also reads as *more* serious
   than a strobe, so this constraint costs you nothing.
6. **The E-STOP must be unmistakable at 3 metres**, with no text available.
7. **Two simultaneous faults (t=52–58) must both be visible**, with one clearly
   dominant.

### The test that matters

Stand up. Walk three metres from your screen. Squint.

If you cannot tell `NOMINAL` from `DEGRADED` from `FAULT` in under a second,
the design is not finished — regardless of how good it looks at your desk.
`--demo alarm` shows the bar you are clearing.

---

## 🔗 Cross-cutting requirement — one design system *(required)*

Both surfaces must consume **one shared design-token file** (JSON, YAML,
a header, a module — your choice). It holds semantic names, not scattered
literals: `fault`, not `#e04b45` typed in eleven places.

Changing `fault` in that one file must change both surfaces. That is the
test of whether you built a system or two lookalike programs.

Check your palette before you ship:

```bash
python3 examples/python/contrast.py --palette your_tokens.json
```

Every foreground must clear **3.0:1** against every surface it can land on, and
body text should clear **4.5:1**. See `examples/tokens.example.json` for the
shape (it is an example, not a palette to copy — yours should differ and you
should be able to say why).

The two surfaces will not *look* the same — a terminal cell and an LED pixel are
different media and pretending otherwise is its own mistake. But a viewer moving between them should never have to relearn what red
means, what pulsing means, or which corner the important thing lives in.

---

## ✍️ Part C — Write-up *(required)*

Short, concrete, and **in your own words**.

You were told to use AI freely for the build, and that stands. This one section
is the exception, and for a practical reason rather than a moral one: it is the
only place we find out whether *you* understood the thing you shipped. A
generated essay about your design tells us nothing we can act on, and it is
extremely obvious when the write-up is not in the same voice as the video.

Rough and specific beats polished and generic here. Bullet points are fine.

1. **The 300 ms question.** For each surface: what is the one thing legible
   before the viewer focuses, and what did you sacrifice for it?

2. **Two faults at once.** At t=52–58 the battery is under 20% *and* the lidar
   is dying. Which did you rank higher, and why? What does the loser look like
   while the winner has priority?

3. **The transient.** The comms dropout at t=26 lasts 3.6 seconds. What does the
   operator see during it, and thirty seconds later? What is your rule for how
   long a resolved fault stays visible — and what happens if it flaps ten times
   in a minute?

4. **The E-STOP.** Does your TUI confirm before halting the robot? Argue your side.
   Consider what the operator's hand is doing in the half-second before they hit
   it, the cost of firing it by accident, the cost of a dialog when it was *not*
   an accident, and whether "are you sure?" is a real safeguard or a reflex
   click. There is a defensible answer either way; there is no defensible
   non-answer.

5. **Boot is not a fault.** At t=0–6 all three sensors read down. That is normal
   startup. How did you keep your UI from crying wolf — and why does that matter
   for whether the operator believes you at t=55?

6. **What you would do with another week.**

---

## 🛠 Extra Credit *(optional — pick what interests you)*

### 🟦 Tier 1 — laptop-friendly

| | Points | |
| --- | --- | --- |
| **Gamma correction** | +8 | PWM duty cycle is linear in *photons*; your eye is not, so a linear ramp written straight to a panel rushes to bright and then plateaus. Run `--demo gamma` to see it, then fix **your own** fade under `panel="led"` and show the before/after. Build a LUT once; do not call `pow()` per pixel per frame. This is a required part of Grade 2. |
| **Colorblind simulation** | +8 | Add a mode that filters your own UI through deuteranopia/protanopia/tritanopia simulation. **Then fix what it breaks** and show the before/after. Finding nothing to fix means you are not looking hard enough. |
| **Reduced motion** | +6 | A `--reduce-motion` flag that keeps every state distinguishable with animation off. Vestibular disorders are real, and it is a good test of whether motion was carrying meaning or decoration. |
| **Contrast in CI** | +5 | Wire `contrast.py --palette` into a pre-commit hook or GitHub Action so a failing palette breaks the build. |
| **Longest-string test** | +6 | Run every label through a pseudo-locale that inflates string length ~40% (German-style). Nothing may clip, overlap, or reflow into nonsense. |
| **Custom pixel font** | +10 | Design your own 3×5 or 4×6 font for the matrix. Include a legibility test at 3 m and say which glyph pairs you had to redesign (`8`/`B`, `5`/`S`, `0`/`O`, `1`/`I`). |
| **Latency instrumentation** | +8 | Measure input → visible-pixel latency in the TUI. Report p50 and p99, not a mean. Say which is worse and why. |
| **Cross-language surface** | +10 | Implement one surface in the *other* language against the same token file, matching semantics. |
| **Sonification** | +6 | Design audio cues for state changes. Distinguishable without looking, non-annoying at ten repetitions, and silenceable. |

### 🟧 Tier 2 — harder

| | Points | |
| --- | --- | --- |
| **Real usability test** | +15 | Two people who have never seen your UI. Give them the scenario and timed tasks ("tell me when the robot is in trouble"). Report what they got wrong, and **make one change because of it** and show it. This is the single most valuable thing on this list. |
| **Real hardware** | +12 | If you own a matrix (HUB75, WS2812, Adafruit, Pimoroni, Pi, ESP32, Arduino), implement the driver backend and film it running. **Your simulator backend must still work** — we have to run your submission without your hardware. |
| **Live-reloading tokens** | +8 | Edit the token file and watch both surfaces update without restarting. Demo it on camera. |
| **Matrix compositor** | +10 | Layers with alpha, z-order, and independent transitions, instead of drawing straight to the framebuffer. Show a layer fading over another. |

---

## 🧨 Grading Rubric

| Category | Points | What we are looking at |
| --- | --- | --- |
| **Part 0** — Design intent, wireframes, severity model | 15 | Specific viewer model; a real hierarchy decision; honest "what changed" |
| **Part A** — TUI | 25 | Resize, too-small, `NO_COLOR`, non-blocking, discoverability, 80×24, E-STOP |
| **Part B** — LED matrix | 25 | Legible at 3 m; driver interface; delta-time animation; easing; **flash audit passes**; no color-only encoding |
| **Cross-surface design system** | 10 | One token file, actually shared; contrast check passes; consistent semantics |
| **Part C** — Write-up | 10 | Concrete, in your own words, commits to answers |
| **Video walkthrough** | 15 | Required demos performed live; explains *what was left out and why* |
| | **100** | |
| **Extra credit Tier 1** | +20 max | |
| **Extra credit Tier 2** | +20 max | |
| | **140 max** | |

### How we actually read a submission

Three things carry more weight than anything else, and none of them is code
quality:

1. **Did you leave things out?** Two surfaces showing the same twelve fields
   means the hierarchy decisions were never made. We look for what is *missing*
   from the matrix first.
2. **Does `DESIGN.md` match what you built** — and where it does not, did you
   say so? An honest "I was wrong about this and here is what I changed" scores
   higher than a document quietly rewritten to match.
3. **Can you defend it in the video?** "It looked better" is not a reason.
   "The operator is glancing for two seconds while walking, so battery state had
   to survive peripheral vision, which is why it is the only thing that moves"
   is a reason. We would rather hear a defensible wrong answer than an
   undefended right one.

**Automatic point losses** — every one of these is a two-minute check we run
before anything else:

* Matrix flash audit fails (3–60 Hz full-field) — Part B capped at half marks
* Any state distinguishable only by color, on any surface
* TUI corrupts on resize, or is unusable under `NO_COLOR=1`
* No shared token file, or one that exists but is not actually consumed by both
* Video does not show both surfaces replaying the scenario at 1×

---

## 🗂 What's in this repo

```
README.md                     this file
scenario/
  scenario.jsonl              the canonical timeline — 531 ticks, 5 Hz, 106 s
  SCHEMA.md                   field reference + the five moments you are judged on
templates/
  DESIGN.md                   Part 0 skeleton — copy this to your repo root
examples/
  README.md                   index: which starter supports which requirement
  requirements.txt            OPTIONAL libraries only; nothing here is required
  tokens.example.json         example design-token file (an example, not a palette)
  python/
    matrix_sim.py             LED matrix simulator + driver interface + 5 demos
    gamma.py                  PWM vs perception; the LUT
    easing.py                 easing curves + delta-time Tween
    scenario_player.py        pull-based timeline replay
    tui_minimal.py            TUI mechanics: resize, too-small, NO_COLOR, non-blocking
    contrast.py               WCAG contrast checker (exits nonzero — CI-friendly)
    flash_audit.py            seizure-safety audit of a recorded luminance trace
    make_scenario.py          how scenario.jsonl was generated
  cpp/
    matrix_sim.hpp            same simulator, header-only, no dependencies
    gamma.hpp  easing.hpp     same maths, byte-identical output
    scenario.hpp              same player; parses the JSONL with no JSON library
    tui_minimal.cpp           same TUI mechanics, ncurses
    demo.cpp                  the same five demos
    Makefile                  `make` → ./demo   |   `make tui` → ./tui_minimal
```

---

## ✅ Final submission checklist

**Before anything else**

- [ ] Started within a window you can finish in — **5–7 days of active work**
- [ ] If that window will not work, emailed `philipamadasun1@gmail.com` with the
      reason **before** it ran out

**Required**

- [ ] `DESIGN.md`, written before you built, with the "what changed" section added after
- [ ] Wireframes for both surfaces, including the matrix sketched on a real 64×32 grid
- [ ] TUI: survives resize, handles too-small, fully usable with `NO_COLOR=1`, `?` help, works at 80×24
- [ ] Matrix: driver interface, delta-time animation, ≥3 easing curves, legible at 3 m
- [ ] **`flash_audit.py` output pasted in `DESIGN.md` and it PASSES**
- [ ] Every state distinguishable **without color** on **both** surfaces
- [ ] One shared token file, genuinely consumed by both
- [ ] `contrast.py --palette` output pasted, and passing
- [ ] Part C write-up, in your own words
- [ ] `run.sh` / `run.ps1` / `make run`
- [ ] **Your email address in your README**
- [ ] Video: both surfaces at 1×, live resize, live `NO_COLOR`, E-STOP on the matrix, and the 3-metre walk-back

**Optional**

- [ ] Gamma correction · colorblind simulation · reduced motion · contrast in CI · longest-string test
- [ ] Custom pixel font · latency p50/p99 · cross-language surface · sonification
- [ ] Usability test with two humans · real hardware · live-reloading tokens · compositor

---

## 🧭 A closing note

If you find yourself stuck on *what to show* rather than *how to show it*, you
are in exactly the right place — that is the actual problem, and it is why this
challenge exists. Go back to Part 0, pick your one 300-millisecond thing, and
let everything else be secondary to it.

Watch the clock against [the 5–7 day window](#-time-commitment--5-to-7-days).
Finished and scoped beats ambitious and unfinished, every time — and if the
window genuinely does not work for you, email before it closes rather than
after.
