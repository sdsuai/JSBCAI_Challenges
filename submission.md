# Grade 2 LLM + RAG WebUI — submission

- **GitHub:** isiahmello24-beep
- **Email:** iluna0855@sdsu.edu
- **Private repo (code + README; walkthrough video to be added):** https://github.com/isiahmello24-beep/JSB_grade_2_interview_problem
- philipamadasun1@gmail.com has been invited as a collaborator on the private repo.

## What's inside

- FastAPI backend: `/chat`, `/rag`, `/tool` (blocking), `/stream` (Server-Sent Events), `/health`, sessions, `/eval`
- Streamlit WebUI: Chat / RAG / Tool modes, styled user vs AI bubbles, token-by-token streaming, model + mode + session ID shown, sources with page numbers under RAG answers, mode filter, session picker
- RAG pipeline: PDFs → ~500-char chunks with doc + page metadata → `all-MiniLM-L6-v2` embeddings → numpy cosine store (cached) → top-k → cited answer
- SQLite persistence of every turn (timestamp, mode, prompt, response, chunks, metrics, session ID) with reload of the last N turns and multi-session support
- `config.yaml` + `.env` overrides, `run.sh`, unit tests
- Extra credit: Tool mode with JSON validation, `/eval` (RAG accuracy + retrieval accuracy), performance metrics (TTFT, total time, tokens/s, retrieval and indexing time)
