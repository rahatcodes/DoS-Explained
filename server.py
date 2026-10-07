import os
import socket
import threading
import time

from protocol import receive_line, send_line

HOST = "127.0.0.1"
PORT = int(os.environ.get("DOS_SIMULATION_PORT", "5000"))

MAX_ACTIVE_CLIENTS = 4
LISTEN_BACKLOG = MAX_ACTIVE_CLIENTS
PROCESSING_DELAY = 0.05

active_clients = 0
active_attackers = 0
lock = threading.Lock()
client_slots = threading.BoundedSemaphore(MAX_ACTIVE_CLIENTS)


def handle_client(conn, addr):
    global active_clients, active_attackers
    is_attacker = False
    attacker_messages = 0
    with lock:
        active_clients += 1
        print(f"[SERVER] New connection from {addr} (active clients: {active_clients})")

    try:
        send_line(conn, "READY")
        with conn.makefile("rb") as reader:
            while True:
                message = receive_line(reader)

                if message.startswith("FLOOD_START "):
                    is_attacker = True
                    with lock:
                        active_attackers += 1
                    print(f"[SERVER] Flood traffic started from {addr}")
                    send_line(conn, "FLOOD_STARTED")
                    continue

                if is_attacker:
                    attacker_messages += 1
                    if attacker_messages == 1 or attacker_messages % 50 == 0:
                        print(f"[SERVER] Flood requests from {addr}: {attacker_messages}")
                    time.sleep(PROCESSING_DELAY)
                    continue

                with lock:
                    overloaded = active_attackers > 0
                if overloaded:
                    print(f"[SERVER] Rejected request from {addr}: service unavailable")
                    send_line(conn, "SERVICE_UNAVAILABLE")
                    continue

                print(f"[SERVER] Received from {addr}: {message}")
                time.sleep(PROCESSING_DELAY)
                send_line(conn, f"Echo: {message}")
    except OSError:
        pass
    finally:
        with lock:
            active_clients -= 1
            if is_attacker:
                active_attackers -= 1
            print(f"[SERVER] Connection closed {addr} (active clients: {active_clients})")
        if is_attacker:
            print(f"[SERVER] Flood connection from {addr} processed {attacker_messages} requests")
        conn.close()
        client_slots.release()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(LISTEN_BACKLOG)

    print(f"[SERVER] Listening on {HOST}:{PORT} (max clients={MAX_ACTIVE_CLIENTS})")

    while True:
        conn, addr = server.accept()
        if not client_slots.acquire(blocking=False):
            try:
                send_line(conn, "SERVICE_UNAVAILABLE")
            except OSError:
                pass
            conn.close()
            print(f"[SERVER] Refused {addr}: capacity reached")
            continue

        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()


if __name__ == "__main__":
    start_server()
