import socket
import verify_update

class Client:
    def __init__(self, host="127.0.0.1", port=9000):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))

    # sends updated,encypted file in raw bytes to server. Server stores them in RAM.
    def update(self, file_id, data: bytes):
        header = bytes([1]) + file_id.to_bytes(3, "big")
        payload = len(data).to_bytes(4, "big") + data
        # todo: encrypt and sign before sending
        self.s.sendall(header + payload)

        # server should send back path_nodes for us to update root_hash
        path_nodes = self.s.recv() # todo: should i put anything inside recv()
        if not update_root_hash(file_id, path_nodes):
            print("Error")
            exit(0) # or whatever else we want to do
        
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

n = 8 # number of file_ids
root_hash = "" # the only hash saved by the client
if __name__ == "__main__":
    c = Client()
    c.update(1, b"hello")
    print(c.get(1))
