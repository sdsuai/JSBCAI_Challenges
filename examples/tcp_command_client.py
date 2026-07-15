"""Minimal TCP command client — the "backend" side of the B2 command channel.

Run tcp_command_server.py first, then this. Sends a few commands and reads
the ACKs. Note the same buffering discipline as the server: we can't assume
one recv() returns exactly one ACK.

Also try this (the framing torture test the README requires your robot to
survive): uncomment the byte-at-a-time send at the bottom. If your server
splits messages on '\n' correctly, it works exactly the same.
"""

import json
import socket

HOST = "127.0.0.1"
PORT = 9000


def recv_line(sock, buffer):
    """Block until a full '\n'-terminated line is buffered, return (line, buffer)."""
    while b"\n" not in buffer:
        data = sock.recv(4096)
        if not data:
            raise ConnectionError("server closed connection")
        buffer += data
    line, _, buffer = buffer.partition(b"\n")
    return line, buffer


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    buffer = b""

    commands = [
        {"id": 1, "action": "move_to", "params": {"x": 0.4, "y": 1.1}},
        {"id": 2, "action": "rotate", "params": {"deg": 90}},
        {"id": 3, "action": "stop", "params": {}},
    ]

    for cmd in commands:
        sock.sendall((json.dumps(cmd) + "\n").encode())
        line, buffer = recv_line(sock, buffer)
        ack = json.loads(line)
        assert ack["id"] == cmd["id"], "ACK id mismatch!"
        print(f"[backend] sent {cmd['action']!r:12} -> ack: {ack}")

    # --- framing torture test: send a command one byte at a time -----------
    # cmd = json.dumps({"id": 99, "action": "ping", "params": {}}) + "\n"
    # for byte in cmd.encode():
    #     sock.sendall(bytes([byte]))
    # line, buffer = recv_line(sock, buffer)
    # print(f"[backend] byte-at-a-time ack: {json.loads(line)}")

    sock.close()


if __name__ == "__main__":
    main()
