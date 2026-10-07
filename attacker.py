import os
import socket
import threading
import time

from server import MAX_ACTIVE_CLIENTS, PROCESSING_DELAY
from protocol import receive_line, send_line

HOST = "127.0.0.1"
PORT = int(os.environ.get("DOS_SIMULATION_PORT", "5000"))

SIMULATED_CONNECTIONS = max(MAX_ACTIVE_CLIENTS - 1, 1)
HOLD_SECONDS = 15
FLOOD_INTERVAL = PROCESSING_DELAY


def send_flood(worker_id, message_counts):
    try:
        with socket.create_connection((HOST, PORT), timeout=2) as client:
            with client.makefile("rb") as reader:
                if receive_line(reader) != "READY":
                    raise ConnectionError("Server did not accept the simulation connection")

                send_line(client, f"FLOOD_START {worker_id}")
                if receive_line(reader) != "FLOOD_STARTED":
                    raise ConnectionError("Server did not start the flood simulation")

            print(f"[SIMULATION] Sender {worker_id} flooding localhost for {HOLD_SECONDS}s")
            deadline = time.monotonic() + HOLD_SECONDS
            message_number = 0
            while time.monotonic() < deadline:
                send_line(client, f"FLOOD {worker_id} {message_number}")
                message_number += 1
                time.sleep(FLOOD_INTERVAL)

            message_counts[worker_id] = message_number
    except OSError as error:
        message_counts[worker_id] = -1
        print(f"[SIMULATION] Sender {worker_id} failed: {error}")


def attack():
    print(f"[SIMULATION] Local request flood at {HOST}:{PORT}")
    print(f"[SIMULATION] Sending from {SIMULATED_CONNECTIONS} connections for {HOLD_SECONDS}s")
    print("[SIMULATION] Keep one client.py session connected and retry during the simulation.")

    message_counts = [0] * SIMULATED_CONNECTIONS
    threads = [
        threading.Thread(target=send_flood, args=(worker_id, message_counts))
        for worker_id in range(SIMULATED_CONNECTIONS)
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    accepted = sum(count >= 0 for count in message_counts)
    messages = sum(max(count, 0) for count in message_counts)
    errors = sum(count < 0 for count in message_counts)
    print(
        f"[SIMULATION] Finished: {accepted} accepted, "
        f"{messages} flood messages sent, {errors} connection errors"
    )


if __name__ == "__main__":
    attack()
