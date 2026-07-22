# Grade 3 — LLM + RAG WebUI Submission

**Candidate:** Vinay Surtani
**Email:** surtanivinay@gmail.com

My implementation is in a **private repository**:
https://github.com/vinaysurtani/JSB_grade_3_interview_problem

I have invited **philipamadasun1@gmail.com** as a collaborator so you can access it.

## What it contains
- FastAPI backend + Streamlit WebUI — streaming (SSE) chat and RAG with cited sources
- RAG pipeline: chunk -> MiniLM embeddings -> numpy cosine retrieval (sources shown with doc/section/score)
- Session memory + SQLite persistence (survives a backend restart)
- `/stats` resource monitoring (process RSS / machine RAM / GPU), snapshot logged per turn
- Part B: `curl_tests.sh` (B1), TCP command channel with framing + reconnect (B2),
  UDP telemetry with loss tracking + `--drop` (B3), transport write-up (B4)
- Extra credit: MQTT with QoS/retained/Last Will (B5), memory-pressure edge cases —
  streamed export, backpressure, 413 (B6), live performance metrics, automatic RAG eval mode
- Walkthrough video in the repo (`video_recording_rag_chat.mp4`)
