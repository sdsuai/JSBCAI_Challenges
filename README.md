# LLM-RAG-WebUI-integration Grade 2


## Name and Email:
* Brandon Garate
* bgarate6105@sdsu.edu
* brandongarate177@gmail.com (GitHub)

# Details
I sent an invite to my private repo to (philipamadasun1@gmail.com). My video submission is uploaded on the GitHub.


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

# 🧠 LLM + RAG WebUI Coding Challenge

**JSBCAI / Robotics Lab — LLM Engineering Task**

This challenge evaluates your ability to build **end-to-end LLM systems**, including:

* LLM API integration
* WebUI development
* RAG (Retrieval-Augmented Generation)
* Session & state management
* Tooling & evaluation
* Optional multimodal / speech
* Optional performance profiling

**You are allowed to use the internet and AI assistants (ChatGPT, Copilot, Gemini, etc.).**
What matters is your **implementation**, architecture reasoning, and the **video explanation** you submit.

---

# 📦 Overview

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

2. **A 3–7 minute walkthrough video** (screenshotted + recorded):

   * Show the running system
   * Explain architecture
   * Show Chat mode
   * Show RAG mode
   * Show retrieval sources displayed under answers
   * Show session persistence
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

**Maximum: 110 points**

---

# 🚀 Suggested System Architecture Diagram

```
User → WebUI → Backend API → LLM Server
                 ↑    ↓
          Vector Store ← Embeddings
                 ↑
             Documents
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

### ✔ Video walkthrough (screenshotted + recorded)

### ✔ Optional: performance metrics

### ✔ Optional: tool mode / eval mode / speech / multimodal

