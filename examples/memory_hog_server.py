"""Worked demo for B6: memory-pressure edge cases.

Run:
    python memory_hog_server.py
It prints its PID. In a second terminal, watch its memory:
    ./watch_mem.sh <pid>
Then, in a third terminal, run the experiments:

  1) Buffered vs streamed (watch RSS spike ~300 MB, then stay flat):
       curl -s -o /dev/null "http://127.0.0.1:5000/export_buffered?mb=300"
       curl -s -o /dev/null "http://127.0.0.1:5000/export_streamed?mb=300"

  2) Slow-consumer backpressure (RSS must stay flat the whole time):
       curl --limit-rate 5M -o /dev/null "http://127.0.0.1:5000/export_streamed?mb=30"

  3) Oversized request body -> 413, WITHOUT the server loading it:
       python3 -c "open('big.json','w').write('x' * (50*1024*1024))"
       curl -i -X POST http://127.0.0.1:5000/upload --data-binary @big.json

Notes:
  * mb is capped at 1024 on purpose. The lesson is the SHAPE of the memory
    curve, not how big a number you can type.
  * After the buffered request, RSS may not drop back down — Python's
    allocator keeps freed memory around. Restart the server between
    measurements if you want clean numbers.
"""

import os

from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# Any request body larger than this is rejected with 413 before being read.
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

# One megabyte of fake log lines, built once at startup.
_LINE = b'{"level": "INFO", "msg": "' + b"x" * 73 + b'"}\n'
ONE_MB = (_LINE * (1024 * 1024 // len(_LINE) + 1))[: 1024 * 1024]


def requested_mb():
    return min(int(request.args.get("mb", 100)), 1024)


@app.route("/export_buffered")
def export_buffered():
    mb = requested_mb()
    payload = ONE_MB * mb  # <-- the ENTIRE response exists in RAM right here
    return Response(payload, mimetype="text/plain")


@app.route("/export_streamed")
def export_streamed():
    mb = requested_mb()

    def generate():
        for _ in range(mb):
            yield ONE_MB   # <-- only ~1 MB is alive at any moment

    return Response(generate(), mimetype="text/plain")


@app.route("/upload", methods=["POST"])
def upload():
    # For oversized bodies Flask answers 413 from MAX_CONTENT_LENGTH and the
    # payload is never loaded; this handler only completes for small ones.
    data = request.get_data()
    return jsonify({"received_bytes": len(data)})


if __name__ == "__main__":
    pid = os.getpid()
    print(f"[server] PID {pid} — watch me with: ./watch_mem.sh {pid}")
    app.run(host="127.0.0.1", port=5000)
