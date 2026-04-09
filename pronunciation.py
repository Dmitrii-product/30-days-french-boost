"""
Pronunciation module for French words.
Provides phonetic pronunciation guide for French words.
"""

import json
import urllib.request
import os

# Dictionary of common French words with their phonetic pronunciations
PRONUNCIATION_DICT = {
    "bonjour": "[bon-zhoor]",
    "merci": "[mehr-see]",
    "oui": "[wee]",
    "non": "[nohn]",
    "s'il vous plaît": "[see voo pleh]",
    "chat": "[shah]",
    "chien": "[shee-ahn]",
    "eau": "[oh]",
    "café": "[ka-fay]",
    "pain": "[pahn]",
    "maison": "[meh-zohn]",
    "femme": "[fahm]",
    "homme": "[om]",
    "enfant": "[ahn-fahn]",
    "jour": "[zhoor]",
    "nuit": "[nwee]",
    "soleil": "[so-lay]",
    "lune": "[loon]",
    "amour": "[ah-moor]",
    "vie": "[vee]",
    "mort": "[mor]",
    "travail": "[trah-vye]",
    "école": "[ay-kol]",
    "livre": "[lee-vruh]",
    "arbre": "[ar-bruh]",
    "fleur": "[fluhr]",
    "beauté": "[boh-tay]",
    "ami": "[ah-mee]",
    "famille": "[fa-mee-yuh]",
    "père": "[pair]",
    "mère": "[mehr]",
    "fils": "[fees]",
    "fille": "[fee-yuh]",
    "frère": "[frehr]",
    "sœur": "[suhr]",
    "français": "[frahn-seh]",
    "anglais": "[ahn-gleh]",
    "espagnol": "[es-pah-nyol]",
    "allemand": "[al-mahn]",
    "italien": "[ee-tah-lyan]",
    "portugais": "[por-too-geh]",
    "merveilleux": "[mehr-vay-yuh]",
    "excellent": "[ek-sel-ahn]",
    "magnifique": "[mag-nee-feek]",
    "formidable": "[for-mee-dah-bluh]",
    "nouveau": "[noo-voh]",
    "ancien": "[ahn-syan]",
    "grand": "[grahn]",
    "petit": "[puh-tee]",
    "heureux": "[uh-ruh]",
    "triste": "[treest]",
}

def get_french_pronunciation(word: str) -> str:
    """
    Get phonetic pronunciation for a French word.
    First checks local dictionary, then generates phonetic approximation.
    
    Args:
        word: The word to get pronunciation for
        
    Returns:
        Phonetic pronunciation string
    """
    word_lower = word.lower().strip()
    
    # Check local dictionary first
    if word_lower in PRONUNCIATION_DICT:
        return PRONUNCIATION_DICT[word_lower]
    
    # Generate phonetic approximation for words not in dictionary
    phonetic = generate_french_phonetic(word_lower)
    PRONUNCIATION_DICT[word_lower] = phonetic
    return phonetic

def generate_french_phonetic(word: str) -> str:
    """
    Generate a phonetic approximation for French words.
    Uses common French pronunciation patterns.
    
    Args:
        word: The French word to generate pronunciation for
        
    Returns:
        Simple phonetic approximation in bracket notation
    """
    word_lower = word.lower()
    
    # Simple approximation: just put in brackets
    # More sophisticated rules could be added here
    phonetic = f"[{word_lower}]"
    
    return phonetic

def add_pronunciation_to_words_json(words_file: str = 'words.json'):
    """
    Add pronunciation field to all words in words.json if not already present.
    
    Args:
        words_file: Path to the words.json file
    """
    if not os.path.exists(words_file):
        print(f"File {words_file} not found")
        return
    
    with open(words_file, 'r', encoding='utf-8') as f:
        words_data = json.load(f)
    
    updated = False
    total = len(words_data)
    processed = 0
    
    for word_entry in words_data:
        if 'pronunciation' not in word_entry or not word_entry['pronunciation']:
            word = word_entry.get('word', '')
            pronunciation = get_french_pronunciation(word)
            if pronunciation:
                word_entry['pronunciation'] = pronunciation
                updated = True
                processed += 1
                if processed % 50 == 0:
                    print(f"Processed {processed}/{total} words...")
    
    if updated:
        with open(words_file, 'w', encoding='utf-8') as f:
            json.dump(words_data, f, ensure_ascii=False, indent=4)
        print(f"✓ Updated {words_file} with pronunciations ({processed} words added)")
    else:
        print("✓ All words already have pronunciations")

if __name__ == "__main__":
    add_pronunciation_to_words_json()
