
# **Assignment: YOLO Object Tracking, Object Relations, and a Simple “Robot Policy” — Grade 3**

> **This is the Grade 3 variant — the hardest.** Grade 2 added the memory work
> (section 4). Grade 3 makes the **robot policy required** rather than extra
> credit, and adds **section 5: real-time behaviour and policy safety** — the
> part where the policy has to survive a pipeline that is slower than the
> camera and a detector that is sometimes wrong. Grades 1 and 2 are lighter.
> If you were sent here directly, this is the one to do.

* This task will require you to run your code from your machines OS **terminal**. For windows, its the powershell (there's another shell too I think), for macOS and Linux machines a common terminal is bash. Your OS might be using a different terminal from what I mentioned, or might have multiple, doesn't matter, just use one.
* After completing this task you will need to screen record to make a video showing that your code works and you explaining how it works. Obviously in the screen recording you MUST run your program from the terminal.
* Create a github repo containing your code and the video. Name the repo something like "JSB_grade_3_interview_problem" or something like that so it's identifiable.
* **IMPORTANT (READ THE ENTIRE BULLET POINT) For submission you must:**
   - **submit a pull request to this repo so that we have access to your username and get find your repo. However, so others don't copy your work, do not do you work in the public forked repo.**
   - **Make a private clone (or however you make things private) of the forked repo and do your actual work there.**
   - **Send an invite to me to the private repo (philipamadasun1@gmail.com) so I can gain access.**
   - **Please don't make me have to remake this repo again. In your ReadME, make sure to provide your email address.**
* You may freely use any tool available to you to accomplish this task. The internet, ChatGPT, anything.

## **Time commitment — 5 to 7 days**

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

If you run out of time, cut breadth in D4 first — fewer degraded conditions,
reported properly. Do not cut D2 or D3: frame dropping and policy safety are
the point of this grade. Say what you cut and why. Scoping under pressure is an engineering skill and we grade it as one.


## **Overview**

In this project, you will use **YOLO** (You may use Ultralytics to perform:

1. **Object Detection**
2. **Object Tracking**
3. **Object Relations Analysis**

   * Distance
   * Left/right relationship
   * Approaching / moving away

4. **Robot policy** — actions chosen from what the "robot" sees.
   **Required at this grade** (extra credit in Grades 1 and 2.)

   * No physical robot required
   * All logic simulated through code

5. **Real-time behaviour and policy safety** — new at this grade. Measuring how
   old your data is when you act on it, dropping frames instead of falling
   behind, and making sure the policy fails safe when perception does not.

You will also instrument your pipeline's **CPU RAM and GPU VRAM usage** and demonstrate that you understand how differently the two behave — the OS silently pages CPU memory to disk, while VRAM is yours to manage explicitly. See **Memory Management (section 4)**.

Then you will make it behave in real time. A tracker that is correct but 1.8 s behind is not a slow robot, it is a robot steering by where things used to be — and the failure is silent, because nothing errors and the frame rate looks fine. See **Real-Time Behaviour & Policy Safety (section 5)**.

You must use **your own video(s)** — either recorded by yourself or found online.

You may use **any resources or tools**, including:

* Internet tutorials
* GitHub code examples
* StackOverflow
* AI tools (ChatGPT, Claude, Gemini, Copilot, etc.)

However: **Your submitted work must be your own**, and your demo video must clearly demonstrate that **you personally understand your code**.

---

# **Project Requirements**

---

## **1. Your Own Video(s)**

You must provide **at least one video**, 10–30 seconds long, containing:

* A static or handheld camera view
* 1–3 object types (person, bottle, phone, chair, laptop, etc.)
* Motion that YOLO can track (objects or people moving)

Good examples:

* You walking toward an object
* A person picking something up
* Objects being moved around a table
* A scene you found online with multiple interacting objects

---

## **2. Code Requirements**

Your Python code must perform the following:

---

### **Part A — YOLO Object Detection & Tracking**

Using Ultralytics YOLO:

```bash
pip install ultralytics opencv-python numpy matplotlib psutil
```

You must:

1. Load a YOLO model (`yolov8n.pt` recommended for speed)
2. Run **object detection & tracking** on your video
3. Extract **per-frame data**:

   * Bounding boxes
   * Class names / IDs
   * Track IDs
   * Object centers

**Starter Code you could use/modify:**

```python
from ultralytics import YOLO
import numpy as np

model = YOLO("yolov8n.pt")

results = model.track(
    source="input.mp4",
    stream=True,
    persist=True,
    verbose=False
)

tracks = []

for frame_idx, result in enumerate(results):
    frame_data = []
    boxes = result.boxes

    if boxes is not None and len(boxes) > 0:
        xyxy = boxes.xyxy.cpu().numpy()
        cls = boxes.cls.cpu().numpy().astype(int)
        ids = boxes.id.cpu().numpy().astype(int) if boxes.id is not None else np.arange(len(xyxy))

        for box, c, tid in zip(xyxy, cls, ids):
            x1, y1, x2, y2 = box
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            frame_data.append({
                "track_id": int(tid),
                "class_id": int(c),
                "bbox": [float(x1), float(y1), float(x2), float(y2)],
                "center": [float(cx), float(cy)]
            })

    tracks.append(frame_data)
```

A runnable version of this snippet — which also writes a per-frame `tracks.csv` — is in `examples/yolo_track_starter.py`:

```
python examples/yolo_track_starter.py your_video.mp4
```

---

### **Part B — Object Relations Analysis**

For at least **one pair** of object types (e.g., person–bottle):

You must compute:

#### **1. Pixel Distance**

```python
def pixel_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))
```

#### **2. Left / Right Relationship**

```python
def left_or_right(a_center, b_center):
    ax, _ = a_center
    bx, _ = b_center
    if bx < ax:
        return "left"
    elif bx > ax:
        return "right"
    else:
        return "aligned"
```

#### **3. Approaching / Moving Away / Stable**

For each tracked pair:

* Compute distance at frame `t` and `t+1`
* Compare trends over time

#### **4. Plot Distance vs Frame**

You must produce at least one plot showing a relationship like:

```python
import matplotlib.pyplot as plt

plt.plot(frames, distances)
plt.xlabel("Frame")
plt.ylabel("Distance (pixels)")
plt.title("Distance Over Time")
plt.show()
```

#### **5. Save a CSV or JSON of object relations**

Example CSV:

```
frame, objectA_id, objectB_id, distance, side, relation
0, 1, 7, 145.2, left, approaching
1, 1, 7, 130.9, left, approaching
...
```

---

## **3. Robot Policy (REQUIRED at this grade)**

Design a **robot controller** that chooses an action for each frame.

This is extra credit in Grades 1 and 2 and required here, because section 5
below is entirely about making it safe — and you cannot harden a policy you
have not written.

### **Choose One Task (or propose your own)**

#### **Option 1 — Follow the Person**

* If person is left of center → `TURN_LEFT`
* If right → `TURN_RIGHT`
* If too small → `MOVE_FORWARD`
* If too large → `MOVE_BACKWARD`
* Otherwise → `STOP`

#### **Option 2 — Protect an Object**

* If a person gets too close → `RAISE_ALERT`
* Otherwise → `IDLE`

#### **Option 3 — Center Between Two Objects**

* Robot tries to align itself between the left and right object

---

## **Complete Policy Function Example (Must Be Included in README)**

This example must appear in your write-up:

```python
def robot_policy(frame_info, image_width, image_height):
    """
    frame_info: list of detected objects for the current frame (track_id, class_id, bbox, center).
    Returns: a string representing the robot's action for this frame.
    """

    # Example: follow the main person (lowest track ID)
    persons = [obj for obj in frame_info if obj["class_id"] == 0]  # YOLO: class_id 0 = person
    if len(persons) == 0:
        return "SEARCH"

    person = sorted(persons, key=lambda x: x["track_id"])[0]
    cx, cy = person["center"]
    x_center = image_width / 2

    x1, y1, x2, y2 = person["bbox"]
    box_height = y2 - y1

    # Horizontal control
    offset_x = cx - x_center
    if abs(offset_x) > 0.1 * image_width:
        if offset_x < 0:
            direction = "TURN_LEFT"
        else:
            direction = "TURN_RIGHT"
    else:
        direction = "ALIGNED"

    # Distance control
    if box_height < 0.2 * image_height:
        distance_cmd = "MOVE_FORWARD"
    elif box_height > 0.4 * image_height:
        distance_cmd = "MOVE_BACKWARD"
    else:
        distance_cmd = "HOLD_POSITION"

    return f"{direction} + {distance_cmd}"
```

### Your Code Must:

* Produce a CSV of actions per frame
* Include readable logic
* Explain design choices

Example CSV output:

```
frame, action
0, SEARCH
1, TURN_LEFT + MOVE_FORWARD
2, ALIGNED + HOLD_POSITION
...
```

---

# **4. Memory Management (CPU RAM vs GPU VRAM)**

Your tracker pushes hundreds of video frames through a neural network — the perfect place to learn how memory *actually* behaves. The core lesson:

> **CPU RAM is managed *for* you.** The OS hands out virtual address space, only backs it with physical pages when you touch them, and can silently swap pages to disk when RAM runs short. Your program doesn't crash — it slows down.
>
> **GPU VRAM is managed *by* you.** CUDA allocations are pinned physical memory: no paging, no swap. Exceed it and you get a hard `OutOfMemoryError`. And PyTorch's caching allocator holds onto "freed" VRAM, so `nvidia-smi` says you're using memory you thought you released — until you explicitly call `torch.cuda.empty_cache()`.

> 🖥️ **No NVIDIA GPU?** C1 and C2 run fine on CPU. For C3, use Google Colab's free T4 GPU — every experiment fits in one notebook cell. Apple Silicon Mac users: also do C3 on Colab; your GPU shares *unified* memory with the CPU, which changes the story (that's the bonus question in C4).

**Starter helpers in `examples/`:** `yolo_track_starter.py` (runnable Part A pipeline + CSV), `mem_monitor.py` (drop-in telemetry class for your tracking loop), `vram_vs_ram_demo.py` (a guided tour of every effect in C3 — run it before writing your own), and `watch_mem.sh` (watch any process's RAM from a second terminal). An index of which example supports which requirement is in `examples/README.md`; deps are in `examples/requirements.txt`. Watch the GPU from outside with `watch -n 0.5 nvidia-smi`.

---

## **C1 — In-app memory telemetry (required)**

Instrument **your own tracking loop**. Every frame (or every N frames), record:

* wall-clock time and frame index
* **CPU:** your process's resident memory (RSS) via `psutil`
* **GPU (if CUDA is available):** all three layers —
  * `torch.cuda.memory_allocated()` — your live tensors
  * `torch.cuda.memory_reserved()` — tensors **plus** PyTorch's cache
  * used memory from `torch.cuda.mem_get_info()` — everything the driver has handed out (matches `nvidia-smi`)

**Deliverables:**

1. `memory_log.csv` written at the end of every run
2. A **memory-vs-frame plot** (it sits nicely next to your distance-vs-frame plot)
3. An end-of-run summary print: peak RSS and `torch.cuda.max_memory_allocated()`
4. *(Nice touch for the demo video)* overlay the live numbers on your annotated output frames with `cv2.putText`

---

## **C2 — Make it leak, then fix it (required)**

Run two controlled experiments on your longest video, with C1 telemetry running. **Note:** if your machine gets low on RAM during these, it may start swapping — everything crawls but nothing crashes. That is exactly the OS flexibility this section is about; describe it in your write-up instead of hiding it. Do **not** push it all the way to a frozen machine on purpose.

### (a) `stream=False` vs `stream=True`

Ultralytics' `model.track(source=...)` **without** `stream=True` returns a *list* containing a `Results` object for **every frame of the whole video**. With `stream=True` it returns a generator — one frame in memory at a time. Run your pipeline both ways and plot the two RSS curves on the same axes.

In your README, explain what is actually heavy inside a `Results` object. Hint: inspect `result.orig_img` — every `Results` carries the **full decoded frame** with it. Estimate the math: `height × width × 3 bytes × number_of_frames` and compare it to what your plot shows.

### (b) The reference leak

Even with `stream=True`, this innocent-looking line re-creates the whole problem:

```python
all_results = []
for result in model.track(source="input.mp4", stream=True, persist=True):
    all_results.append(result)      # <-- pins every frame in memory forever
```

Python frees memory when the *last reference* dies. The generator lets each `result` go — your list grabs it back. Fix it the way the Part A starter code does: extract plain floats with `.cpu().numpy()` into your own small dicts, and let `result` fall out of scope.

**Deliverables:** the leaky plot and the fixed plot, plus a short explanation of both mechanisms in your README.

---

## **C3 — The VRAM lifecycle (required — GPU or Colab)**

First run `examples/vram_vs_ram_demo.py` and watch it alongside `nvidia-smi`. Then reproduce each effect in your own code or notebook, with a screenshot per stage:

1. **Three numbers, three layers.** After your video finishes, print `memory_allocated()`, `memory_reserved()`, and driver-used from `mem_get_info()`, and put `nvidia-smi` next to them. Explain each layer — and why `nvidia-smi` is the biggest number (the CUDA context alone costs hundreds of MB).
2. **Cache emptying.** `del` your model and tensors. `memory_allocated()` drops — but `memory_reserved()` doesn't, and `nvidia-smi` still shows the memory as used. Only `torch.cuda.empty_cache()` hands the cached blocks back to the driver. Show `nvidia-smi` before and after the call. Then answer: PyTorch keeps that cache *on purpose* — why would calling `empty_cache()` every frame make your tracker **slower**?
3. **Hard OOM vs soft RAM.** Deliberately request more than the GPU has (e.g. 1.25× total VRAM), catch `torch.cuda.OutOfMemoryError`, and recover **without restarting the process**. Then request the *same size* from the CPU with `np.zeros(...)` — it "succeeds" instantly. Explain why (virtual pages exist only on paper until touched; check RSS).
4. **Graceful degradation in your app.** Your tracker must survive a mid-run CUDA OOM: catch it, then either retry at a smaller `imgsz` or fall back to `device="cpu"` — logging the event, not dying with a traceback.

---

## **C4 — Write-up (required)**

Answer in your README, in your own words (short and concrete beats long and vague):

1. Your laptop happily runs Chrome + YOLO + Spotify with more combined "memory" than physically exists. Why can't an 8 GB GPU run two 6 GB models the same way?
2. What exactly does `torch.cuda.empty_cache()` free — and what can it *never* free?
3. Why does `nvidia-smi` disagree with `torch.cuda.memory_allocated()`? Name all the layers in between.
4. "Swapping for GPUs" does exist — but **you** have to write it: moving tensors with `.cpu()` and back, or layer offloading when serving big LLMs. Why can't the driver just page VRAM to disk transparently, the way the OS does with RAM? One paragraph of your own reasoning (think: bandwidth, latency, and who knows what's needed next).
5. *(Bonus)* Apple Silicon Macs give the GPU *unified* memory shared with the CPU. Which C3 effects would disappear there, and which would remain?

---

# **5. Real-Time Behaviour & Policy Safety**

Section 4 was about running out of *memory*. This one is about running out of
*time*, and it is the difference between a pipeline that works on a video file
and one you would let near a real machine.

The core idea, which every requirement below circles:

> **A detection is only useful if it is still true.** Everything your pipeline
> does — decode, inference, tracking, relations, policy — happens *after* the
> moment the frame was captured. By the time you act, the world has moved on.
> How far it moved is a number you can measure, and almost nobody does.

**Starters, all runnable in seconds with no GPU, no model download and no
video:** `examples/latency_probe.py` (D1), `examples/realtime_loop.py` (D2),
`examples/policy_safety.py` (D3) and `examples/degrade_video.py` (D4). Run the
first three back to back before you write anything — together they take about
thirty seconds and they *are* the brief for this section.

---

## **D1 — Latency budget (required)**

Instrument your own pipeline per stage: decode, inference, tracking, relations,
policy.

**Report percentiles, not averages.** "30 FPS" is a mean, and means hide the
thing a robot cares about. If 99 frames take 20 ms and one takes 900 ms, the
average is a healthy 29 ms and the robot still drove blind for nearly a second.

**Deliverables:**

1. `latency.csv` — per-frame, per-stage timings
2. A table of **p50 / p95 / p99 / max** for every stage and for end-to-end
3. **The age of the data your policy acted on** — capture to action, including
   any time the frame spent waiting in a queue. This is the headline number of
   the whole section
4. Your **p99 ÷ p50 ratio**, and an explanation of what causes the tail in
   *your* pipeline

In your write-up: which stage dominates, and did that match your guess before
you measured?

---

## **D2 — Real-time or bust: drop frames, do not queue them (required)**

Your camera produces frames at a fixed rate. YOLO does not care. When the
pipeline is slower than the source, you get exactly two choices:

* **Queue everything.** Nothing is lost, the backlog grows forever, and every
  frame you process is older than the last.
* **Drop the oldest.** You process fewer frames, and every one you *do* process
  is the newest available. Age stays bounded no matter how long you run.

For a recording pipeline the first is right. For a robot the second is right,
and it is not a compromise: **a stale frame has negative value**, because you
will confidently act on the past.

> **You have already met this bug.** In C2, an unbounded list between a fast
> producer and a slow consumer ate RAM. Here, an unbounded queue between a fast
> producer and a slow consumer eats *time*. Same shape, different resource:
> **unbounded buffer + producer faster than consumer = something grows without
> bound.** Naming that general rule is worth marks.

**Deliverables:**

1. A bounded, drop-oldest hand-off between frame capture and inference —
   capacity one or two. `examples/realtime_loop.py` shows the mechanism
2. A run where inference is genuinely slower than the source (use a longer
   video, a bigger model, or `--work-ms` in the starter to prove the shape)
3. **One plot, two curves**: data age over time, queued vs drop-oldest. The
   queued curve climbs; the dropped one is flat
4. Frames processed and frames dropped for both. Note that throughput is
   usually about the *same* — you did not lose work, you lost lag

> ⚠️ If you use OpenCV's `cap.read()`, note it pulls from a driver-side buffer
> that queues **for** you. A slow loop silently accumulates lag even though your
> code contains no queue at all. Finding that is part of the exercise.

---

## **D3 — Policy safety (required)**

Your policy from section 3 is correct on clean data. Now make it safe on real
data. `examples/policy_safety.py` implements all four mechanisms with a runnable
before/after.

**Required behaviours:**

1. **Deadband / hysteresis.** A person sitting exactly on your turn threshold
   makes a naive policy emit `TURN_LEFT, ALIGNED, TURN_LEFT, ALIGNED` at 30 Hz.
   Use two thresholds: a wide one to start turning, a narrow one to stop.
2. **Staleness watchdog.** If the tracked object has not been seen for a while,
   the policy must fall back to a safe action — **not** keep steering toward the
   last known position. It must be measured in **seconds, not frames**: your
   frame rate varies (see D1/D2), so "10 frames" means 300 ms on a good run and
   3 s on a bad one.
3. **Minimum dwell time.** Hold each action briefly before allowing another
   change, so you emit commands an actuator could actually follow. Safety
   actions must bypass this — a stop must never wait its turn.
4. **Track-lock and ID switches.** YOLO track IDs are not stable. When the ID
   you were following vanishes and a new one appears, a naive policy silently
   starts following a different person. Lock on, notice the loss, and require
   the replacement to be stable before adopting it.

**Deliverables:**

1. `actions.csv` **before and after** the safety layer, from the same video
2. **Action changes per second** for both. The drop should be dramatic
3. The watchdog demonstrated: a segment where the object is occluded or leaves
   frame, showing the naive policy still issuing steering commands and the
   guarded one falling back to a safe action
4. Your chosen thresholds and timeouts, **with the reasoning**. "It looked
   right" is not reasoning; relate them to your D1 numbers

---

## **D4 — Degraded input (required)**

Generate degraded versions of your own video and rerun the whole pipeline on
each:

```
python examples/degrade_video.py your_video.mp4 --all
```

You get low-light, motion blur, occlusion, heavy compression, and a frozen-feed
variant. Report **per condition**:

| condition | detection rate | ID switches | mean confidence | what the policy did | did the D3 watchdog engage? |
| --- | --- | --- | --- | --- | --- |

Then answer the question that matters:

> **Which failure mode is more dangerous — a detector that returns nothing, or
> one that returns a confident wrong box?**

One of those your watchdog handles cleanly. The other one it cannot see at all,
because a confidently wrong detection looks exactly like a good one from the
policy's side. Say what you would do about it.

---

## **D5 — Write-up (required)**

In your README, in your own words:

1. Your p50 and p99 end-to-end latency. Why does a robot care more about the
   tail than the average?
2. Unbounded queue vs drop-oldest. Relate it to the C2 memory leak — what is
   the general rule that covers both?
3. Your policy acted on data that was N ms old. At a plausible robot speed
   (say 0.5 m/s), how far did the world move in that time? What does that mean
   for the thresholds you chose in D3?
4. Why must the staleness watchdog be measured in seconds rather than frames?
5. A wrong detection at 0.9 confidence is more dangerous than no detection at
   all. Why — and what, if anything, can the policy do about it?

---

# **6. Documentation (README.md Requirements)**

Your README must clearly explain:

### ✔ How to install and run your code

Commands, examples, environment setup, etc.

### ✔ Description of your video(s)

* What objects appear
* Why you chose the scene
* Any difficulties (lighting, occlusion, motion, etc.)

### ✔ Explanation of object relations

* Distance calculation
* Left/right decision
* Trend detection (approaching/moving away)

### ✔ Robot policy explanation

* What task you chose
* What each action means
* How thresholds were chosen

### ✔ Memory management (Part C)

* Memory-vs-frame plot, leaky vs fixed plots
* VRAM lifecycle screenshots (allocated / reserved / `nvidia-smi`, before & after `empty_cache()`)
* Answers to the C4 questions

### ✔ Real-time behaviour and policy safety (Part D)

* Latency table: p50 / p95 / p99 / max per stage, and the age of the data your
  policy acted on
* The two-curve plot: data age, queued vs drop-oldest
* Action changes per second, before and after the safety layer
* The degraded-input table, and your answer on which failure mode is worse

### ✔ Example outputs

* Plots
* CSV snippets
* Screenshot frames

---

# **7. Required Demo Video (6–10 Minutes)**

Your demo video must:

### A. Show your video(s)

Briefly play or describe them.

### B. Explain how your code works

Walk through:

* YOLO detection
* Tracking pipeline
* Relation analysis
* (Optional) Robot policy

### C. Show real outputs

You must show:

* Plots
* Logs
* Debug prints
* Example actions

### D. Show the memory work (Part C)

* Your memory-vs-frame plot, and the leaky vs fixed comparison
* Live: `torch.cuda.empty_cache()` with `nvidia-smi` visible side by side, showing reserved memory being handed back
* The mid-run OOM being caught and recovered from (C3.4)

### E. Show the real-time work (Part D)

* Your latency table, and say which stage dominates
* The queued-vs-dropped age plot, and what the climbing curve means
* **Live: the policy during an occlusion.** Show the naive version still issuing
  steering commands with nothing detected, and the guarded version falling back
  to a safe action
* One degraded-video condition running, and what broke

### F. Discuss challenges you faced

### G. Explain what you learned

This proves you personally understand the materials — even if you used AI tools for help.

---

# **8. Allowed & Not Allowed Resources**

### **Allowed**

* ANY internet tools or AI assistants
* Any libraries or open-source repos
* Any debugging help from classmates (no code sharing)

### **Not Allowed**

* Submitting code you clearly do not understand
* Copy-paste from AI or GitHub without modification
* Fake tracking results or manipulated outputs

---

# **9. Grading Rubric**

| Category                     | Points |
| ---------------------------- | ------ |
| YOLO Tracking Implementation | 25     |
| Object Relations Computation | 25     |
| Robot Policy (required at this grade) | 15 |
| Plots & Data Outputs         | 10     |
| C1: In-app memory telemetry  | 10     |
| C2: Leak experiments (stream=True, references) | 10 |
| C3: VRAM lifecycle + OOM recovery | 10 |
| C4: Memory write-up          | 5      |
| D1: Latency budget (percentiles, data age) | 10 |
| D2: Frame dropping vs queueing | 15   |
| D3: Policy safety (deadband, watchdog, dwell, track lock) | 15 |
| D4: Degraded input           | 10     |
| D5: Real-time write-up       | 5      |
| Documentation (README.md)    | 15     |
| Demo Video                   | 15     |
| **Extra Credit (see below)** | +25    |

Maximum: **195 (+25 bonus)**

## **Extra Credit (optional)**

The robot policy is required at this grade, so the bonus moves up a level:

| | Points | |
| --- | --- | --- |
| **Closed-loop simulation** | +15 | Feed the policy's action back into the pipeline — move a crop window over the frame as though the camera were on the robot. Errors now compound instead of being corrected by the next frame, which is the real test of whether your policy is stable. Show a run where it holds the target and a run where it loses it. |
| **Export and quantize** | +12 | Export to ONNX (or TensorRT / OpenVINO), rerun D1, and put the latency tables side by side. Report the accuracy you traded for the speed — measured, not assumed. |
| **Ground-truth evaluation** | +10 | Hand-label ~100 frames. Report precision, recall and ID switches against your labels rather than against your impression of the output. |
