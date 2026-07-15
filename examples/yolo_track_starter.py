"""Minimal YOLO detection + tracking starter — the mechanics of Part A.

This is the README's inline snippet, made runnable and with a CSV dump so
you can see the per-frame data your relation analysis (Part B) and policy
(Tier 2) will consume. It is NOT your finished pipeline — adapt it, add
your relation math, your memory instrumentation (mem_monitor.py), and your
policy.

Run:
    python yolo_track_starter.py your_video.mp4
    python yolo_track_starter.py your_video.mp4 --model yolov8n.pt --csv tracks.csv

Needs: pip install ultralytics opencv-python numpy
First run downloads yolov8n.pt (~6 MB). Use your OWN video (README section 1).

Note on the API: stream=True makes model.track(...) return a GENERATOR —
one Result at a time. Without stream=True it returns a LIST holding every
frame, which is exactly the C2(a) memory leak you'll measure later. Start
the way you mean to go on: stream=True here, and don't keep a reference to
every result (C2(b)).
"""

import argparse
import csv
import sys

import numpy as np

try:
    from ultralytics import YOLO
except ImportError:
    sys.exit("missing ultralytics: pip install ultralytics")


def iter_frames(path, model_name):
    """Yield (frame_index, list_of_object_dicts) for each tracked frame.

    Each object dict is a small bag of plain floats — we deliberately do
    NOT keep the ultralytics Result object (see C2(b): it carries the full
    decoded frame in result.orig_img, and pinning every one is a leak).
    """
    model = YOLO(model_name)
    results = model.track(source=path, stream=True, persist=True, verbose=False)

    for frame_idx, result in enumerate(results):
        frame_data = []
        boxes = result.boxes
        if boxes is not None and len(boxes) > 0:
            xyxy = boxes.xyxy.cpu().numpy()
            cls = boxes.cls.cpu().numpy().astype(int)
            ids = (boxes.id.cpu().numpy().astype(int)
                   if boxes.id is not None else np.arange(len(xyxy)))

            for box, c, tid in zip(xyxy, cls, ids):
                x1, y1, x2, y2 = box
                frame_data.append({
                    "track_id": int(tid),
                    "class_id": int(c),
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "center": [float((x1 + x2) / 2), float((y1 + y2) / 2)],
                })
        yield frame_idx, frame_data


def main():
    p = argparse.ArgumentParser()
    p.add_argument("video", help="path to YOUR video (README section 1)")
    p.add_argument("--model", default="yolov8n.pt")
    p.add_argument("--csv", default="tracks.csv",
                   help="output CSV of per-frame detections")
    args = p.parse_args()

    names = YOLO(args.model).names  # class_id -> human-readable name
    print(f"[track] {args.video} -> {args.csv}  (classes: {list(names.values())[:6]})")

    with open(args.csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["frame", "track_id", "class_id", "x1", "y1", "x2", "y2",
                    "cx", "cy"])
        total = 0
        for frame_idx, frame_data in iter_frames(args.video, args.model):
            for o in frame_data:
                w.writerow([frame_idx, o["track_id"], o["class_id"],
                            *o["bbox"], *o["center"]])
            total += len(frame_data)
            if frame_idx % 30 == 0:
                print(f"  frame {frame_idx}: {len(frame_data)} objects")

    print(f"[track] done — {total} object-rows written to {args.csv}")


if __name__ == "__main__":
    main()
