import os

from cryptography.fernet import Fernet


def fernet_encrypt(value: str) -> str:
    key = os.environ["FERNET_KEY"]
    return Fernet(key.encode()).encrypt(value.encode()).decode()
