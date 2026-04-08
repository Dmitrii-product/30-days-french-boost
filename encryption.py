import os
from cryptography.fernet import Fernet
import hashlib
from dotenv import load_dotenv

load_dotenv()

key = os.environ.get('ENCRYPTION_KEY')
fernet = Fernet(key.encode()) if key else None

def generate_key():
    return Fernet.generate_key().decode()

def encrypt_id(chat_id: int) -> str:
    if not fernet:
        return str(chat_id)
    return fernet.encrypt(str(chat_id).encode()).decode()

def decrypt_id(encrypted_text: str) -> int:
    if not fernet:
        try:
            return int(encrypted_text)
        except ValueError:
            return 0
    try:
        decrypted = fernet.decrypt(encrypted_text.encode()).decode()
        return int(decrypted)
    except Exception as e:
        print(f"Error decrypting ID: {e}")
        return 0

def hash_id(chat_id: int) -> str:
    """Creates a deterministic hash of the chat_id for database correlation without exposing the real ID."""
    return hashlib.sha256(str(chat_id).encode()).hexdigest()
