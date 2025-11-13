import socket
import client_help
from verify_update import verify_update, compute_hash

class Client:

    def __init__(self, host="127.0.0.1", port=9000):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.n = 8 # number of file_ids
        self.root_hash = b"" # the only hash saved by the client

    def put(self, password, file_id, data: bytes):
        """
        Sends encrypted and signed data to server. Returns True on success.
        """
        # get old file to verify update
        old_plain, old_raw_blob = self.get(password, file_id)
        if old_raw_blob is None:
            encrypted_old_file = b""
        else:
            encrypted_old_file = old_raw_blob
        print("ENCRYPTED OLD FILE", encrypted_old_file, len(encrypted_old_file))

        # update file
        header = bytes([1]) + file_id.to_bytes(3, "big")  # 1=put, 2=get
        encrypted_payload = client_help.encrypt_data(password, file_id, data)
        self.s.sendall(header + len(encrypted_payload).to_bytes(4, "big") + encrypted_payload)
        print("ENCRYPTED PAYLOAD", encrypted_payload)
        
        # we receive path_hashes for us to update our root_hash
        return_message = self.s.recv(128) 
        print("return message:", return_message)
        path_hashes = [return_message[i:i+32] for i in range(0, len(return_message), 32)] # consists of bytes
        print("length of path hashes", len(path_hashes), "length of one hash", len(path_hashes[0]))
        print("path hashes", path_hashes)
        
        new_hash = verify_update(file_id, path_hashes, self.root_hash, encrypted_old_file, encrypted_payload, self.n) 
        if new_hash == False:
            return False
        else: 
            self.root_hash = new_hash
            
        return True
    
    def get(self, password, file_id):
        """
        Retrieves encrypted data from server by file_id.
        Returns decrypted data bytes on success, or None if not found.
        """
        header = bytes([2]) + file_id.to_bytes(3, "big")
        self.s.sendall(header)
        resp = self.s.recv(2)
        if resp != b"OK":
            return None, None
        size = int.from_bytes(self.s.recv(4), "big")
        blob = self.s.recv(size)
        # decrypt for caller, but also return raw blob
        plaintext = client_help.decrypt_data(password, file_id, blob)
        return plaintext, blob

# file id can be 0-7 bc of merkle conditions (rn)
if __name__ == "__main__":
    #password = "ilikerats"
    message1 = b"rats like cheese"

    password = "ilikeicecream"
    message2 = b"sofie wants to be an icecream"

    c = Client()
    
    print("Putting data...")
    if not c.put(password, 0, message1): 
        print("Error: update error")
        exit(0)
    returned_message = c.get(password, 0)
    if returned_message == message1:
        print("Success! Retrieved matches original.")

    if not c.put(password, 0, message2): 
        print("Error: update error")
        exit(0)
    returned_message = c.get(password, 0)
    if returned_message == message2:
        print("Success! Retrieved matches original.")
    
    

