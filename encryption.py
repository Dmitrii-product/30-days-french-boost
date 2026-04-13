import os
from cryptography.fernet import Fernet
import hashlib
from dotenv import load_dotenv

load_dotenv()

def get_cipher() -> Fernet:
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        raise RuntimeError("ENCRYPTION_KEY is not set in environment variables.")
    try:
        return Fernet(key.encode())
    except Exception as e:
        raise RuntimeError(f"ENCRYPTION_KEY is invalid: {e}") from e

def ensure_encryption_ready():
    get_cipher()

def generate_key():
    return Fernet.generate_key().decode()

def encrypt_id(chat_id: int) -> str:
    return get_cipher().encrypt(str(chat_id).encode()).decode()

def decrypt_id(encrypted_text: str) -> int:
    decrypted = get_cipher().decrypt(encrypted_text.encode()).decode()
    return int(decrypted)

def hash_id(chat_id: int) -> str:
    """Creates a deterministic hash of the chat_id for database correlation without exposing the real ID."""
    return hashlib.sha256(str(chat_id).encode()).hexdigest()
