
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

If you run out of time, a solid Part A and Part B with a clear README beats
a rushed robot policy — the policy is extra credit at this grade for exactly
that reason. Say what you cut and why. Scoping under pressure is an engineering skill and we grade it as one.


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
pip install ultralytics opencv-python numpy matplotlib
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

# **4. Documentation (README.md Requirements)**

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

### ✔ Example outputs

* Plots
* CSV snippets
* Screenshot frames

---

# **5. Required Demo Video (3–6 Minutes)**

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

### D. Discuss challenges you faced

### E. Explain what you learned

This proves you personally understand the materials — even if you used AI tools for help.

---

# **6. Allowed & Not Allowed Resources**

### **Allowed**

* ANY internet tools or AI assistants
* Any libraries or open-source repos
* Any debugging help from classmates (no code sharing)

### **Not Allowed**

* Submitting code you clearly do not understand
* Copy-paste from AI or GitHub without modification
* Fake tracking results or manipulated outputs

---

# **7. Grading Rubric**

| Category                     | Points |
| ---------------------------- | ------ |
| YOLO Tracking Implementation | 30     |
| Object Relations Computation | 30     |
| Plots & Data Outputs         | 10     |
| Documentation (README.md)    | 15     |
| Demo Video                   | 15     |
| **Tier 2 Extra Credit**      | +10    |

Maximum: **100 (+10 bonus)**
