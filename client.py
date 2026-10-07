import os
import socket

from protocol import receive_line, send_line

HOST = "127.0.0.1"
PORT = int(os.environ.get("DOS_SIMULATION_PORT", "5000"))
SOCKET_TIMEOUT = 2


def start_client():
    try:
        with socket.create_connection((HOST, PORT), timeout=SOCKET_TIMEOUT) as client:
            with client.makefile("rb") as reader:
                if receive_line(reader) != "READY":
                    print("Service unavailable")
                    return

                print(f"[CLIENT] Connected to {HOST}:{PORT}")
                while True:
                    message = input("Enter message (type 'exit' to quit): ")
                    if message.lower() == "exit":
                        break

                    try:
                        send_line(client, message)
                        response = receive_line(reader)
                    except OSError:
                        print("Service unavailable")
                        break

                    if response == "SERVICE_UNAVAILABLE":
                        print("Service unavailable")
                        continue

                    print("Sent")
                    print(f"[SERVER RESPONSE] {response}")
    except OSError:
        print("Service unavailable")


if __name__ == "__main__":
    start_client()