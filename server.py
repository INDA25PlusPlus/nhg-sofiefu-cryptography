import socket
import threading

store = {}  # file_id -> data (bytes)

def handle_client(conn):
    try:
        while True:
            header = conn.recv(4)
            if not header:
                break
            op = header[0]      # 1=put, 2=get
            file_id = int.from_bytes(header[1:4], "big")

            if op == 1:  # PUT
                size = int.from_bytes(conn.recv(4), "big")
                blob = recv_all(conn, size)
                print("SERVER got blob len:", len(blob))
                store[file_id] = blob
                conn.sendall(b"OK")

            elif op == 2:  # GET
                data = store.get(file_id, None)
                if data is None:
                    conn.sendall(b"NO")
                else:
                    conn.sendall(b"OK" + len(data).to_bytes(4, "big") + data)

    finally:
        conn.close()

def recv_all(conn, size):
    """
    Receive exactly size bytes from conn.
    (Otherwise it does not always retrieve full blob).
    """
    buf = b""
    while len(buf) < size:
        chunk = conn.recv(size - len(buf))
        if not chunk:
            raise ConnectionError("Connection closed early")
        buf += chunk
    return buf

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 9000))
    s.listen()
    print("Server listening on port 9000")

    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    main()
