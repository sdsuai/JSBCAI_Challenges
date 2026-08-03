# DESIGN.md — fill this in BEFORE you write code

Copy this file to the root of your submission as `DESIGN.md` and answer every
section. Part 0 is graded on this document alone.

Two rules:

- **Commit to answers.** "It depends" and "both are valid" score zero. We are
  hiring for judgment, and judgment means choosing and being able to say why.
- **Write it first.** Then build. Then, at the end, add the *What changed*
  section honestly. Discovering your plan was wrong and saying so is worth more
  than a document retro-fitted to whatever you ended up shipping — and it is
  obvious to us which one we are reading.

Aim for 500–1000 words plus sketches. Longer is not better.

---

## 1. Who is looking at this?

One paragraph per surface. Be specific and physical, not aspirational.

For each: **who** is looking, from **how far**, for **how long**, **how often**,
in what **lighting**, and **what else are they doing** at the time. "A user who
wants to monitor the robot" is not an answer. "The operator, 60 cm away, glancing
for 2 seconds every 30 seconds while walking alongside the rover, outdoors in
daylight, holding a controller in both hands" is.

- **TUI:**
- **GUI:**
- **LED matrix:**

## 2. The 300-millisecond question

For each surface: **what is the ONE thing** a viewer must be able to read in
300 ms — before they have focused, before they have read a single word?

Name one thing per surface. Not two. If your answer is a list, you have not
made the decision yet, and the design will show it.

- **TUI:**
- **GUI:**
- **LED matrix:**

Then: **what did you sacrifice to make that thing primary?** Something got
smaller, dimmer, or moved. Name it. A hierarchy where nothing lost is not a
hierarchy.

## 3. Wireframes

One per surface, before code. Photos of paper sketches are ideal and preferred
over anything polished — we want to see thinking, not tooling.

Annotate each with what goes where and *why*. Include your LED matrix sketch on
a **64×32 grid** (graph paper, or a spreadsheet with square cells). Sketching
the matrix at real resolution is the single fastest way to discover that your
idea does not fit, and it is much cheaper than discovering it in code.

<!-- ![TUI wireframe](docs/wireframe-tui.jpg) -->

## 4. Severity model

The scenario gives you raw state and no severity ranking. Define yours.

| condition | severity | how it is shown (TUI) | (GUI) | (matrix) |
| --- | --- | --- | --- | --- |
| | | | | |

Then answer:

- **At t=52–58 the battery is under 20% AND the lidar is dying. Which wins, and
  why?** What does the loser look like while the winner has priority?
- **Boot (t=0–6) has three sensors down. Is that an alarm?** Justify either way.
- **The comms dropout at t=26 lasts 3.6 seconds.** What does the operator see —
  during, and thirty seconds after? What is your rule for how long a resolved
  fault stays visible, and what happens if it flaps?

## 5. Design tokens

Where your shared token file lives, and what is in it. Colors, timings, spacing,
severity names. All three surfaces must consume it.

- **File:**
- **How each surface consumes it:**
- **Contrast check output** (paste it — `python3 contrast.py --palette ...`):

For each semantic color, what carries the same meaning **without** color —
shape, position, motion, or text?

| token | color | non-color encoding |
| --- | --- | --- |
| | | |

## 6. Motion

- **Which easing curve for which transition, and why that one?**
- **What does *not* animate, and why?** (This is the harder half. Everything
  moving is the same as nothing moving.)
- **Longest animation in your system, in ms:** — justify it. Anything over
  ~400 ms on a status change is a decision you have to defend.

## 7. The E-STOP question

Does your GUI's E-STOP button ask for confirmation before firing?

Answer yes or no, and defend it in a short paragraph. Consider: what does the
operator's hand do in the half-second before they hit it; what is the cost of
firing it by accident; what is the cost of a dialog when it was *not* an
accident; and whether "are you sure?" is a real safeguard or a reflex click.

There is a defensible answer either way. There is no defensible non-answer.

## 8. Flash safety

Paste your `flash_audit.py` output for the matrix's most active state.

If any state started above 3 Hz, say what it was and what you changed. If none
did, say what you did to keep it that way — designing under the constraint
rather than getting lucky.

## 9. What changed

Written **after** you built it. Where did the plan meet reality and lose?

- Something you were sure about that turned out wrong when you saw it running:
- Something you cut, and what it cost:
- The surface that was hardest, and why:
- What you would do differently with another week:

Honesty scores here. Every real design changes on contact with the screen; a
DESIGN.md that predicted everything perfectly reads as one written afterwards.
