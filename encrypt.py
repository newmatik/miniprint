from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from base64 import b64encode
import os

def encrypt_aes(input_string, key):
    # Convert key to bytes and ensure it's 32 bytes (256 bits) for AES-256
    key_bytes = key.encode('utf-8').ljust(32, b'\0')[:32]
    iv = os.urandom(16)  # Generate a random IV
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=backend)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(input_string.encode()) + padder.finalize()
    
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_data) + encryptor.finalize()
    
    # Return the IV and encrypted data encoded in base64 to ensure it can be transported easily
    return b64encode(iv + ct).decode('utf-8')

# Example usage
key = "my_secret_key"
encrypted_message = encrypt_aes("token dfd354ca965f0e4:2b0c64580af2ede", key)
print("Encrypted:", encrypted_message)