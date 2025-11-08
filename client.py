import socket

class Client:
    def __init__(self, host="127.0.0.1", port=9000):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))

    # sends an ID and raw bytes to the server. Server stores them in RAM.
    def put(self, file_id, data: bytes):
        header = bytes([1]) + file_id.to_bytes(3, "big")
        payload = len(data).to_bytes(4, "big") + data
        self.s.sendall(header + payload)
        return self.s.recv(2) == b"OK"

    # retrieves raw bytes from the server by ID. Returns None if not found. 
    def get(self, file_id):
        header = bytes([2]) + file_id.to_bytes(3, "big")
        self.s.sendall(header)
        resp = self.s.recv(2)
        if resp != b"OK":
            return None
        size = int.from_bytes(self.s.recv(4), "big")
        return self.s.recv(size)

if __name__ == "__main__":
    c = Client()
    c.put(1, b"hello")
    print(c.get(1))
