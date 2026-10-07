def receive_line(reader):
    line = reader.readline()
    if not line:
        raise ConnectionError("Connection closed")
    return line.decode(errors="ignore").rstrip("\n")


def send_line(connection, message): 
    connection.sendall(f"{message}\n".encode())

