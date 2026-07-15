"""Minimal UDP telemetry receiver — the "backend" side of B3.

Run udp_telemetry_sender.py first (try --drop 0.2), then this.

Tracks the latest packet and counts loss from gaps in the seq field.
In your real system this loop must NOT block your backend: run it in a
thread, an asyncio task, or a separate process, and share only the latest
telemetry + counters with your HTTP handlers.
"""

import json
import socket

HOST = "127.0.0.1"
PORT = 9001


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"[backend] listening for telemetry on {HOST}:{PORT}")

    received = 0
    lost = 0
    last_seq = None

    while True:
        data, addr = sock.recvfrom(4096)  # one recvfrom == one whole datagram
        pkt = json.loads(data)
        received += 1

        # A gap in seq means packets went missing. (A real system would also
        # handle out-of-order arrival — fine to ignore on localhost.)
        if last_seq is not None and pkt["seq"] > last_seq + 1:
            lost += pkt["seq"] - last_seq - 1
        last_seq = pkt["seq"]

        loss_pct = 100.0 * lost / (received + lost)
        print(f"\r[backend] pos=({pkt['x']:+.2f},{pkt['y']:+.2f}) "
              f"hdg={pkt['heading']:6.1f} bat={pkt['battery']:5.1f}% | "
              f"recv={received} lost={lost} loss={loss_pct:4.1f}%",
              end="", flush=True)


if __name__ == "__main__":
    main()
