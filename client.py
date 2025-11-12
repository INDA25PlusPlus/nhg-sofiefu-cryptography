import socket
import client_help


class Client:
    def __init__(self, host="127.0.0.1", port=9000):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))

    def put(self, password, file_id, data: bytes):
        """
        Sends encrypted and signed data to server. Returns True on success.
        """
        header = bytes([1]) + file_id.to_bytes(3, "big")  # 1=put, 2=get
        encrypted_payload = client_help.encrypt_data(password, file_id, data)

        self.s.sendall(header + len(encrypted_payload).to_bytes(4, "big") + encrypted_payload)
        return self.s.recv(2) == b"OK"
    
    def get(self, file_id):
        """
        Retrieves encrypted data from server by file_id.
        Returns decrypted data bytes on success, or None if not found.
        """
        header = bytes([2]) + file_id.to_bytes(3, "big")    #1=put, 2=get
        self.s.sendall(header)
        resp = self.s.recv(2)
        if resp != b"OK":
            return None
        size = int.from_bytes(self.s.recv(4), "big")
        blob = self.s.recv(size)
        print("GET blob len:", len(blob))
        return client_help.decrypt_data("ilikerats", file_id, blob)

# file id can be 0-7 bc of merkle conditions (rn)
if __name__ == "__main__":
    password = "ilikerats"
    message = b"rats like cheese"

    c = Client()
    
    c.put(password, 1, message)
    returned_message = c.get(1)
    if returned_message == message:
        print("Success! Retrieved matches original.")
