"""Client-side half of the B6 lesson: requests without vs with stream=True.

requests.get(url) downloads the ENTIRE response into memory (r.content)
before your code sees any of it. stream=True + iter_content() handles it a
chunk at a time. Same buffered-vs-streamed story as the server side, seen
from the other end of the wire.

Run memory_hog_server.py first, then:
    python3 requests_stream_demo.py buffered
    python3 requests_stream_demo.py streamed

(Uses the `resource` module: macOS/Linux only. On Windows, watch the
python process in Task Manager or with Get-Process instead.)
"""

import platform
import resource
import sys

import requests

URL = "http://127.0.0.1:5000/export_streamed?mb=300"


def peak_rss_mb():
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Cross-platform gotcha: ru_maxrss is KILOBYTES on Linux, BYTES on macOS.
    return peak / (1024 * 1024) if platform.system() == "Darwin" else peak / 1024


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "buffered"

    if mode == "buffered":
        r = requests.get(URL)                      # whole body -> r.content
        total = len(r.content)
    else:
        total = 0
        with requests.get(URL, stream=True) as r:  # nothing downloaded yet
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                total += len(chunk)                # handle 1 MB, then drop it

    print(f"{mode}: received {total / (1024 * 1024):.0f} MB, "
          f"peak RSS {peak_rss_mb():.0f} MB")


if __name__ == "__main__":
    main()
