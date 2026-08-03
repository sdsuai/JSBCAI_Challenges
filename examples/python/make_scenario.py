"""
make_scenario.py — generates the canonical timelines in scenario/.

You do NOT need to run this. Both timelines are already committed. This
generator is here so you can read exactly how they were produced, and so you
can author timelines of your own for testing.

    python make_scenario.py --variant a --out ../../scenario/scenario.jsonl
    python make_scenario.py --variant b --out ../../scenario/scenario-b.jsonl

Timelines are deliberately time-compressed: battery drain and mission progress
are far faster than real hardware, so a whole arc plays out in under two
minutes. That is a demo-pacing decision, not a physics claim.

--- Scenario A (scenario.jsonl) -------------------------------------------
The one you design against. 106 s, clean arc, everything recovers.

    t=1.4-4.2   sensors come up one at a time      -> partial/unknown state
    t=26.0      comms drops for 3.5s, then returns -> TRANSIENT fault: does
                                                      your UI cry wolf?
    t=46.0      battery crosses 20%                -> degraded but RUNNING
    t=52.0      lidar degrades, then dies at 55    -> TWO faults at once
    t=58.0      EMERGENCY STOP                     -> irreversible, operator-
                                                      initiated
    t=72.0      e-stop cleared                     -> recovery is a state
    t=85.0      battery crosses 8%                 -> a second severity tier

--- Scenario B (scenario-b.jsonl) — the hold-out --------------------------
Grade 3 only. Deliberately nastier, and designed to break a UI that was tuned
to scenario A rather than designed properly:

    t=24.0      IMU dies mid-mission               -> a fault A never has
    t=40.2-61.8 THE FEED STOPS ENTIRELY            -> no ticks at all for 22s.
                                                      Your UI keeps rendering
                                                      the last value it saw.
                                                      Is it still telling the
                                                      truth?
    (during)    the robot E-STOPS while you are blind, and the battery keeps
                draining. The first tick after the gap shows a machine in a
                state you never saw it enter.
    t=96.0      state becomes STRANDED             -> a value that does NOT
                                                      appear in scenario A.
                                                      Handle the unknown.
    end         no clean shutdown. It just stops, low and stranded.

The stall is the interesting one. `ScenarioPlayer.poll()` returns the most
recent tick at or before now, so during the gap it keeps handing you the t=40
sample forever. Nothing errors. Your UI will happily display a 22-second-old
battery reading as though it were live — which, on a real robot, is how an
operator ends up making a decision on data from a machine that has already
stopped.

Detecting it is your job and it is not hard: compare the tick's `t` against
`player.scenario_time` (Python) / `player.scenario_time()` (C++). What you DO
about it is the design question.
"""

import argparse
import json
import math

DT = 0.2          # 5 Hz
MAX_ACCEL = 0.60  # m/s^2
MAX_TURN = 60.0   # deg/s

# ---------------------------------------------------------------------------
# Scenario A — the canonical timeline. DO NOT EDIT: the committed
# scenario.jsonl must stay byte-identical across all grades.
# ---------------------------------------------------------------------------
EVENTS_A = [
    (0.0,   "note",         "power on"),
    (0.0,   "state",        "BOOT"),
    (1.4,   "comms",        "ok"),
    (1.4,   "note",         "comms link up"),
    (2.8,   "imu",          "ok"),
    (2.8,   "note",         "imu calibrated"),
    (4.2,   "lidar",        "ok"),
    (4.2,   "note",         "lidar spin-up complete"),
    (6.0,   "state",        "IDLE"),
    (6.0,   "note",         "self-test passed, awaiting tasking"),

    (14.0,  "state",        "MISSION"),
    (14.0,  "task_total",   4),
    (14.0,  "task_idx",     1),
    (14.0,  "task",         "survey grid A"),
    (14.0,  "speed_target", 0.45),
    (14.0,  "heading_target", 30.0),
    (14.0,  "note",         "mission start"),
    (20.0,  "heading_target", 95.0),

    (26.0,  "task_idx",     2),
    (26.0,  "task",         "sample at waypoint B"),
    (26.0,  "comms",        "lost"),
    (26.0,  "note",         "comms dropout"),
    (29.5,  "comms",        "ok"),
    (29.5,  "note",         "comms restored"),
    (31.0,  "heading_target", 170.0),
    (31.0,  "speed_target", 0.35),

    (38.0,  "task_idx",     3),
    (38.0,  "task",         "survey grid C"),
    (38.0,  "speed_target", 0.50),
    (38.0,  "heading_target", 250.0),
    (46.0,  "note",         "battery below 20%"),

    (50.0,  "task_idx",     4),
    (50.0,  "task",         "return leg prep"),
    (50.0,  "heading_target", 310.0),
    (50.0,  "speed_target", 0.40),
    (52.0,  "lidar",        "degraded"),
    (52.0,  "note",         "lidar returns intermittent"),
    (55.0,  "lidar",        "down"),
    (55.0,  "note",         "lidar offline - obstacle detection lost"),

    (58.0,  "state",        "ESTOP"),
    (58.0,  "estop",        1),
    (58.0,  "speed_target", 0.0),
    (58.0,  "note",         "EMERGENCY STOP asserted by operator"),

    (70.0,  "lidar",        "ok"),
    (70.0,  "note",         "lidar recovered"),
    (72.0,  "state",        "RECOVER"),
    (72.0,  "estop",        0),
    (72.0,  "note",         "e-stop cleared, running self-check"),

    (80.0,  "state",        "RETURN"),
    (80.0,  "speed_target", 0.50),
    (80.0,  "heading_target", 20.0),
    (80.0,  "task",         "return to dock"),
    (80.0,  "task_idx",     4),
    (80.0,  "note",         "returning to dock"),
    (85.0,  "note",         "battery critical"),

    (98.0,  "state",        "SHUTDOWN"),
    (98.0,  "speed_target", 0.0),
    (98.0,  "note",         "docked, shutting down"),
    (101.0, "lidar",        "down"),
    (102.5, "imu",          "down"),
    (104.0, "comms",        "down"),
    (104.0, "note",         "link down"),
]
DRAIN_A = [(0.0, 0.15), (14.0, 2.60), (38.0, 1.65), (46.0, 0.55),
           (58.0, 0.18), (72.0, 0.22), (80.0, 0.24), (98.0, 0.10)]

# ---------------------------------------------------------------------------
# Scenario B — the hold-out. Grade 3 only.
# ---------------------------------------------------------------------------
EVENTS_B = [
    (0.0,   "note",         "power on"),
    (0.0,   "state",        "BOOT"),
    (0.8,   "comms",        "ok"),
    (1.6,   "imu",          "ok"),
    (2.4,   "lidar",        "ok"),
    (2.4,   "note",         "self-test passed"),
    (4.0,   "state",        "IDLE"),

    (10.0,  "state",        "MISSION"),
    (10.0,  "task_total",   3),
    (10.0,  "task_idx",     1),
    (10.0,  "task",         "transect north"),
    (10.0,  "speed_target", 0.50),
    (10.0,  "heading_target", 10.0),
    (10.0,  "note",         "mission start"),

    (18.0,  "lidar",        "degraded"),
    (18.0,  "note",         "lidar returns intermittent"),
    (24.0,  "imu",          "down"),
    (24.0,  "note",         "imu offline - dead reckoning only"),
    (24.0,  "speed_target", 0.30),
    (26.0,  "task_idx",     2),
    (26.0,  "task",         "sample at rock field"),
    (30.0,  "note",         "battery below 20%"),
    (36.0,  "heading_target", 120.0),
    (40.0,  "note",         "telemetry link degrading"),

    # --- everything below happens DURING the blackout, unobserved ---------
    (48.0,  "state",        "ESTOP"),
    (48.0,  "estop",        1),
    (48.0,  "speed_target", 0.0),
    (50.0,  "lidar",        "down"),
    # ----------------------------------------------------------------------

    (62.0,  "note",         "telemetry restored"),
    (70.0,  "state",        "RECOVER"),
    (70.0,  "estop",        0),
    (70.0,  "note",         "e-stop cleared remotely"),

    (76.0,  "state",        "RETURN"),
    (76.0,  "speed_target", 0.35),
    (76.0,  "heading_target", 200.0),
    (76.0,  "task",         "return to dock"),
    (76.0,  "note",         "attempting return"),
    (84.0,  "note",         "battery critical"),
    (90.0,  "comms",        "lost"),
    (90.0,  "note",         "comms lost"),
    (94.0,  "speed_target", 0.0),
    (94.0,  "note",         "motion halted - insufficient power"),
    (96.0,  "state",        "STRANDED"),
    (96.0,  "note",         "stranded - awaiting recovery"),
]
DRAIN_B = [(0.0, 0.20), (10.0, 3.70), (30.0, 0.50), (40.0, 0.32), (62.0, 0.15)]

# ticks inside this window are simulated but NOT emitted — the feed is dead
STALL_B = (40.2, 61.8)

SCENARIOS = {
    "a": dict(events=EVENTS_A, drain=DRAIN_A, end=106.0, battery=97.8, stall=None),
    "b": dict(events=EVENTS_B, drain=DRAIN_B, end=100.0, battery=96.0, stall=STALL_B),
}


def drain_at(drain, t):
    rate = drain[0][1]
    for t0, r in drain:
        if t >= t0:
            rate = r
    return rate


def generate(events, drain, end, battery, stall=None):
    s = dict(state="BOOT", battery_pct=battery, x=0.0, y=0.0, heading=0.0,
             speed=0.0, lidar="down", imu="down", comms="down",
             task="", task_idx=0, task_total=0, estop=0, note="")
    speed_target = 0.0
    heading_target = 0.0

    events = sorted(events, key=lambda e: e[0])
    ei = 0
    rows = []
    t = 0.0
    while t <= end + 1e-9:
        s["note"] = ""
        while ei < len(events) and events[ei][0] <= t + 1e-9:
            _, field, value = events[ei]
            if field == "speed_target":
                speed_target = value
            elif field == "heading_target":
                heading_target = value
            else:
                s[field] = value
            ei += 1

        # rate-limited speed and heading, then integrate position
        ds = speed_target - s["speed"]
        s["speed"] += max(-MAX_ACCEL * DT, min(MAX_ACCEL * DT, ds))
        dh = (heading_target - s["heading"] + 180.0) % 360.0 - 180.0
        s["heading"] = (s["heading"] + max(-MAX_TURN * DT, min(MAX_TURN * DT, dh))) % 360.0
        rad = math.radians(s["heading"])
        s["x"] += math.cos(rad) * s["speed"] * DT
        s["y"] += math.sin(rad) * s["speed"] * DT

        s["battery_pct"] = max(0.0, s["battery_pct"] - drain_at(drain, t) * DT)

        # The world keeps turning during a blackout; we simply do not see it.
        # This is why the first tick after the gap can be a shock.
        stalled = stall is not None and stall[0] <= t <= stall[1]
        if not stalled:
            rows.append({
                "t": round(t, 2),
                "state": s["state"],
                "battery_pct": round(s["battery_pct"], 2),
                "x": round(s["x"], 3),
                "y": round(s["y"], 3),
                "heading": round(s["heading"], 1),
                "speed": round(max(0.0, s["speed"]), 3),
                "lidar": s["lidar"],
                "imu": s["imu"],
                "comms": s["comms"],
                "task": s["task"],
                "task_idx": s["task_idx"],
                "task_total": s["task_total"],
                "estop": s["estop"],
                "note": s["note"],
            })
        t = round(t + DT, 4)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=sorted(SCENARIOS), default="a")
    ap.add_argument("--out", default="scenario.jsonl")
    args = ap.parse_args()

    cfg = SCENARIOS[args.variant]
    rows = generate(cfg["events"], cfg["drain"], cfg["end"], cfg["battery"], cfg["stall"])

    with open(args.out, "w", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")

    print(f"wrote {len(rows)} ticks ({rows[-1]['t']:.1f}s at {1/DT:.0f} Hz) -> {args.out}")
    print(f"battery {rows[0]['battery_pct']:.1f}% -> {rows[-1]['battery_pct']:.1f}%")
    if cfg["stall"]:
        lo, hi = cfg["stall"]
        print(f"FEED STALL from t={lo} to t={hi}  ({hi - lo:.1f}s with no data at all)")
    for r in rows:
        if r["note"]:
            print(f"  t={r['t']:>6.1f}  {r['state']:<9} batt={r['battery_pct']:>5.1f}%  {r['note']}")


if __name__ == "__main__":
    main()
