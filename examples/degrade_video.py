"""
degrade_video.py — make your own video worse, on purpose.

Supports D4. Needs opencv-python and numpy (you already have both).

    python examples/degrade_video.py input.mp4 --all
    python examples/degrade_video.py input.mp4 --effect lowlight --strength 0.25

Writes input_lowlight.mp4, input_blur.mp4, and so on, next to the original.

WHY
---
Your pipeline works on the clip you chose, which you filmed in good light,
holding the camera reasonably still, with the object nicely framed. A robot
gets none of those guarantees. It gets dusk, a camera bolted to something that
vibrates, a person half behind a doorway, and a compressed stream over wifi.

The interesting question is not whether accuracy drops — it will. It is:

    * WHICH degradation hurts most? (It is rarely the one people guess.)
    * Does the failure look like nothing detected, or like confidently wrong
      detections? Those need completely different handling.
    * Does the safety layer you built in D3 catch it, or does the policy sail
      on giving orders?

A detector that returns nothing is honest and your watchdog handles it. A
detector that returns a 0.9-confidence box around a coat rack is the dangerous
case, and no amount of confidence thresholding fully removes it.

EFFECTS
-------
  lowlight    scale brightness down and add sensor noise — dusk, indoors
  blur        directional motion blur — camera shake, fast pans
  occlude     a moving opaque rectangle — someone walks in front, a doorframe
  compress    heavy JPEG re-encoding per frame — a bad wifi stream
  dropframes  duplicate frames to simulate a stalled feed (see D2)

All of them keep the original resolution and frame rate, so your numbers stay
comparable across conditions.
"""

import argparse
import os
import sys

try:
    import cv2
    import numpy as np
except ImportError:
    sys.exit("needs opencv-python and numpy:  pip install opencv-python numpy")


def eff_lowlight(frame, s, rng, i):
    """s in (0,1]: fraction of original brightness. Noise rises as light falls,
    which is what a real sensor does — you are not just multiplying pixels."""
    dark = frame.astype(np.float32) * s
    noise_sigma = 12.0 * (1.0 - s)
    dark += rng.normal(0.0, noise_sigma, dark.shape)
    return np.clip(dark, 0, 255).astype(np.uint8)


def eff_blur(frame, s, rng, i):
    """s: blur length as a fraction of width. Directional, like real motion."""
    k = max(3, int(s * frame.shape[1]) | 1)          # odd kernel
    kernel = np.zeros((k, k), np.float32)
    kernel[k // 2, :] = 1.0 / k                       # horizontal streak
    return cv2.filter2D(frame, -1, kernel)


def eff_occlude(frame, s, rng, i):
    """A bar that sweeps across, covering s of the width."""
    h, w = frame.shape[:2]
    out = frame.copy()
    bw = max(1, int(s * w))
    # travels left to right and back, ~4 s period at 30 fps
    phase = (i % 240) / 240.0
    tri = 1.0 - abs(2.0 * phase - 1.0)
    x0 = int(tri * (w - bw))
    out[:, x0:x0 + bw] = 0
    return out


def eff_compress(frame, s, rng, i):
    """s in (0,1]: lower is worse. JPEG quality = 100*s, re-encoded per frame."""
    q = max(1, min(95, int(100 * s)))
    ok, enc = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), q])
    return cv2.imdecode(enc, cv2.IMREAD_COLOR) if ok else frame


def eff_dropframes(frame, s, rng, i):
    """Handled in the loop; the frame itself is untouched."""
    return frame


EFFECTS = {
    "lowlight":   (eff_lowlight,   0.25),
    "blur":       (eff_blur,       0.03),
    "occlude":    (eff_occlude,    0.30),
    "compress":   (eff_compress,   0.08),
    "dropframes": (eff_dropframes, 0.30),
}


def process(src, effect, strength, seed=0):
    fn, default = EFFECTS[effect]
    s = default if strength is None else strength
    rng = np.random.default_rng(seed)

    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        sys.exit(f"cannot open {src}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    stem, ext = os.path.splitext(src)
    out_path = f"{stem}_{effect}{ext or '.mp4'}"
    writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    if not writer.isOpened():
        sys.exit(f"cannot write {out_path} (codec problem?)")

    i = 0
    held = None
    written = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if effect == "dropframes":
            # Hold a stale frame for a run of frames: the feed froze, but the
            # file still has the right number of frames and the right duration.
            # A pipeline that trusts frame count over timestamps will not
            # notice a thing.
            if i % int(max(2, 1 / max(1e-6, s))) == 0:
                held = frame
            out = held if held is not None else frame
        else:
            out = fn(frame, s, rng, i)
        writer.write(out)
        written += 1
        i += 1

    cap.release()
    writer.release()
    print(f"  {effect:<11} strength={s:<6} -> {out_path}  ({written} frames)")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--effect", choices=sorted(EFFECTS))
    ap.add_argument("--strength", type=float, default=None)
    ap.add_argument("--all", action="store_true", help="generate every effect")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if not args.all and not args.effect:
        ap.error("give --effect NAME or --all")

    effects = sorted(EFFECTS) if args.all else [args.effect]
    print(f"source: {args.video}")
    for e in effects:
        process(args.video, e, args.strength, args.seed)

    print("\nNow run your full pipeline on each one and record, per condition:")
    print("  - detection rate (frames with the target found / total frames)")
    print("  - ID switches")
    print("  - mean confidence of the detections you DID get")
    print("  - what your policy did, and whether the D3 watchdog engaged")
    print("\nThe condition that produces confident WRONG detections is more")
    print("dangerous than the one that produces none. Say which is which.")


if __name__ == "__main__":
    main()
