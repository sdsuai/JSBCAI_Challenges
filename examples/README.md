# Starter examples — what each one is for

Each file shows the **mechanics** of one part of the assignment. Read it,
run it, then adapt it into your own pipeline. Copy-pasting a file
unmodified will not satisfy the requirement it supports.

## Quick index (by requirement)

| File | Supports | Run it |
| ---- | -------- | ------ |
| `yolo_track_starter.py` | Part A — YOLO detection + tracking, per-frame data, CSV | `python yolo_track_starter.py your_video.mp4` |
| `mem_monitor.py` | C1 — in-app memory telemetry (CPU RSS + 3-layer VRAM) | drop-in `MemoryLog` class, or `python mem_monitor.py` (self-test) |
| `vram_vs_ram_demo.py` | C3 — the VRAM lifecycle tour (4 acts) | `python vram_vs_ram_demo.py` |
| `watch_mem.sh` | watch any process's RSS from a second terminal | `./watch_mem.sh <pid>` |

Part B (object relations) and Tier 2 (robot policy) have their starter code
inline in the README — they consume the per-frame dicts that
`yolo_track_starter.py` produces.

## Install

```
pip install -r examples/requirements.txt
```

## Quick start

```
# 1) See tracking work on your own video (Part A)
python examples/yolo_track_starter.py your_video.mp4 --csv tracks.csv

# 2) Watch the VRAM story before instrumenting your own loop (C3)
python examples/vram_vs_ram_demo.py        # watch -n 0.5 nvidia-smi in another terminal

# 3) Then wrap MemoryLog around your real tracking loop (C1)
#    from mem_monitor import MemoryLog
#    memlog = MemoryLog()
#    for frame_idx, result in enumerate(results): ...
#        memlog.sample(frame_idx)
#    memlog.save_csv(); memlog.plot(); memlog.print_peaks()
```
