import os
from typing import Optional, List, Tuple
from supabase import create_client, Client
from encryption import encrypt_id, decrypt_id, hash_id
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

supabase: Optional[Client] = None
if url and key:
    supabase = create_client(url, key)
else:
    print(
        "Warning: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY "
        "(fallback SUPABASE_KEY) not set. DB functions will silently fail."
    )

def init_db():
    pass

def add_or_update_user(chat_id: int, level: str):
    if not supabase: return
    id_hash = hash_id(chat_id)
    encrypted_id = encrypt_id(chat_id)
    try:
        supabase.table('users').upsert({"id_hash": id_hash, "encrypted_id": encrypted_id, "level": level}).execute()
    except Exception as e:
        print(f"Error adding user to DB: {e}")

def get_user_level(chat_id: int) -> Optional[str]:
    if not supabase: return None
    id_hash = hash_id(chat_id)
    try:
        response = supabase.table('users').select('level').eq('id_hash', id_hash).execute()
        if response.data:
            return response.data[0]['level']
    except Exception as e:
        print(f"Error getting user level: {e}")
    return None

def get_all_users() -> List[Tuple[int, str]]:
    if not supabase: return []
    try:
        response = supabase.table('users').select('encrypted_id, level').execute()
        users = []
        for row in response.data:
            enc_id = row['encrypted_id']
            lvl = row['level']
            real_id = decrypt_id(enc_id)
            if real_id:
                users.append((real_id, lvl))
        return users
    except Exception as e:
        print(f"Error fetching all users: {e}")
        return []

def add_word_to_vocabulary(chat_id: int, word: str):
    if not supabase: return
    id_hash = hash_id(chat_id)
    try:
        supabase.table('vocabulary').upsert({
            "user_hash": id_hash,
            "word": word,
            "is_learned": True
        }).execute()
    except Exception as e:
        print(f"Error adding word to vocabulary: {e}")

def get_golden_list(chat_id: int):
    if not supabase: return [], []
    id_hash = hash_id(chat_id)
    import datetime
    try:
        response = supabase.table('vocabulary').select('*').eq('user_hash', id_hash).execute()
        recent_words = []
        unlearned_words = []
        now = datetime.datetime.now(datetime.timezone.utc)
        two_weeks = datetime.timedelta(days=14)
        for row in response.data:
            added_at_str = row.get('added_at', '')
            if added_at_str:
                added_at = datetime.datetime.fromisoformat(added_at_str.replace('Z', '+00:00'))
                is_recent = (now - added_at) <= two_weeks
            else:
                is_recent = False
            
            is_learned = row.get('is_learned', True)
            word = row.get('word', '')
            
            if is_recent:
                recent_words.append((word, is_learned))
            if not is_learned and not is_recent:
                unlearned_words.append((word, is_learned))
        return recent_words, unlearned_words
    except Exception as e:
        print(f"Error fetching golden list: {e}")
        return [], []

def update_word_status(chat_id: int, word: str, is_learned: bool):
    if not supabase: return
    id_hash = hash_id(chat_id)
    try:
        supabase.table('vocabulary').update({'is_learned': is_learned}).eq('user_hash', id_hash).eq('word', word).execute()
    except Exception as e:
        print(f"Error updating word status: {e}")

def get_word_status(chat_id: int, word: str) -> Optional[bool]:
    if not supabase: return None
    id_hash = hash_id(chat_id)
    try:
        response = supabase.table('vocabulary').select('is_learned').eq('user_hash', id_hash).eq('word', word).execute()
        if response.data:
            return response.data[0].get('is_learned')
    except Exception as e:
        print(f"Error getting word status: {e}")
    return None
