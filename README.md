
# **Assignment: YOLO Object Tracking, Object Relations, and a Simple “Robot Policy”**

* This task will require you to run your code from your machines OS **terminal**. For windows, its the powershell (there's another shell too I think), for macOS and Linux machines a common terminal is bash. Your OS might be using a different terminal from what I mentioned, or might have multiple, doesn't matter, just use one.
* After completing this task you will need to screen record to make a video showing that your code works and you explaining how it works. Obviously in the screen recording you MUST run your program from the terminal.
* Create a github repo containing your code and the video. Name the repo something like "JSB_grade_2_interview_problem" or something like that so it's identifiable.
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

If you run out of time, section 4 is where people over-invest. C1 and C2 are
the core of it; C3 needs a GPU or Colab and is the natural thing to trim if
something has to go. Trim it deliberately and say so in your README rather
than quietly leaving it out. Scoping under pressure is an engineering skill and we grade it as one.


## **Overview**

In this project, you will use **YOLO** (You may use Ultralytics to perform:

1. **Object Detection**
2. **Object Tracking**
3. **Object Relations Analysis**

   * Distance
   * Left/right relationship
   * Approaching / moving away

(Optional **Tier 2 / Extra Credit**):

4. Implement a simple **robot policy** that outputs actions based on what the “robot” sees.

   * No physical robot required
   * All logic simulated through code

You will also instrument your pipeline's **CPU RAM and GPU VRAM usage** and demonstrate that you understand how differently the two behave — the OS silently pages CPU memory to disk, while VRAM is yours to manage explicitly. See **Memory Management (section 4)**.

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

## **3. Tier 2 (Extra Credit): Simple Robot Policy**

Design a **robot controller** that chooses an action for each frame.

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

# **5. Documentation (README.md Requirements)**

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

### ✔ (Tier 2) Robot policy explanation

* What task you chose
* What each action means
* How thresholds were chosen

### ✔ Memory management (Part C)

* Memory-vs-frame plot, leaky vs fixed plots
* VRAM lifecycle screenshots (allocated / reserved / `nvidia-smi`, before & after `empty_cache()`)
* Answers to the C4 questions

### ✔ Example outputs

* Plots
* CSV snippets
* Screenshot frames

---

# **6. Required Demo Video (4–8 Minutes)**

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

### E. Discuss challenges you faced

### F. Explain what you learned

This proves you personally understand the materials — even if you used AI tools for help.

---

# **7. Allowed & Not Allowed Resources**

### **Allowed**

* ANY internet tools or AI assistants
* Any libraries or open-source repos
* Any debugging help from classmates (no code sharing)

### **Not Allowed**

* Submitting code you clearly do not understand
* Copy-paste from AI or GitHub without modification
* Fake tracking results or manipulated outputs

---

# **8. Grading Rubric**

| Category                     | Points |
| ---------------------------- | ------ |
| YOLO Tracking Implementation | 30     |
| Object Relations Computation | 30     |
| Plots & Data Outputs         | 10     |
| C1: In-app memory telemetry  | 10     |
| C2: Leak experiments (stream=True, references) | 10 |
| C3: VRAM lifecycle + OOM recovery | 10 |
| C4: Memory write-up          | 5      |
| Documentation (README.md)    | 15     |
| Demo Video                   | 15     |
| **Tier 2 Extra Credit**      | +10    |

Maximum: **135 (+10 bonus)**
