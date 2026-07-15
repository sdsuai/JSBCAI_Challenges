# LLM-RAG-WebUI-integration Grade 2

## Important note
* You must code in Python and/or C++.
* The "bare-minimum" task can be accomplished with just CPU. If your GPU is good enough just use that though.
* This task will require you to run your code from your machines OS terminal. For windows, its the powershell (there's another shell too I think), for macOS and Linux machines a common terminal is bash. Your OS might be using a different terminal from what I mentioned, or might have multiple, doesn't matter, just use one.
* After completing this task you will need to screen record to make a video showing that your code works and you explaining how it works. Obviously in the screen recording you MUST run your program from the terminal.
* Create a github repo containing your code and the video. Name the repo something like "JSB_grade_2_interview_problem" or something like that so it's identifiable.
* **IMPORTANT (READ THE ENTIRE BULLET POINT) For submission you must:**
   - **submit a pull request to this repo so that we have access to your username and get find your repo. However, so others don't copy your work, do not do you work in the public forked repo.**
   - **Make a private clone (or however you make things private) of the forked repo and do your actual work there.**
   - **Send an invite to me to the private repo (philipamadasun1@gmail.com) so I can gain access.**
   - **Please don't make me have to remake this repo again. In your ReadME, make sure to provide your email address.**
* You may freely use any tool available to you to accomplish this task. The internet, ChatGPT, anything.
* You could use some of the code above might help get you started if you choose.
  
## Tools you can use
The platform I advise to run LLMs from is [ollama](https://ollama.com/) as it's the easierst to set up, here is their [repo](https://github.com/ollama/ollama). The ollama repo also provides some example scripts that might provide some inspiration on how to go about solving some parts of the problem. There are other API platforms like vllm and llama.cpp you could try too. You could use the transformers library and fastAPI or flask and set up your own API service that way too.
For those with not so good PCs, again the "bare-minimum" can be done with just CPU, you can pull a small LLM like `gemma:2b` or `tinyllama` (these are around 2GB in size) locally on your ollama and just use those. For the webUI you may use streamlit and Flask as a server to retreive user queries and LLM responses from. I have provided two scripts which use streamlit and Flask to show a simple example of to get user input to show up on the streamlit webUI. Again, this is just advice, any other way you can get this done, you can just do that. You don't have to use ollama , or streamlit or Flask.

For **Part B (Networking & Data Transfer)** I have provided starter examples in the `examples/` folder: a TCP command server/client pair, a UDP telemetry sender/receiver pair, an MQTT pub/sub example, a curl cheatsheet, and (for the B6 extra credit) a memory-pressure demo server plus a memory-watcher script. These are deliberately minimal — they show you the mechanics (socket setup, message framing, sequence numbers), but you must adapt them into your own system. Copy-pasting them unmodified will not satisfy the requirements.

# 🧠 LLM + RAG WebUI Coding Challenge

**JSBCAI / Robotics Lab — LLM Engineering Task**

This challenge evaluates your ability to build **end-to-end LLM systems**, including:

* LLM API integration
* WebUI development
* RAG (Retrieval-Augmented Generation)
* Session & state management
* **Networking & data transfer (HTTP/curl, TCP, UDP, MQTT)**
* Tooling & evaluation
* Optional multimodal / speech
* Optional performance profiling

**You are allowed to use the internet and AI assistants (ChatGPT, Copilot, Gemini, etc.).**
What matters is your **implementation**, architecture reasoning, and the **video explanation** you submit.

---

# 📦 Overview

The challenge has **two parts**:

* **Part A — LLM + RAG WebUI**: build the WebUI + backend service described below.
* **Part B — Robot Networking & Data Transfer**: connect your backend to a robot simulator you write, using raw **TCP** for commands, **UDP** for telemetry, **curl** to exercise your HTTP API, and optionally **MQTT** for pub/sub. See the [Part B section](#-part-b-robot-networking--data-transfer) below.

You will build a **WebUI + backend service** that supports:

### Core Modes

1. **Chat Mode** — direct conversation with an LLM
2. **RAG Mode** — the LLM answers from supplied documents using retrieval
3. **(Optional)** **Tool Mode** — LLM outputs structured robot-action JSON

### Your system must include:

* A working WebUI (Streamlit, React, Flask templates, anything)
* A backend service (Flask/FastAPI/Node)
* Support for **streamed generation** into the UI
* The ability to switch between Chat and RAG modes
* Configurable model + server settings
* A reproducible RAG pipeline (document parsing → chunking → embeddings → retrieval)
* A session-based conversation memory
* A persistence layer (SQLite or JSONL logs)
* A short recorded video walkthrough explaining your system

---

# 🎯 Project Deliverables (What You Must Submit)

1. **A GitHub repository** containing:

   * Source code (backend + UI)
   * A `README.md` describing setup + usage
   * A `requirements.txt` or `environment.yml`
   * A `config.yaml` or `.env`

2. **A 4–10 minute walkthrough video** (screenshotted + recorded):

   * Show the running system
   * Explain architecture
   * Show Chat mode
   * Show RAG mode
   * Show retrieval sources displayed under answers
   * Show session persistence
   * **Part B:** run `curl_tests.sh` live; demonstrate the TCP kill/reconnect scenario; show live UDP telemetry and the `--drop 0.2` loss counter
   * If you implemented extra credit, demonstrate it

3. **A short write-up** (included in README or separate file):

   * What you built
   * What you struggled with
   * What you would improve with more time

You may use AI tools—but your submission must reflect **your own structure, engineering, debugging, and decisions**.

---

# 🧩 Architecture Requirements

Your system must include:

## 1. Backend API

* Can be **Flask**, **FastAPI**, **Node**, etc.

* Exposes endpoints for:

  * `/chat`
  * `/rag`
  * `/stream` (stream responses)
  * `/eval` (optional)
  * `/tool` (optional)

* Must load an LLM through:

  * **Ollama**, or
  * **llama.cpp server**, or
  * **OpenAI-compatible API**

* Must support both **blocking (“complete”)** and **streaming** responses.

## 2. WebUI

* Any framework:

  * Streamlit
  * React frontend + backend
  * Flask/HTML/CSS
  * Gradio (allowed, but less preferred unless styled cleanly)

### UI Requirements:

* Two clearly labeled modes:

  * **Chat**
  * **RAG**
* User and LLM messages must be styled differently (colors / bubbles)
* Show model name & mode in interface
* Show **streaming token-by-token responses**
* Show **sources** for RAG answers (retrieved chunks)
* Ability to **switch modes without losing conversation history**
* Ability to **filter conversation history by mode**
* Show **session ID** somewhere

## 3. Session Memory + Persistence

Always store:

* Timestamp
* Mode
* Input prompt
* LLM response
* RAG retrieved chunks
* (Optional) tool outputs
* Session ID

Persistence options:

* `session_logs.sqlite`
* `logs.jsonl`
* Anything reproducible and queryable

Sessions must reload the last N turns at startup.

---

# 📘 RAG Requirements

Your RAG pipeline must include:

### ✔ Document ingestion

Use blog and/or PDFs.

### ✔ Chunking

* Reasonable chunk size (256–512 tokens or ~500 characters)
* Include chunk metadata (doc name, page number)

### ✔ Embeddings

Use a CPU-safe embedding model such as:

* `all-MiniLM-L6-v2` (Sentence Transformers)
* Or Ollama’s `mxbai-embed-large` or `nomic-embed-text`
  Both run on a MacBook.

### ✔ Vector store

Acceptable options:

* FAISS
* Numpy + cosine similarity
* Annoy
* A simple in-memory store

### ✔ Retrieval

Retrieve top-k chunks and show them in the UI.

### ✔ LLM answer with citations

Each answer must show:

* **Retrieved text snippets**
* **Document name / source**

---

# ⚙️ Config + Metadata Requirements

Include a `config.yaml` or `.env`:

```yaml
model: "tinyllama"
llm_server_url: "http://localhost:11434"
embedding_model: "all-MiniLM-L6-v2"
vector_store_path: "./index/faiss.index"
max_context_tokens: 4096
session_memory_turns: 10
```

Also provide:

* `run.sh` or
* `make run`

This should:

* Start the backend
* Start the UI
* Optionally start the local LLM server if needed

---

# 🧪 Required Technical Features

## ✔ Streaming responses

* Must be chunked, SSE (Server-Sent Events), or incremental polling
* UI must show text appearing gradually

## ✔ Mode switching

Chat → RAG should keep conversation state.
RAG → Chat should preserve the chat messages and continue naturally.

## ✔ Clean error handling

UI must indicate:

* When server is loading
* When LLM server is unreachable
* When LLM returns invalid JSON for tool mode

---

# 🌐 Part B: Robot Networking & Data Transfer

**This part is required.** In a real robotics lab, your LLM backend is the "brain" — but the robot is a separate machine (or at least a separate process). Data has to move between them over the network, and different kinds of data want different transports:

| Data                     | Transport      | Why                                                          |
| ------------------------ | -------------- | ------------------------------------------------------------ |
| User ↔ backend requests  | HTTP (TCP)     | request/response, human-triggered, must be reliable          |
| Robot commands           | raw TCP        | must arrive, must arrive in order, must be acknowledged      |
| Robot telemetry (pose, battery) | UDP     | high-rate, latest-value-wins; a dropped packet doesn't matter |
| Many-to-many messaging   | MQTT (extra credit) | multiple subscribers, decoupled senders/receivers        |

You will write a **robot simulator** (`robot_sim.py` — a separate process, run in its own terminal) and connect it to your Part A backend.

> 🖥️ **This entire part runs on any laptop** — macOS, Linux, or Windows. No physical robot, no GPU, no router config: every connection is between processes on your own machine over `localhost` (`127.0.0.1`), and the ports used (9000/9001) need no admin/sudo rights. If you can run Part A, you can run Part B.

> 💡 Starter code for every task below is in `examples/`. Read it, run it, then adapt it. The examples are the mechanics; the requirements below are the actual assignment.

---

## B1. HTTP fluency with curl (required)

Your backend from Part A already speaks HTTP. Prove you understand what your framework is doing for you by driving every endpoint **from curl, with no browser and no Python**.

Write a script `curl_tests.sh` that:

1. `GET`s a health/status endpoint and prints the **HTTP status code** (hint: `curl -s -o /dev/null -w "%{http_code}"`)
2. `POST`s a JSON chat request (`-H "Content-Type: application/json" -d '{...}'`) and pretty-prints the response
3. Hits your **streaming** endpoint with `curl -N` so tokens visibly arrive one at a time in the terminal
4. Sends a deliberately **malformed** request (bad JSON, wrong content-type, or missing field) and shows your backend returns a proper `4xx` — not a crash, not a `500`
5. Shows full request/response headers for one call using `curl -v`

In your README, briefly explain: what a request line, header, and body are; what status code classes (2xx/4xx/5xx) mean; and why `curl -N` is needed for streaming (what is curl buffering otherwise?).

> 🪟 **Windows users:** `curl.exe` ships with Windows 10+, but in PowerShell plain `curl` is an alias for `Invoke-WebRequest` — a different tool. Type `curl.exe` explicitly. For the script itself, either run `curl_tests.sh` in Git Bash / WSL, or submit an equivalent `curl_tests.ps1` — both are accepted.

**In the video:** run `curl_tests.sh` live and narrate what each call demonstrates.

*Extra credit that builds directly on this task: see [B6](#b6-memory-pressure-edge-cases-extra-credit-10).*

---

## B2. TCP command channel (required)

Your backend must send robot commands to `robot_sim.py` over a **raw TCP socket** (Python `socket` module — no HTTP libraries, no frameworks).

### Protocol

* `robot_sim.py` listens on a TCP port (e.g. `127.0.0.1:9000`)
* The backend connects and sends **newline-delimited JSON** commands:

```json
{"id": 1, "action": "move_to", "params": {"x": 0.4, "y": 1.1}}
```

* The robot replies to every command with an ACK on the same connection:

```json
{"id": 1, "status": "ok", "detail": "moving to (0.4, 1.1)"}
```

* Add a **UI button or endpoint** that sends a command and displays the ACK. If you implemented Tool Mode, wire it up: LLM outputs the action JSON → backend validates it → sends it over TCP → shows the robot's ACK in the UI. (If you didn't do Tool Mode, hardcoded/manual commands from the UI are fine.)

### Requirements (this is where the points are)

1. **Framing.** TCP is a *byte stream*, not a message stream. One `send()` does NOT equal one `recv()`. Your receiver must buffer bytes and split on `\n` correctly even if a message arrives split across two `recv()` calls, or two messages arrive in a single `recv()`. To prove it works, your `robot_sim.py` must survive a client that sends one command **one byte at a time** (write this test — it's ~5 lines).
2. **Reconnect.** Kill `robot_sim.py` while the backend is connected. The backend must detect the dead connection, report "robot offline" in the UI, and automatically reconnect when the robot comes back. (Hint: what does `recv()` return when the peer closes? What exception does `send()` raise?)
3. **Ordering.** Send 5 commands rapidly; ACKs must come back matched to the right `id`s.

In your README, explain: what the three-way handshake establishes, why TCP guarantees ordering, and what `SO_REUSEADDR` does (you'll find out why you want it the second time you restart your server).

**In the video:** demonstrate the reconnect scenario — kill the robot, show the UI reacting, restart it, show recovery.

---

## B3. UDP telemetry stream (required)

While running, `robot_sim.py` continuously sends telemetry over **UDP** to your backend at **10 Hz**:

```json
{"seq": 1042, "x": 0.38, "y": 1.02, "heading": 87.5, "battery": 91.2, "t": 1699999999.123}
```

* `seq` increments by 1 with every packet sent
* The backend listens on a UDP port, keeps only the **latest** telemetry, and exposes it (endpoint or WebSocket) to the UI
* The UI shows **live-updating** telemetry: position, heading, battery — plus:
  * **packets received**
  * **packets lost** (count the gaps in `seq`)
  * **loss %**

### Requirements

1. Telemetry updates visibly in the UI in near-real-time.
2. Loss tracking works. To prove it, add a `--drop 0.2` flag to `robot_sim.py` that randomly skips sending 20% of packets — your UI's loss counter must reflect roughly 20%.
3. The UDP listener must not block or crash your backend (thread, asyncio task, or separate process — your choice, but justify it in the README).

In your README, explain: why UDP is the right choice for telemetry but the wrong choice for commands; what happens to a UDP packet that arrives corrupted or when the receiver's buffer is full; and why "latest value wins" makes packet loss acceptable here.

**In the video:** show telemetry streaming live, then run with `--drop 0.2` and show the loss counter climbing.

---

## B4. Write-up: choosing a transport (required)

Add a section to your README (≈half a page) answering, in your own words:

1. Your phone streams video over UDP-based protocols but loads web pages over TCP. Why is that split the right one?
2. If you sent the 10 Hz telemetry over TCP instead of UDP and the network started dropping packets, what specifically would go wrong? (Think about what TCP does on loss, and what happens to *latency* of the newest data.)
3. Your robot command channel is one backend ↔ one robot. Now imagine 5 robots and 3 dashboards that all need everything. Why does the TCP approach get painful, and how does MQTT's pub/sub model fix it?

No AI-generated essays here please — short, concrete, and in your own words. This is the part where we find out if you understood what you built.

---

## B5. MQTT mode (extra credit, +10)

Replace (or run alongside) B2/B3 with **MQTT** pub/sub:

* Run a broker locally: `sudo apt install mosquitto` / `brew install mosquitto` (or use a public test broker like `test.mosquitto.org` — fine for this exercise, but note in your README why you'd never do that in production)
* Use `paho-mqtt` (see `examples/mqtt_example.py`)
* Topics:
  * `robot/<robot_id>/cmd` — backend publishes commands, robot subscribes (**QoS 1**)
  * `robot/<robot_id>/telemetry` — robot publishes telemetry, backend subscribes (**QoS 0**)
  * `robot/<robot_id>/status` — robot publishes `online`/`offline` as a **retained** message, and sets an MQTT **Last Will** so the broker publishes `offline` automatically if the robot dies without saying goodbye
* Demonstrate the fan-out win: two terminals running `mosquitto_sub -t 'robot/#' -v` both receiving everything while your UI also updates — three subscribers, zero extra code in the robot.

In your README: explain QoS 0 vs 1 vs 2, why commands get QoS 1 but telemetry gets QoS 0, and what retained messages + Last Will give you that raw sockets don't.

**In the video:** kill the robot ungracefully (`kill -9`) and show the broker publishing the Last-Will `offline` message.

---

## B6. Memory-pressure edge cases (extra credit, +10)

Everything in B1 worked because your responses were a few KB. Real systems die on the big ones: a server that assembles a whole response in RAM before sending, or a client that reads a whole response into one variable, works perfectly in every demo — then gets OOM-killed the first time someone exports a month of session logs. In this task you make that failure mode **visible and measurable**, then fix it with streaming.

> ⚠️ **You are demonstrating a memory profile, not crashing your laptop.** 200–300 MB payloads are plenty to see the effect on any machine. Don't "test" with 20 GB — a frozen laptop is not the deliverable; a flat memory graph is.

**Tooling:** watch any process's memory with `./examples/watch_mem.sh <pid>` (macOS/Linux). Windows PowerShell equivalent:
`while ($true) { "{0:N0} MB" -f ((Get-Process -Id <pid>).WS / 1MB); Start-Sleep 0.5 }`
A complete worked demo of tasks 1–3 is in `examples/memory_hog_server.py` — run the experiments there first, then reproduce them on **your own backend**.

### 1. Buffered vs streamed export

Add an `/export?mb=N` endpoint to your backend that returns N megabytes of data (your session logs padded out, or synthetic fake logs). Build it **two ways**:

* **Buffered** — assemble the full payload in memory, then return it in one shot
* **Streamed** — a generator that yields ~1 MB chunks (Flask: `return Response(generator())`; FastAPI: `StreamingResponse`)

Run the same transfer against both while `watch_mem.sh` watches the **server**:

```bash
curl -s -o /dev/null "http://localhost:5000/export?mb=300&mode=buffered"
curl -s -o /dev/null "http://localhost:5000/export?mb=300&mode=streamed"
```

Record the peak server RSS for each in a small table in your README. Expected shape: buffered spikes by roughly the payload size; streamed stays near-flat. Then run both with `curl -v` and compare the response headers: which one has `Content-Length`, which one has `Transfer-Encoding: chunked`, and why *can't* the streamed one know its length up front?

*(Note: after the buffered request finishes, the server's RSS may not drop back down — Python's allocator keeps freed memory around. That's normal; restart the server between measurements for clean numbers.)*

### 2. Slow consumer (backpressure)

A streaming server is only safe if a **slow** client doesn't make it buffer everything anyway:

```bash
curl --limit-rate 500k -o /dev/null "http://localhost:5000/export?mb=50&mode=streamed"
```

Server RSS must stay flat for the entire (slow) transfer. In your README, explain *why*: what pauses your generator when curl won't read fast enough? Follow the chain — client stops reading → its TCP receive window fills → the server's socket send buffer fills → the framework's write of your yielded chunk blocks → your generator simply isn't advanced again until the client catches up.

### 3. Giant request body → 413

Clients can hurt you too. Generate an oversized upload and throw it at your `/chat` endpoint:

```bash
python3 -c "open('big.json','w').write('{\"message\": \"' + 'x'*(50*1024*1024) + '\"}')"
curl -i -X POST http://localhost:5000/chat -H "Content-Type: application/json" --data-binary @big.json
```

Your server must reject it with **`413 Payload Too Large`** via a configured limit (Flask: `MAX_CONTENT_LENGTH`; FastAPI: check `Content-Length` in a middleware) — **before** parsing or loading the body. A 500, a hang, or a worker whose memory balloons by 50 MB all score zero for this task.

### 4. The client side: `stream=True`

The same bug exists from the client seat — `requests.get(url)` downloads the **entire** body into `r.content` before you see any of it. Run `examples/requests_stream_demo.py` against your streamed endpoint both ways and record the client's peak RSS:

```bash
python3 examples/requests_stream_demo.py buffered   # peak RSS ≈ payload size
python3 examples/requests_stream_demo.py streamed   # flat: stream=True + iter_content()
```

In your README: where in your Part A UI code would you *have* to use `stream=True`, and what's the trade-off (you must consume or close the response; you can't inspect the whole body before acting on it)?

**In the video:** split screen — `watch_mem.sh` on the server while you run the buffered and streamed exports back to back, then show the 413 rejection live.

---

# 🛠 Extra Credit (Choose Any)

These are optional but valuable.

## 🟦 Tier 1 (MacBook-friendly)

### 1. 🔧 Tool Mode (Robot Action JSON)

LLM must output a JSON of the form:

```json
{
  "action": "move_to",
  "params": {"x": 0.4, "y": 1.1},
  "natural_language_explanation": "I'm moving toward the desk."
}
```

Backend must:

* Validate JSON
* Display parsed actions in UI
* Show errors if malformed

### 2. 📊 Automatic Evaluation Mode

Create `--eval` CLI or `/eval` endpoint:

* Ask 5–10 questions about the provided docs
* Use RAG mode internally
* Compare answers with:

  * Keyword overlap, OR
  * Exact expected phrases
* Produce a score like:

```
RAG Accuracy: 7/10 (70%)
```

### 3. 🕒 Performance Metrics

(x) Time-To-First-Token
(x) Total response time
(x) Token throughput (tokens/s)
(x) Embedding indexing time

Show metrics in UI or log them.

## 🟧 Tier 2 (Requires GPU or stronger desktop)

### 4. 🗣️ Speech Mode

* Low-resource STT (`faster-whisper small`)
* Any TTS (even API-based)
* UI button:

  * “Record”
  * “Play answer audio”

### 5. 🖼 Multimodal Image Input

If you have a multimodal model:

* Add UI image upload
* Route prompt + image to model
* Show answer inline

### 6. 🧠 Large Model Mode

If on GPU:

* Run 7B–8B model locally
* Demonstrate faster inference or better quality
* Compare TTFT and throughput vs tiny CPU model

---

# 🧨 Grading Rubric

### Part A — LLM + RAG WebUI

| Category                     | Points | Description                                          |
| ---------------------------- | ------ | ---------------------------------------------------- |
| Backend implementation       | 20     | clean routing, LLM integration, streaming            |
| WebUI quality                | 20     | clarity, styling, colors, streaming, switching modes |
| RAG correctness              | 25     | indexing, retrieval, sources, citations              |
| Session memory + persistence | 10     | logs, reload, multi-session                          |
| Config & reproducibility     | 10     | `.env`, config.yaml, run.sh                          |
| Video walkthrough            | 15     | clarity, explanation, demonstration                  |
| **Extra Credit Tier 1**      | +10    | tool mode, eval mode, profiling                      |
| **Extra Credit Tier 2**      | +10    | speech/multimodal/big model                          |

### Part B — Networking & Data Transfer

| Category                        | Points | Description                                                      |
| ------------------------------- | ------ | ---------------------------------------------------------------- |
| B1: curl / HTTP fluency         | 10     | `curl_tests.sh`, status codes, streaming with `-N`, 4xx handling |
| B2: TCP command channel         | 15     | correct framing (byte-at-a-time test), ACKs, reconnect handling  |
| B3: UDP telemetry               | 15     | live UI updates, seq-based loss tracking, `--drop` demo          |
| B4: Transport write-up          | 5      | correct, concrete, in your own words                             |
| **B5 Extra Credit: MQTT**       | +10    | QoS, retained + Last Will, fan-out demo                          |
| **B6 Extra Credit: memory pressure** | +10 | buffered-vs-streamed RSS table, backpressure, 413, `stream=True` |

**Maximum: 100 (Part A) + 45 (Part B) + 40 extra credit = 185 points**

---

# 🚀 Suggested System Architecture Diagram

```
User → WebUI → Backend API → LLM Server
                 ↑    ↓
          Vector Store ← Embeddings
                 ↑
             Documents

                 Backend API
                  ↑       ↓
        UDP :9001 |       | TCP :9000  (or MQTT topics robot/<id>/...)
            telemetry   commands+ACKs
                  ↑       ↓
                 robot_sim.py
```

---

# ▶️ How to Run (Candidate fills these out)

This section will be filled by you (the candidate) after implementation:

```
pip install -r requirements.txt
ollama serve &
ollama pull tinyllama
python backend/main.py
streamlit run ui/app.py
```

---

# 🎥 Final Submission Checklist

Before submitting, ensure you have:

### ✔ GitHub repo with full source

### ✔ README with setup + explanation

### ✔ Session memory + persistence implemented

### ✔ RAG with visible sources

### ✔ Streaming UI

### ✔ Mode switching fully working

### ✔ `curl_tests.sh` (or `curl_tests.ps1`) with all 5 required calls

### ✔ TCP command channel with framing + reconnect

### ✔ UDP telemetry with loss tracking + `--drop` flag

### ✔ Transport write-up (B4) in README

### ✔ Video walkthrough (screenshotted + recorded)

### ✔ Optional: MQTT mode (QoS, retained, Last Will)

### ✔ Optional: memory-pressure edge cases (streamed export, backpressure, 413, `stream=True`)

### ✔ Optional: performance metrics

### ✔ Optional: tool mode / eval mode / speech / multimodal

