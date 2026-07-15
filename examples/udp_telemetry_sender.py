"""Minimal UDP telemetry sender — the "robot" side of B3.

Run:      python udp_telemetry_sender.py [--drop 0.2]
Then run: python udp_telemetry_receiver.py   (in another terminal)

Sends fake pose/battery telemetry at 10 Hz. Note there is no connect, no
handshake, no ACK — sendto() just fires the datagram and moves on. If
nobody is listening, the packets vanish silently. That's UDP.

The --drop flag simulates a lossy network by randomly skipping sends.
IMPORTANT: seq still increments on skipped packets — that's what lets the
receiver detect the loss. Your robot_sim.py needs this same flag.
"""

import argparse
import json
import math
import random
import socket
import time

HOST = "127.0.0.1"
PORT = 9001
RATE_HZ = 10


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--drop", type=float, default=0.0,
                        help="probability of dropping each packet (0.0-1.0)")
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq = 0
    print(f"[robot] sending telemetry to {HOST}:{PORT} at {RATE_HZ} Hz "
          f"(drop={args.drop})")

    while True:
        t = time.time()
        packet = {
            "seq": seq,
            "x": round(2.0 * math.cos(t / 5), 3),   # drive in a circle
            "y": round(2.0 * math.sin(t / 5), 3),
            "heading": round((t * 20) % 360, 1),
            "battery": round(max(0.0, 100 - (t % 1000) / 10), 1),
            "t": t,
        }
        seq += 1  # increment even if we drop, so the receiver sees a gap

        if random.random() >= args.drop:
            sock.sendto(json.dumps(packet).encode(), (HOST, PORT))

        time.sleep(1.0 / RATE_HZ)


if __name__ == "__main__":
    main()
