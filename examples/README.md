# Starter examples — what each one is for

Every file here shows the **mechanics** of one part of the assignment.
Read it, run it, then adapt it into your own system. Copy-pasting a file
unmodified will not satisfy the requirement it supports — the requirement
is always bigger than the example.

## Quick index (by requirement)

| File | Supports | Run it |
| ---- | -------- | ------ |
| `ollama_stream.py` | LLM API integration, `/chat`, `/stream` (streaming) | `python ollama_stream.py` (needs `ollama serve`) |
| `rag_minimal.py` | RAG pipeline: chunk → embed → retrieve → cite | `python rag_minimal.py --k 2` |
| `system_stats.py` | Resource monitoring, `GET /stats` (RAM + VRAM) | `python system_stats.py --watch` |
| `curl_cheatsheet.md` | B1 — HTTP fluency with curl | (read it) |
| `tcp_command_server.py` / `tcp_command_client.py` | B2 — TCP command channel, framing | run the server, then the client |
| `udp_telemetry_sender.py` / `udp_telemetry_receiver.py` | B3 — UDP telemetry, seq-based loss | `sender.py --drop 0.2` + `receiver.py` |
| `mqtt_example.py` | B5 (extra credit) — MQTT, QoS, retained + Last Will | `python mqtt_example.py` (needs a broker) |
| `memory_hog_server.py` | B6 (extra credit) — buffered vs streamed, 413 | `python memory_hog_server.py` |
| `requests_stream_demo.py` | B6.4 — client-side `stream=True` | `python requests_stream_demo.py streamed` |
| `watch_mem.sh` | watch any process's RSS from a second terminal | `./watch_mem.sh <pid>` |

The two top-level files `flask_app.py` + `streamlit_app.py` are a separate
minimal demo of getting terminal text onto a Streamlit UI — a starting
point for the WebUI, not a backend you should ship as-is.

## Install

```
pip install -r examples/requirements.txt
```

(Plus `ollama` running locally for `ollama_stream.py`, and a Mosquitto
broker for `mqtt_example.py`.)
