# DoS Simulation

A small Python TCP simulation that demonstrates how a server behaves under a denial-of-service style flood and how normal client traffic is impacted when the service is under load.

This project is intended for learning and demonstration purposes only. It models a basic local service with a simple protocol and a flood/attack simulation.

## Overview

The project contains four files:

- `server.py` — runs the TCP server and enforces a small connection limit
- `client.py` — opens a normal client connection and sends text messages
- `attacker.py` — simulates a flood of requests from multiple concurrent connections
- `protocol.py` — shared helpers for sending and receiving newline-delimited messages

## How it works

The server listens on `127.0.0.1` and defaults to port `5000`.

Behavior:

- Up to `4` active client connections are accepted at once
- A flood attacker sends `FLOOD_START` to mark itself as malicious traffic
- Once a flood is active, normal requests are rejected with `SERVICE_UNAVAILABLE`
- The server logs connection activity, attacker traffic, and overload conditions

The attack simulator creates several threads, each opening its own connection to the server and sending flood messages repeatedly for a short period.

## Prerequisites

- Python 3.8+
- A terminal or shell environment to run multiple processes

## Quick start

### 1) Start the server

```bash
python3 server.py
```

You should see output similar to:

```text
[SERVER] Listening on 127.0.0.1:5000 (max clients=4)
```

### 2) Start a normal client

Open a second terminal and run:

```bash
python3 client.py
```

The client will connect and then prompt for messages:

```text
Enter message (type 'exit' to quit):
```

Try sending a few normal messages like:

```text
hello
status
test
```

The server will reply with:

```text
Echo: hello
```

### 3) Simulate a flood attack

Open a third terminal and run:

```bash
python3 attacker.py
```

This starts multiple simulated connections and attempts to overwhelm the server. During the attack, the regular client will likely receive:

```text
Service unavailable
```

That is the expected overload behavior in this simulation.

## Environment variables

You can change the port used by the project with:

```bash
export DOS_SIMULATION_PORT=5001
python3 server.py
```

Then run the client and attacker in the same environment or set the variable before each command.

## Example workflow

```bash
# Terminal 1
python3 server.py

# Terminal 2
python3 client.py

# Terminal 3
python3 attacker.py
```

## Project notes

- The server is intentionally simple and local-only.
- It uses newline-delimited messages over TCP sockets.
- It demonstrates connection exhaustion and service denial in a controlled environment.
- This is not a real-world DoS defense implementation; it is a teaching simulation.

## License

This project is provided for educational use. Add a license file if you plan to share or publish it publicly.

## Suggested improvements

- Add a proper README badge and project screenshot
- Add command-line arguments instead of hard-coded host/port values
- Add logging to files for easier debugging
- Add a more realistic queue or rate-limiting model
- Convert the simulation into a small web dashboard or GUI
