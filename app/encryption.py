from cryptography.fernet import Fernet, InvalidToken
from app.config import settings
import bcrypt

fernet = Fernet(settings.SECRET_KEY.encode())


def encrypt_secret(secret: str) -> str:
    return fernet.encrypt(secret.encode()).decode()


def decrypt_secret(encrypted: str) -> str:
    try:
        return fernet.decrypt(encrypted.encode()).decode()
    except InvalidToken:
        raise ValueError("Invalid or corrupted secret")


def hash_passphrase(passphrase: str) -> str:
    return bcrypt.hashpw(passphrase.encode(), bcrypt.gensalt()).decode()


def verify_passphrase(passphrase: str, hashed: str) -> bool:
    return bcrypt.checkpw(passphrase.encode(), hashed.encode())
