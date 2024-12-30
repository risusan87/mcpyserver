
import hashlib

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def gen_key_pair():
    private_key = rsa.generate_private_key(key_size=1024, public_exponent=65537)
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_key, public_key

def create_ciphers(shared_secret):
    encrypt_cipher = Cipher(
        algorithms.AES(shared_secret), modes.CFB8(shared_secret), backend=default_backend()
    ).encryptor()
    decrypt_cipher = Cipher(
        algorithms.AES(shared_secret), modes.CFB8(shared_secret), backend=default_backend()
    ).decryptor()
    return encrypt_cipher, decrypt_cipher

def auth_hash(server_id: str, shared_secret: bytes, server_public_key):
    sha1 = hashlib.sha1()
    sha1.update(server_id.encode('ascii'))
    sha1.update(shared_secret)
    sha1.update(server_public_key)
    return sha1.hexdigest()


def encrypt(data: bytes, public_key: bytes):
    public_key = serialization.load_der_public_key(public_key)
    return public_key.encrypt(data, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA1()),
        algorithm=hashes.SHA1(),
        label=None
    ))

def decrypt(data: bytes, private_key: rsa.RSAPrivateKey):
    return private_key.decrypt(data, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA1()),
        algorithm=hashes.SHA1(),
        label=None
    ))
