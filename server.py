import socket
import threading
from node import Node

store = {}  # file_id -> data (bytes)

def handle_client(conn, root_node: Node):
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

                encrypted_file = blob[3:]
                
                path_hashes = []
                path_hashes.append(root_node.hash)
                root_node.update_leaf(file_id, encrypted_file, path_hashes)
                print("number of bytes of one hash:", len(path_hashes[0])) # check if its 32 byte

                return_message = b""
                for hash in path_hashes:
                    return_message += hash

                conn.sendall(return_message)

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

    n = 8 # fixed
    root_node = Node(0, 0, n-1) # create root node of merkle tree 

    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle_client, args=(conn, root_node), daemon=True).start()

if __name__ == "__main__":
    main()
