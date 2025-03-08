from cryptography.fernet import Fernet
import os

key = os.environ.get('KEY')
cipher_suite = Fernet(key)

def encrypt(data):
    encoded_data = data.encode("utf-8")
    encrypted_data = cipher_suite.encrypt(encoded_data)
    return encrypted_data

def decrypt(encrypted_data):
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    return decrypted_data.decode("utf-8")