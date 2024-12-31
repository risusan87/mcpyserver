
import hashlib

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def gen_rsa_key_pair(key_size=1024):
    private_key = rsa.generate_private_key(key_size=key_size, public_exponent=65537)
    public_key = private_key.public_key()
    return private_key, public_key

def encode_public_key_der(public_key: rsa.RSAPublicKey) -> bytes:
    der_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return der_bytes

def encode_public_key_pem(public_key: rsa.RSAPublicKey) -> bytes:
    pem_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem_bytes

def gen_ciphers(shared_secret):
    encrypt_cipher = Cipher(
        algorithms.AES(shared_secret), modes.CFB8(shared_secret), backend=default_backend()
    ).encryptor()
    decrypt_cipher = Cipher(
        algorithms.AES(shared_secret), modes.CFB8(shared_secret), backend=default_backend()
    ).decryptor()
    return encrypt_cipher, decrypt_cipher

def auth_hash(server_id: str, shared_secret: bytes, public_der: bytes) -> str:
    sha1 = hashlib.sha1()
    sha1.update(server_id.encode('utf-8'))
    sha1.update(shared_secret)
    sha1.update(public_der)
    big_int = int.from_bytes(sha1.digest(), byteorder='big', signed=True)
    return format(big_int, 'x')

def encrypt_rsa(data: bytes, public_key: rsa.RSAPublicKey) -> bytes:
    return public_key.encrypt(data, padding.PKCS1v15())

def decrypt_rsa(data: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    return private_key.decrypt(data, padding.PKCS1v15())
