# curl cheatsheet (for B1)

Everything your browser or `requests` does, curl can do — and it shows you
what's actually on the wire. These examples assume a backend on
`localhost:5000`; adjust to your ports/routes.

## The basics

```bash
# Simple GET (prints the response body)
curl http://localhost:5000/health

# Just the HTTP status code, nothing else
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/health

# Show response headers too
curl -i http://localhost:5000/health

# Show EVERYTHING — request headers, response headers, TLS, the works.
# Lines starting with '>' are what curl SENT, '<' is what came BACK.
curl -v http://localhost:5000/health
```

## POSTing JSON

```bash
curl -X POST http://localhost:5000/chat \
     -H "Content-Type: application/json" \
     -d '{"session_id": "abc123", "message": "What is RAG?"}'

# Pretty-print the JSON response (needs jq: apt/brew install jq)
curl -s -X POST http://localhost:5000/chat \
     -H "Content-Type: application/json" \
     -d '{"session_id": "abc123", "message": "What is RAG?"}' | jq
```

## Streaming

```bash
# -N disables curl's output buffering. Without it, curl may sit on the
# data and dump it in chunks — with it, you see tokens as they arrive.
curl -N http://localhost:5000/stream?prompt=hello
```

## Breaking things on purpose (your backend should survive all of these)

```bash
# Malformed JSON body — expect a 400, not a 500 or a stack trace
curl -i -X POST http://localhost:5000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "oops'

# Wrong content type
curl -i -X POST http://localhost:5000/chat -d 'just some text'

# Route that doesn't exist — expect a 404
curl -i http://localhost:5000/does_not_exist
```

## Handy flags reference

| Flag | What it does |
| ---- | ------------ |
| `-s` | silent (no progress bar) |
| `-i` | include response headers in output |
| `-v` | verbose: show the full request/response exchange |
| `-N` | no output buffering (needed for streaming) |
| `-X` | HTTP method (`-X POST`, `-X DELETE`, ...) |
| `-H` | add a request header |
| `-d` | request body (implies POST) |
| `-o` | write body to a file (`-o /dev/null` to discard) |
| `-w` | print info after transfer (`%{http_code}`, `%{time_total}`, ...) |
