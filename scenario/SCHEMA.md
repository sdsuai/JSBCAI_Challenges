# The canonical timelines

Two files. **`scenario.jsonl`** is the one you design against.
**`scenario-b.jsonl`** is the hold-out (Grade 3 only) — see the bottom of
this page. The schema below applies to both.

## `scenario.jsonl`

531 ticks at **5 Hz**, covering **106 seconds**. One JSON object per line, flat,
no nesting, no arrays. Both `examples/python/scenario_player.py` and
`examples/cpp/scenario.hpp` read it; the C++ side parses it with ~40 lines and
no JSON library, which is why the format is flat.

**Every candidate is graded against this file.** All three of your surfaces
replay it, and your video shows all three doing so. This is what makes
submissions comparable to each other — and it means you cannot quietly avoid
the states that are hard to design for.

## Fields

| field | type | values | notes |
| --- | --- | --- | --- |
| `t` | number | 0.0 – 106.0 | seconds since start, monotonic, 0.2 steps |
| `state` | string | `BOOT` `IDLE` `MISSION` `ESTOP` `RECOVER` `RETURN` `SHUTDOWN` | the mission state machine |
| `battery_pct` | number | 97.8 → 4.1 | monotonically decreasing |
| `x`, `y` | number | metres | position in the dock frame |
| `heading` | number | 0 – 359.9 | degrees |
| `speed` | number | 0.0 – 0.5 | m/s |
| `lidar` | string | `ok` `degraded` `down` | |
| `imu` | string | `ok` `down` | |
| `comms` | string | `ok` `lost` `down` | `lost` = link dropped mid-mission; `down` = not yet up / powered off |
| `task` | string | free text, may be `""` | |
| `task_idx` | int | 0 – 4 | |
| `task_total` | int | 0 or 4 | |
| `estop` | int | 0 or 1 | 1 = emergency stop engaged |
| `note` | string | usually `""` | a discrete EVENT, present on ~18 of the 531 ticks |

## State vs events — the distinction that matters

Every field except `note` is **state**: what is true right now. `note` is an
**event**: something that just happened, on exactly one tick.

They drive different parts of a UI. State drives the layout — the numbers, the
bars, the colors. Events drive the log and the transitions — the thing that
slides in, the row that appears. A design that conflates them either misses
transient faults or re-animates things that did not change.

Both players hand you these separately (`poll()` and `drain_notes()`), and
`poll()` walks every intervening tick so an event is never skipped even if your
frame rate drops below 5 Hz.

## What we did NOT give you

There is no `alarm` field, no `severity`, no `priority`. That is deliberate.

Deciding what counts as an alarm, how to rank two of them that fire at once,
what the operator sees first, and what is allowed to be quiet — that **is** the
design work being assessed. If we handed you a severity number you would render
it and we would learn nothing about you.

## The timeline

```
   t=0.0    BOOT      power on — all three sensors down
   t=1.4    BOOT      comms up
   t=2.8    BOOT      imu up
   t=4.2    BOOT      lidar up
   t=6.0    IDLE      self-test passed
   t=14.0   MISSION   mission start, task 1/4
   t=26.0   MISSION   comms LOST                    <-- transient fault
   t=29.6   MISSION   comms restored (3.6s outage)
   t=46.0   MISSION   battery crosses 20%           <-- degraded, still running
   t=52.0   MISSION   lidar degraded                <-- second fault begins
   t=55.0   MISSION   lidar DOWN                    <-- two faults at once
   t=58.0   ESTOP     EMERGENCY STOP                <-- irreversible action
   t=70.0   ESTOP     lidar recovered
   t=72.0   RECOVER   e-stop cleared, self-check
   t=80.0   RETURN    returning to dock
   t=85.0   RETURN    battery crosses 8%            <-- second severity tier
   t=98.0   SHUTDOWN  docked
   t=104.0  SHUTDOWN  link down
   t=106.0            end
```

### The five moments your design is judged on

1. **t=0–6, boot.** Three sensors are down and that is *fine* — it is normal
   startup, not a fault. Does your UI scream? An operator who is trained to
   ignore the boot alarms will ignore the real one at t=55.

2. **t=26, the 3.6-second comms dropout.** A transient. Does it register at all?
   Does it still shout thirty seconds later? Crying wolf and missing it entirely
   are both failures, and the gap between them is the whole craft.

3. **t=52–58, two faults at once.** Battery is under 20% *and* lidar is dying.
   Your layout has to show both without either hiding the other, and something
   has to be visibly more important. Which one, and how did you decide?

4. **t=58, E-STOP.** The one irreversible thing in the timeline. It must be
   unmistakable and unmissable on all three surfaces — including the 64×32 one
   that has no room for the words "emergency stop".

5. **t=85, battery critical.** A *second* severity tier on a channel that was
   already warning. If low and critical look the same, the tier is decorative.

## Timing is compressed

Battery drain and mission progress are far faster than real hardware so the
whole arc plays in under two minutes. That is a demo-pacing decision, not a
physics claim. Both players take a speed multiplier
(`--speed 4`, `ScenarioPlayer(path, 4.0)`) — useful while developing, but your
**video must show it at 1×**.

---

# `scenario-b.jsonl` — the hold-out *(Grade 3)*

392 ticks, 100 seconds, same schema. **You do not get to design for this one.**

Your surfaces must handle it without special-casing. A design that was
*designed* handles it; a design that was *tuned to scenario A* falls over
visibly, and that is exactly what this file is for.

```
   t=0.0    BOOT      power on
   t=4.0    IDLE
   t=10.0   MISSION   3 tasks, faster than scenario A
   t=18.0   MISSION   lidar degraded — early, and it never recovers
   t=24.0   MISSION   IMU DOWN                      <-- a fault A never has
   t=30.0   MISSION   battery crosses 20%
   t=40.0   MISSION   "telemetry link degrading"    <-- LAST TICK BEFORE THE GAP
   ......   ........  NO DATA AT ALL FOR 21.6 s     <-- the feed is simply dead
   t=62.0   ESTOP     "telemetry restored"          <-- it e-stopped while you
                                                        were blind, and lost
                                                        half its battery
   t=70.0   RECOVER   e-stop cleared remotely
   t=76.0   RETURN    attempting return
   t=84.0   RETURN    battery critical
   t=90.0   RETURN    comms lost
   t=96.0   STRANDED  <-- a state value that is NOT in scenario A
   end      no clean shutdown. It just stops, at 2.2%, stranded.
```

## The three things it tests

### 1. Stale data — the important one

There are **no ticks at all** between t=40.2 and t=61.8.

`poll()` returns the most recent tick at or before now, so throughout the gap it
keeps handing you the t=40 sample. Nothing errors. Nothing warns you. Your UI
will cheerfully display a 21-second-old battery reading, a 21-second-old
position, and the word `MISSION` — while the actual robot has stopped, dumped
half its remaining charge, and entered an emergency stop.

On a real robot this is how an operator makes a confident decision about a
machine that is no longer there.

**A display that cannot distinguish "this is true now" from "this was true 21
seconds ago" is lying, and the more polished it looks the more convincingly it
lies.** Detecting it is trivial:

```python
tick = player.poll()
age  = player.scenario_time - tick["t"]      # Python
```
```cpp
const lm::Tick& tk = player.poll();
double age = player.scenario_time() - tk.t;  // C++
```

What you *do* with that number is the design question, and it is different on
each surface. On a 64×32 panel with no text, how do you say "I have stopped
knowing"? Do you freeze, grey out, blink, or show something else entirely? Is
stale data worse than no data?

### 2. An unknown state value

`STRANDED` appears at t=96 and appears nowhere in scenario A. Real systems grow
new enum values and old displays have to survive them.

Your UI must not crash, must not render blank, and must not silently show the
previous state as though nothing happened. It does not need to look *good* — it
needs to be **honestly unhelpful**: something a viewer reads as "the system is
in a state this display does not know about", which is far safer than confident
nonsense.

### 3. Faults that never recover

Scenario A resolves everything. Here the lidar degrades at t=18 and stays
degraded, the IMU dies at t=24 and never returns, and the mission never
completes. If your severity model assumes faults are transient — if a warning
banner auto-dismisses, or an alert animation only plays once — this is where
that assumption shows.

## Making your own

`examples/python/make_scenario.py` produced this file and documents the event
table and battery model. Author extra timelines for testing if you like —
edge cases, longer runs, faults we did not include. Submitting against a
different timeline instead of this one, however, does not count.
