"""Minimal TCP command server — the "robot" side of the B2 command channel.

Run:      python tcp_command_server.py
Then run: python tcp_command_client.py   (in another terminal)

Protocol: newline-delimited JSON. One command per line, one ACK per line.

The important part of this file is recv_lines(): TCP gives you a BYTE
STREAM, not messages. One send() on the client does not equal one recv()
here. You must buffer and split on '\n' yourself. This example does that
correctly — your real robot_sim.py must too (and must pass the
byte-at-a-time test described in the README).
"""

import json
import socket

HOST = "127.0.0.1"
PORT = 9000


def recv_lines(conn, buffer):
    """Read from the socket, return (complete_lines, leftover_buffer).

    recv() may return half a message, or three messages at once.
    Everything after the last '\n' is an incomplete message — keep it
    in the buffer for next time.
    """
    data = conn.recv(4096)
    if not data:                      # empty bytes == peer closed the connection
        return None, buffer
    buffer += data
    *lines, buffer = buffer.split(b"\n")
    return lines, buffer


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Without SO_REUSEADDR, restarting the server within ~60s of a previous
    # run fails with "Address already in use". Look up TIME_WAIT to see why.
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(1)
    print(f"[robot] listening on {HOST}:{PORT}")

    while True:  # accept loop: when a client disconnects, wait for the next one
        conn, addr = srv.accept()
        print(f"[robot] client connected from {addr}")
        buffer = b""
        try:
            while True:
                lines, buffer = recv_lines(conn, buffer)
                if lines is None:
                    print("[robot] client disconnected")
                    break
                for line in lines:
                    if not line.strip():
                        continue
                    cmd = json.loads(line)
                    print(f"[robot] got command: {cmd}")
                    ack = {"id": cmd.get("id"), "status": "ok",
                           "detail": f"executing {cmd.get('action')}"}
                    conn.sendall((json.dumps(ack) + "\n").encode())
        except (ConnectionResetError, BrokenPipeError):
            print("[robot] connection lost")
        finally:
            conn.close()


if __name__ == "__main__":
    main()
