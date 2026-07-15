"""Minimal streaming chat client for an Ollama server — starter for the
required /chat and /stream endpoints.

Ollama speaks two streaming flavors; this uses the native one
(`/api/chat`), which streams one JSON object per line (NDJSON) until a
final object with `"done": true`. Each object's `message.content` is the
next token-chunk — exactly what you want to forward to a streaming UI.

Run (needs an `ollama serve` running locally):
    python ollama_stream.py
    python ollama_stream.py --model gemma3 --prompt "What is RAG in 2 lines?"

Wire it into your backend along these lines:

    @app.route("/stream")
    def stream():
        def gen():
            for chunk in chat_stream(prompt, model):
                yield f"data: {json.dumps({'token': chunk})}\n\n"  # SSE
            yield "data: [DONE]\n\n"
        return Response(gen(), mimetype="text/event-stream")

Two lessons this file ties together:
  * stream=True on the requests side mirrors B6.4 — don't buffer the whole
    reply in your backend's RAM before forwarding it.
  * the UI side then consumes that SSE stream token-by-token (see the curl
    `-N` test in B1.3). If your framework buffers the generator, the whole
    point is lost.

Needs: pip install requests
"""

import argparse
import json
import sys

import requests

OLLAMA_URL = "http://localhost:11434"


def chat_stream(prompt, model="tinyllama"):
    """Yield token chunks as they arrive from Ollama's /api/chat."""
    resp = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        },
        stream=True,                 # the requests-side half of B6.4
        timeout=60,
    )
    resp.raise_for_status()

    for raw in resp.iter_lines(decode_unicode=True):
        if not raw:
            continue
        msg = json.loads(raw)
        if chunk := msg.get("message", {}).get("content", ""):
            yield chunk
        if msg.get("done"):
            return


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="gemma3",
                   help="any model from `ollama list` (tinyllama, gemma3, ...)")
    p.add_argument("--prompt", default="Explain retrieval-augmented "
                                        "generation in two short sentences.")
    args = p.parse_args()

    print(f"[stream] model={args.model}\n[stream] reply: ", end="", flush=True)
    try:
        for chunk in chat_stream(args.prompt, args.model):
            sys.stdout.write(chunk)
            sys.stdout.flush()        # token-by-token, like curl -N
    except requests.ConnectionError:
        sys.exit(f"\n[stream] could not reach ollama at {OLLAMA_URL} — "
                 f"is `ollama serve` running?")
    print("\n[stream] done.")


if __name__ == "__main__":
    main()
