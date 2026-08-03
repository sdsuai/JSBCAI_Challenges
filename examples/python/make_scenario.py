"""
make_scenario.py — generates scenario/scenario.jsonl, the canonical timeline.

You do NOT need to run this. `scenario/scenario.jsonl` is already committed and
is the file every candidate is graded against. This generator is here so you
can read exactly how the data was produced, and so you can author extra
timelines of your own for testing (see --out).

    python make_scenario.py --out ../../scenario/scenario.jsonl

The timeline is deliberately time-compressed: battery drain and mission
progress are far faster than real hardware, so the entire arc — boot, work,
two overlapping faults, an emergency stop, recovery, and shutdown — plays out
in under two minutes. That is a demo-pacing decision, not a physics claim.

Design intent of this timeline (why each event is here):

    t=1.4-4.2   sensors come up one at a time      -> partial/unknown state
    t=26.0      comms drops for 3.5s, then returns -> TRANSIENT fault: does
                                                      your UI cry wolf?
    t=46.0      battery crosses 20%                -> degraded but RUNNING
    t=52.0      lidar degrades, then dies at 55    -> TWO faults at once. Which
                                                      one does your design put
                                                      first, and why?
    t=58.0      EMERGENCY STOP                     -> irreversible, operator-
                                                      initiated, must not be
                                                      confusable with anything
    t=72.0      e-stop cleared                     -> recovery is a state, not
                                                      an instant
    t=85.0      battery crosses 8%                 -> a second severity tier
"""

import argparse
import json
import math

DT = 0.2  # 5 Hz
END = 106.0

# (t, field, value) — applied when playback time reaches t.
EVENTS = [
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

# Battery drain breakpoints: (t_from, percent_per_second). Tuned so the two
# severity thresholds (20%, 8%) land where the faults are, not for realism.
DRAIN = [(0.0, 0.15), (14.0, 2.60), (38.0, 1.65), (46.0, 0.55),
         (58.0, 0.18), (72.0, 0.22), (80.0, 0.24), (98.0, 0.10)]

MAX_ACCEL = 0.60      # m/s^2
MAX_TURN = 60.0       # deg/s


def drain_at(t):
    rate = DRAIN[0][1]
    for t0, r in DRAIN:
        if t >= t0:
            rate = r
    return rate


def generate():
    s = dict(state="BOOT", battery_pct=97.8, x=0.0, y=0.0, heading=0.0,
             speed=0.0, lidar="down", imu="down", comms="down",
             task="", task_idx=0, task_total=0, estop=0, note="")
    speed_target = 0.0
    heading_target = 0.0

    events = sorted(EVENTS, key=lambda e: e[0])
    ei = 0
    rows = []
    t = 0.0
    while t <= END + 1e-9:
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

        s["battery_pct"] = max(0.0, s["battery_pct"] - drain_at(t) * DT)

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
    ap.add_argument("--out", default="scenario.jsonl")
    args = ap.parse_args()
    rows = generate()
    with open(args.out, "w", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(f"wrote {len(rows)} ticks ({rows[-1]['t']:.1f}s at {1/DT:.0f} Hz) -> {args.out}")
    print(f"battery {rows[0]['battery_pct']:.1f}% -> {rows[-1]['battery_pct']:.1f}%")
    for r in rows:
        if r["note"]:
            print(f"  t={r['t']:>6.1f}  {r['state']:<9} batt={r['battery_pct']:>5.1f}%  {r['note']}")


if __name__ == "__main__":
    main()
