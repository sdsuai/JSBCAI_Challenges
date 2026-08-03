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
* **Difficulty** — completable by a sophomore in a focused week.
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
