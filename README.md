# 🎛 One System, Three Surfaces — UX & Interface Design Challenge · Grade 3

**JSBCAI / Robotics Lab — Interface & Interaction Design Task · Grade 3**

> This is the **Grade 3** variant — the hardest. Same three surfaces as Grade 2,
> plus a **second, hold-out scenario you do not get to design for**, and a
> **usability test with two real humans** which is required rather than extra
> credit. Grades 1 and 2 are lighter. If you were sent here directly, this is
> the one to do — do not go looking for the other branches.

This challenge evaluates your ability to **design an interface**, not just build
one. Specifically:

* Information hierarchy under hard constraints
* TUI design (terminal, keyboard-only)
* GUI design (desktop, mouse + keyboard)
* LED matrix animation design (64×32 RGB, no text, viewed from across a room)
* Animation timing, easing, and gamma
* Accessibility and failure states
* Cross-surface consistency via shared design tokens
* Designing for data you have not seen, and for data that has stopped arriving
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
  Part C). If you *do* own a panel, that is extra credit — never a requirement.
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

If you are running out of time, **ship three finished surfaces that each do one
thing well** rather than three half-built ones attempting everything. Say what
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
| `gui_minimal.py` (tkinter) | ✅ | ⚠️ `sudo apt install python3-tk` | ✅ |
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

You will build **one robot status-and-control console, three times**:

| Part | Surface | Constraint that makes it interesting |
| ---- | ------- | ------------------------------------ |
| **Part 0** | Design intent + wireframes | Decide before you build |
| **Part A** | **TUI** — terminal, keyboard-only | Monospace cells, resizes under you, may have no color at all |
| **Part B** | **GUI** — desktop window | Mouse *and* keyboard, must never freeze, needs real interaction states |
| **Part C** | **LED matrix** — 64×32 RGB | 2048 pixels. No text. Viewed from 3 metres. Physically linear light |
| **Part D** | Write-up and video | Defend it |

All three read **the same canonical timeline** — `scenario/scenario.jsonl`, a
106-second replay of a rover's mission that includes a transient fault, two
simultaneous faults, an emergency stop, and a recovery. Every candidate is
graded on the same events, so submissions are directly comparable.

### And a second one you do not get to design for

`scenario/scenario-b.jsonl` is the **hold-out**. Same schema, different mission,
and deliberately nastier. Your surfaces must handle it **without
special-casing**, and your video must show them doing so.

It contains three things scenario A never does:

1. **The feed stops.** No ticks at all for 21.6 seconds. `poll()` keeps
   returning the last sample it saw, nothing errors, and your UI will
   confidently display a 21-second-old battery reading — while the real robot
   has stopped, lost half its remaining charge, and gone into emergency stop.
   **A display that cannot tell "true now" from "true 21 seconds ago" is lying,
   and the more polished it looks the more convincingly it lies.**
2. **An unknown state.** `STRANDED` appears at t=96 and exists nowhere in
   scenario A. Do not crash, do not render blank, and do not show the previous
   state as if nothing happened.
3. **Faults that never recover.** The IMU dies at t=24 and stays dead. If your
   severity model assumes faults are transient, this is where that shows.

Read [`scenario/SCHEMA.md`](scenario/SCHEMA.md) for the full breakdown. The
point of a hold-out is simple: it separates a design that was *designed* from
one that was *tuned to a demo*.

### Why three surfaces

Because the interesting part is the **translation**.

Anybody can put fifteen numbers on a screen. The skill we are hiring for shows
up when the screen is 64×32 pixels, has no room for text, and is being looked at
from across a lab by someone holding a controller — and you have to decide what
survives.

A candidate who shrinks their GUI onto the matrix fails visibly. A candidate who
re-encodes the state into color, shape, and motion — and can explain why they
dropped the other twelve numbers — is who we are looking for.

> **The single most common way to fail this challenge is to show everything.**
> Three surfaces that all display the same twelve fields at different sizes is
> not three designs. It is one design, rendered three times, and it means the
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

# 2. The four demos. Run all of them — they ARE the brief for Part C.
python3 matrix_sim.py --demo sweep     #   ./demo sweep
python3 matrix_sim.py --demo gamma     #   ./demo gamma     <-- especially this
python3 matrix_sim.py --demo easing    #   ./demo easing
python3 matrix_sim.py --demo alarm     #   ./demo alarm

# 3. The timelines — the second one is the hold-out
python3 scenario_player.py --list      #   ./demo scenario
python3 scenario_player.py --list --file ../../scenario/scenario-b.jsonl
```

Then read [`scenario/SCHEMA.md`](scenario/SCHEMA.md) and
[`examples/README.md`](examples/README.md).

---

## 🎯 Deliverables

1. **A GitHub repository** containing:
   * Source for all three surfaces
   * A **shared design-token file** consumed by all three
   * `DESIGN.md` (Part 0 — start from [`templates/DESIGN.md`](templates/DESIGN.md))
   * `README.md` with setup + run instructions **and your email address**
   * `run.sh` / `run.ps1` / `make run` that launches each surface

2. **A 6–12 minute walkthrough video** (screen recording with your voice):
   * Run all three surfaces from a terminal, replaying **scenario A at 1× speed**
   * Then run **scenario B** on at least the TUI and the matrix, and show what
     each does during the 21-second stall and at `STRANDED`
   * **Resize your terminal while the TUI is running**, live
   * **Run the TUI with `NO_COLOR=1`**, live
   * **Tab through your GUI using only the keyboard** — no mouse — and show focus moving
   * Show the matrix during the **E-STOP at t=58** and during **two-faults-at-once at t=55**
   * Show your `--panel led` gamma before/after
   * Walk 3 metres back from the screen with the matrix running, on camera
   * For each surface, say **what you chose to leave out, and why**
   * Show a clip or summary of your **usability test**, including the change you
     made because of it
   * Demonstrate any extra credit you did

3. **A usability test report** — `USABILITY.md`, from
   [`templates/USABILITY.md`](templates/USABILITY.md). See Part D.

4. **A write-up** (in your README or `WRITEUP.md`) answering the Part E questions.

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
8. **Handles stale and unknown data.** Run it against `scenario-b.jsonl`. When
   the feed stalls, the operator must be able to tell that what they are seeing
   is old — and when `STRANDED` arrives, the display must not break or silently
   show the previous state.

Starter mechanics for all of this: `examples/python/tui_minimal.py`,
`examples/cpp/tui_minimal.cpp`. They are deliberately ugly — they solve the
plumbing so you can spend your time on the design.

---

## 🖱 Part B — The GUI *(required)*

A desktop window. Same data, same semantics, different medium.

### Requirements

1. **Never freezes.** Scenario replay runs off the UI thread; the UI thread only
   renders. A window that stops repainting is the single most common way a
   student GUI reads as broken. Any operation over ~200 ms must show progress.
2. **Five states on every interactive control**: default, hover, focus
   (keyboard), active (pressed), disabled. Focus must be **visually distinct
   from hover** — a keyboard user has to see where they are.
3. **Fully keyboard-navigable.** Tab order is sensible, Enter/Space activate,
   and nothing is reachable by mouse only. *You will demonstrate this in the
   video with your hands off the mouse.*
4. **Disabled means disabled.** A greyed-out control that still fires is worse
   than one that was never greyed out.
5. **A spacing and type scale.** Every gap is a multiple of one step; you have
   two or three type sizes, not nine. When we ask "why is that gap 13 pixels?"
   the answer must not be "it looked right".
6. **Resizes sensibly.** Define a minimum size. Decide what stretches and what
   stays fixed, and make that a deliberate choice you can name.
7. **An E-STOP control.** Whether it confirms first is **your call** — see
   Part E. Whatever you choose, the video must show it and you must defend it.
8. **Handles stale and unknown data**, as in Part A. On a GUI you have room to
   be explicit about it; use it.

Starter mechanics: `examples/python/gui_minimal.py` (tkinter, stdlib, nothing to
install on Windows/macOS). Qt, Dear ImGui, Dear PyGui, FLTK, raylib, and friends
are all equally welcome — several are nicer.

---

## 💡 Part C — The LED matrix *(required — the heart of the challenge)*

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
4. **Gamma correction — and prove it.** PWM duty cycle is linear in *photons*;
   your eye is not. A linear ramp written straight to a panel rushes to bright
   in the first third and then barely changes. Run `--demo gamma` to see it, then
   run **your own** fade under `panel="led"` and show the before/after in your
   video. Build a LUT once; do not call `pow()` per pixel per frame.
5. **No color-only encoding.** Assume your viewer is colorblind, or that the
   panel's reds have drifted. Every state must also differ in **shape or
   motion**. A greyscale screenshot of your matrix must still be readable.
6. **Flash safety — this is a hard requirement, not a style note.** **No
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
7. **The E-STOP must be unmistakable at 3 metres**, with no text available.
8. **Two simultaneous faults (t=52–58) must both be visible**, with one clearly
   dominant.
9. **Stale data must be unmistakable at 3 metres.** This is the hardest single
   requirement in the challenge. You have 2048 pixels, no text, and you must
   communicate "I have stopped knowing" — which is a different message from
   "everything is fine" and from "something is wrong". Freezing the display is
   the one thing you certainly must not do, because a frozen display of good
   news is indistinguishable from good news.
10. **`STRANDED` must render as something**, and that something must not be
    mistakable for a state you designed for.

### The test that matters

Stand up. Walk three metres from your screen. Squint.

If you cannot tell `NOMINAL` from `DEGRADED` from `FAULT` in under a second,
the design is not finished — regardless of how good it looks at your desk.
`--demo alarm` shows the bar you are clearing.

---

## 🔗 Cross-cutting requirement — one design system *(required)*

All three surfaces must consume **one shared design-token file** (JSON, YAML,
a header, a module — your choice). It holds semantic names, not scattered
literals: `fault`, not `#e04b45` typed in eleven places.

Changing `fault` in that one file must change all three surfaces. That is the
test of whether you built a system or three lookalike programs.

Check your palette before you ship:

```bash
python3 examples/python/contrast.py --palette your_tokens.json
```

Every foreground must clear **3.0:1** against every surface it can land on, and
body text should clear **4.5:1**. See `examples/tokens.example.json` for the
shape (it is an example, not a palette to copy — yours should differ and you
should be able to say why).

The three surfaces will not *look* the same — a terminal cell, a desktop widget,
and an LED pixel are different media and pretending otherwise is its own
mistake. But a viewer moving between them should never have to relearn what red
means, what pulsing means, or which corner the important thing lives in.

---

## 👥 Part D — Usability test *(required at this grade)*

Extra credit in Grades 1 and 2. Required here, and weighted accordingly.

**Two people who have never seen your design.** Twenty minutes each. Give them
tasks, watch, and change something because of what you saw.

Use [`templates/USABILITY.md`](templates/USABILITY.md) and submit it as
`USABILITY.md`.

### The rules that make it worth doing

1. **Do not explain your design.** Not one sentence. The moment you say "the bar
   on the left is battery", the test is over and you have learned nothing.
2. **Do not help when they get stuck.** Say "what do you think you'd do?" and
   stay quiet. The silence is uncomfortable and it is where the data is.
3. **Do not defend.** Write down what they say. Arguing produces a participant
   who stops telling you things.
4. **Watch what they do, not what they say.** People are polite. The signal is
   where their eyes go, how long they take, and what they get wrong.

### Required

* Both participants, the same tasks, in the same order, at 1× speed
* **Time to correct answer** per task, or "never"
* A section on **what they got wrong** — and for each mistake, what in your
  design made that mistake reasonable. The answer is never "they weren't paying
  attention"; they were reading your design and it told them something you did
  not intend
* Verbatim quotes, **including the unflattering ones**
* **At least one real change made because of what you saw**, with before/after

> A report concluding "the test confirmed my design works" scores near zero —
> not because the design is bad, but because a test that changed nothing was a
> demonstration, not a test. Everyone's design confuses a stranger somewhere.
> Finding where is the entire point, and it is the cheapest design win
> available to you.

---

## ✍️ Part E — Write-up *(required)*

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

4. **Stale data.** What does each surface do during scenario B's 21-second
   stall, and why did you choose that? What is the *worst* thing a status
   display can do when its data stops arriving, and why?

5. **The unknown state.** How does each surface render `STRANDED`? What is your
   general rule for values you did not anticipate?

6. **The usability test.** What surprised you most, and what did you change?

7. **The E-STOP.** Does your GUI confirm before firing? Argue your side.
   Consider what the operator's hand is doing in the half-second before they hit
   it, the cost of firing it by accident, the cost of a dialog when it was *not*
   an accident, and whether "are you sure?" is a real safeguard or a reflex
   click. There is a defensible answer either way; there is no defensible
   non-answer.

8. **Boot is not a fault.** At t=0–6 all three sensors read down. That is normal
   startup. How did you keep your UI from crying wolf — and why does that matter
   for whether the operator believes you at t=55?

9. **Gamma.** Explain in your own words why a linear PWM ramp looks wrong on a
   panel but a linear sRGB ramp looks fine on your monitor. What would break if
   you applied your gamma LUT twice?

10. **What you would do with another week.**

---

## 🛠 Extra Credit *(optional — pick what interests you)*

### 🟦 Tier 1 — laptop-friendly

| | Points | |
| --- | --- | --- |
| **Adversarial scenario** | +8 | Author a third timeline specifically designed to break *your own* design. Show it breaking on video, then fix it. Finding nothing that breaks it means you have not tried hard enough. |
| **Colorblind simulation** | +8 | Add a mode that filters your own UI through deuteranopia/protanopia/tritanopia simulation. **Then fix what it breaks** and show the before/after. Finding nothing to fix means you are not looking hard enough. |
| **Reduced motion** | +6 | A `--reduce-motion` flag that keeps every state distinguishable with animation off. Vestibular disorders are real, and it is a good test of whether motion was carrying meaning or decoration. |
| **Contrast in CI** | +5 | Wire `contrast.py --palette` into a pre-commit hook or GitHub Action so a failing palette breaks the build. |
| **Longest-string test** | +6 | Run every label through a pseudo-locale that inflates string length ~40% (German-style). Nothing may clip, overlap, or reflow into nonsense. |
| **Custom pixel font** | +10 | Design your own 3×5 or 4×6 font for the matrix. Include a legibility test at 3 m and say which glyph pairs you had to redesign (`8`/`B`, `5`/`S`, `0`/`O`, `1`/`I`). |
| **Latency instrumentation** | +8 | Measure input → visible-pixel latency in the TUI and GUI. Report p50 and p99, not a mean. Say which is worse and why. |
| **Cross-language surface** | +10 | Implement one surface in the *other* language against the same token file, matching semantics. |
| **Sonification** | +6 | Design audio cues for state changes. Distinguishable without looking, non-annoying at ten repetitions, and silenceable. |

### 🟧 Tier 2 — harder

| | Points | |
| --- | --- | --- |
| **Fleet view** | +15 | Three robots on the one 64×32 panel instead of one. You cannot show three of anything at that size, so decide what survives — and defend it. The hardest pure information-design problem available here. |
| **Real hardware** | +12 | If you own a matrix (HUB75, WS2812, Adafruit, Pimoroni, Pi, ESP32, Arduino), implement the driver backend and film it running. **Your simulator backend must still work** — we have to run your submission without your hardware. |
| **Live-reloading tokens** | +8 | Edit the token file and watch all three surfaces update without restarting. Demo it on camera. |
| **Matrix compositor** | +10 | Layers with alpha, z-order, and independent transitions, instead of drawing straight to the framebuffer. Show a layer fading over another. |

---

## 🧨 Grading Rubric

| Category | Points | What we are looking at |
| --- | --- | --- |
| **Part 0** — Design intent, wireframes, severity model | 15 | Specific viewer model; a real hierarchy decision; honest "what changed" |
| **Part A** — TUI | 20 | Resize, too-small, `NO_COLOR`, non-blocking, discoverability, 80×24 |
| **Part B** — GUI | 20 | Five interaction states, keyboard-complete, never freezes, real spacing scale |
| **Part C** — LED matrix | 30 | Legible at 3 m; driver interface; delta-time animation; easing; gamma proven; **flash audit passes**; no color-only encoding |
| **Cross-surface design system** | 10 | One token file, actually shared; contrast check passes; consistent semantics |
| **Generality** — the hold-out scenario | 20 | Stale data made visible on all three surfaces; `STRANDED` handled; no special-casing |
| **Part D** — Usability test | 20 | Real strangers, honest failures, a change made and shown |
| **Part E** — Write-up | 10 | Concrete, in your own words, commits to answers |
| **Video walkthrough** | 15 | Required demos performed live; explains *what was left out and why* |
| | **160** | |
| **Extra credit Tier 1** | +20 max | |
| **Extra credit Tier 2** | +20 max | |
| | **200 max** | |

### How we actually read a submission

Three things carry more weight than anything else, and none of them is code
quality:

1. **Did you leave things out?** Three surfaces showing the same twelve fields
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

At this grade we also read **`USABILITY.md` first**, before we look at the
design itself. A test where nothing went wrong is treated as a test that was not
really run.

**Automatic point losses** — every one of these is a two-minute check we run
before anything else:

* Matrix flash audit fails (3–60 Hz full-field) — Part C capped at half marks
* Any state distinguishable only by color, on any surface
* TUI corrupts on resize, or is unusable under `NO_COLOR=1`
* GUI freezes during any operation, or has mouse-only controls
* No shared token file, or one that exists but is not actually consumed by all three
* Video does not show all three surfaces replaying the scenario at 1×
* Any surface that special-cases scenario B instead of handling it generally
* A display that shows stale data as though it were live
* `USABILITY.md` missing, or reporting that nothing needed changing

---

## 🗂 What's in this repo

```
README.md                     this file
scenario/
  scenario.jsonl              the canonical timeline — 531 ticks, 5 Hz, 106 s
  scenario-b.jsonl            the HOLD-OUT — 392 ticks, a 21.6 s feed stall
  SCHEMA.md                   field reference, both timelines, what each tests
templates/
  DESIGN.md                   Part 0 skeleton — copy this to your repo root
  USABILITY.md                Part D skeleton — the usability test report
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
    gui_minimal.py            GUI mechanics: worker thread, 5 states, spacing scale
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
- [ ] Wireframes for all three surfaces, including the matrix sketched on a real 64×32 grid
- [ ] TUI: survives resize, handles too-small, fully usable with `NO_COLOR=1`, `?` help, works at 80×24
- [ ] GUI: five interaction states, fully keyboard-navigable, never freezes, spacing scale
- [ ] Matrix: driver interface, delta-time animation, ≥3 easing curves, gamma proven, legible at 3 m
- [ ] **`flash_audit.py` output pasted in `DESIGN.md` and it PASSES**
- [ ] Every state distinguishable **without color** on **all three** surfaces
- [ ] One shared token file, genuinely consumed by all three
- [ ] `contrast.py --palette` output pasted, and passing
- [ ] Both surfaces handle `scenario-b.jsonl` — stale data visible, `STRANDED` safe
- [ ] `USABILITY.md` — two strangers, timed tasks, and a change you actually made
- [ ] Part E write-up, in your own words
- [ ] `run.sh` / `run.ps1` / `make run`
- [ ] **Your email address in your README**
- [ ] Video: all three surfaces at 1×, live resize, live `NO_COLOR`, keyboard-only GUI pass, E-STOP on the matrix, gamma before/after, the 3-metre walk-back, **scenario B's stall**, and your usability change

**Optional**

- [ ] Colorblind simulation · reduced motion · contrast in CI · longest-string test
- [ ] Custom pixel font · latency p50/p99 · cross-language surface · sonification
- [ ] Adversarial scenario · fleet view · real hardware · live-reloading tokens · compositor

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
