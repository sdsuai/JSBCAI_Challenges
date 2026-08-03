# Problem Set 2 — TBD

Placeholder. The second applicant problem set for the JSBCAI / Robotics Lab.

Sibling repo: `../UX_Design_Challenge` — *One System, Three Surfaces*, an
interface and interaction design challenge (TUI + GUI + LED matrix).

## Conventions carried over from the other problem sets

These are shared across the lab's applicant challenges; keep them consistent
unless there is a reason not to.

* **Language policy** — Python and/or C++. C++ is stated as preferred (the
  lab's rendering and hardware work is C++) but carries **no rubric weight**;
  a Python submission is graded identically. Ship every starter in both
  languages so neither choice is disadvantaged.
* **Hardware** — assume the candidate owns nothing beyond a personal laptop.
  No GPU, no dev boards, no panels, no paid accounts. Anything requiring
  hardware is extra credit only.
* **Platforms** — must run on macOS, Linux, and Windows (incl. WSL). Prefer
  standard-library-only starters so there is no dependency story; where a
  platform needs a one-line fix (`python3-tk`, `windows-curses`,
  `libncurses-dev`), state it in a support table rather than leaving the
  candidate to discover it. Ship a `--demo probe` style capability check so
  they can confirm their terminal in ten seconds.
* **Difficulty** — completable by a sophomore.
* **Time box — 5 to 7 days of active work**, stated prominently near the top
  with the rationale, not buried. The rationale is deliberate and should be
  carried over verbatim in spirit: volunteering here means taking real time out
  of weeknights and weekends, consistently, and an applicant who can carve out
  that time for the challenge can carve it out for lab work. The window exists
  to filter out people who would engage once every fortnight — stated as a
  matter of *fit*, not of worth, since being over-committed elsewhere is
  legitimate but incompatible with the lab's pace. Applicants who cannot make
  the window must email `philipamadasun1@gmail.com` **before** it expires with
  an explanation; extensions are granted at his discretion, and asking is
  explicitly never held against them. Pair this with advice to cut scope and
  document what was cut, so the time box tests scoping judgment rather than
  just speed.
* **Structure** — tiered parts, each required part stating its requirements as
  a numbered list, plus Tier 1 (laptop-friendly) and Tier 2 (harder) extra
  credit with explicit point values.
* **`examples/`** — minimal, runnable starters that show the *mechanics* of a
  requirement without solving it, plus an index README mapping each file to the
  requirement it supports.
* **Submission** — PR to the public repo for identification, real work in a
  private clone, invite `philipamadasun1@gmail.com`, candidate's email in their
  README, and a screen-recorded walkthrough run from a terminal.
* **A rubric with explicit point values**, and a short "how we actually read a
  submission" section naming the two or three things that outweigh the rest.

## Ideas not yet used by the other two sets

Left here as a starting point, to be replaced once the topic is chosen.

* Real-time systems / scheduling and jitter under load
* Computer vision on CPU (calibration, tracking, pose estimation)
* Embedded-flavoured C++: fixed-point maths, no allocation in the hot loop,
  interrupt-safe data structures
* Data structures and algorithms under a hard memory budget
* Concurrency: lock-free queues, producer/consumer, measuring contention
* Sensor fusion and filtering (complementary, Kalman) on replayed data
* Build systems, cross-compilation, and reproducible toolchains
