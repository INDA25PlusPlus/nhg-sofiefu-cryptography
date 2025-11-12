"""
Encrypt/decrypt and sign/verify data for client-server communication.
Intended for use by client before sending data to server, and after receiving data from server.
"""

# krypterar/dekrypt data med AES-GCM. signering/verifiering med HMAC

# all data ska krypteras av klienten innan den skickas till servern, med en nyckel härledd från ett lösenord och en slumpmässig nonce per kryptering*
# datan ska även vara signerad med samma nyckel och med fil-id:t, så att servern inte kan byta ut den mot annan slumpmässig data/en annan fil**

# kryptering: AES-GCM med 256-bitars nyckel
# signering: HMAC-SHA256
# KDF: make weak key strong key
# nonce: salt
# PBKDF2: hashing many times    

import os
from typing import Tuple
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, hmac # https://cryptography.io/en/latest/hazmat/primitives/mac/hmac/
from cryptography.hazmat.primitives.ciphers.aead import AESGCM # https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM
from cryptography.hazmat.backends import default_backend # needed for KDF and HMAC!!!

# Constants
SALT_LEN = 16        # salt/nonce for KDF
GCM_NONCE_LEN = 12   # AES-GCM recommended nonce
DERIVED_LEN = 64     # derive 64 bytes, split into 32+32
AES_KEY_LEN = 32     # 256-bit AES
HMAC_KEY_LEN = 32
HMAC_LEN = 32        # SHA256 output
KDF_ITERS = 200_000  

def generate_key_from_password(password: str, salt: bytes, iterations: int = KDF_ITERS) -> Tuple[bytes, bytes]:
    """
    Derive AES and HMAC keys from a password and a salt (random nonce).
    Returns (aes_key, hmac_key).
    """
    if not isinstance(salt, (bytes, bytearray)) or len(salt) < 8:
        raise ValueError("salt must be bytes and reasonably long (recommended 16 bytes)")
    password_bytes = password.encode("utf-8")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=DERIVED_LEN,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    material = kdf.derive(password_bytes)
    aes_key = material[:AES_KEY_LEN]
    hmac_key = material[AES_KEY_LEN:AES_KEY_LEN+HMAC_KEY_LEN]
    return aes_key, hmac_key

def sign_data(hmac_key: bytes, file_id: int, ciphertext: bytes) -> bytes:
    """
    Produce HMAC-SHA256 signature over file_id || ciphertext.
    file_id encoded as 3 big-endian bytes (matching server code).
    """
    file_id_bytes = file_id.to_bytes(3, "big")
    h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
    h.update(file_id_bytes)
    h.update(ciphertext)
    return h.finalize()

def verify_signature(hmac_key: bytes, file_id: int, ciphertext: bytes, signature: bytes) -> bool:
    """
    Verify HMAC-SHA256 signature. Returns True if valid, False otherwise.
    """
    file_id_bytes = file_id.to_bytes(3, "big")
    h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
    h.update(file_id_bytes)
    h.update(ciphertext)
    try:
        h.verify(signature)
        return True
    except Exception:
        return False

def encrypt_data(password: str, file_id: int, data: bytes) -> bytes:
    """
    Encrypt data with AES-GCM and sign it.
    Returns blob ready to send to server:
      salt(16) || gcm_nonce(12) || ciphertext_with_tag || signature(32)
    The AES-GCM uses file_id as associated data.
    """
    salt = os.urandom(SALT_LEN)
    aes_key, hmac_key = generate_key_from_password(password, salt)
    gcm_nonce = os.urandom(GCM_NONCE_LEN)
    aesgcm = AESGCM(aes_key)
    associated_data = file_id.to_bytes(3, "big") # associated data = not encrypted
    ciphertext_with_tag = aesgcm.encrypt(gcm_nonce, data, associated_data)
    signature = sign_data(hmac_key, file_id, ciphertext_with_tag)
    blob = salt + gcm_nonce + ciphertext_with_tag + signature
    return blob

def decrypt_data(password: str, file_id: int, blob: bytes) -> bytes:
    """
    Inverse of encrypt_data. Expects blob format:
      salt(16) || gcm_nonce(12) || ciphertext_with_tag || signature(32)
    Returns data bytes on success.
    Raises ValueError on malformed blob or signature/authentication failures.
    """
    if len(blob) < SALT_LEN + GCM_NONCE_LEN + HMAC_LEN + 1:
        raise ValueError("blob too short or malformed")
    salt = blob[:SALT_LEN]
    gcm_nonce = blob[SALT_LEN:SALT_LEN + GCM_NONCE_LEN]
    signature = blob[-HMAC_LEN:]
    ciphertext_with_tag = blob[SALT_LEN + GCM_NONCE_LEN:-HMAC_LEN]
    aes_key, hmac_key = generate_key_from_password(password, salt)

    if not verify_signature(hmac_key, file_id, ciphertext_with_tag, signature):
        raise ValueError("signature verification failed")

    aesgcm = AESGCM(aes_key)
    associated_data = file_id.to_bytes(3, "big")
    try:
        data = aesgcm.decrypt(gcm_nonce, ciphertext_with_tag, associated_data)
    except Exception as e:
        raise ValueError("AES-GCM decryption/authentication failed") from e
    return data

# eexample usage and test 
if __name__ == "__main__":
    pw = "ilikerats"
    fid = 42
    message = b"this is the secret file bytes"

    blob = encrypt_data(pw, fid, message)
    print("blob len:", len(blob))

    recovered = decrypt_data(pw, fid, blob)
    assert recovered == message
    print("decrypted matches original")

    # tamper test (should raise on verify or decrypt)
    try:
        tampered = bytearray(blob)
        tampered[SALT_LEN + GCM_NONCE_LEN + 5] ^= 1 # flip a bit in ciphertext area
        decrypt_data(pw, fid, bytes(tampered))
    except Exception as e:
        print("tamper detected:", type(e).__name__, e)
