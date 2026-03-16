import pandas as pd
import sys
import re
import ahocorasick

def CleaningPunct(df,columns):
    df = df.copy()
    df[columns]=df[columns].apply(lambda x: re.sub(r'[^\w\s]','',str(x)))
    return df[columns]

def FilterDatasetOnKeywords(df, columns, keywords):
    df = df.copy()

    # Ubah underscore jadi spasi dulu
    clean_keyword = keywords.lower().replace("_", " ")

    # Escape aman
    clean_keyword = re.escape(clean_keyword)

    # Ganti spasi jadi fleksibel (bisa spasi / underscore / tanpa spasi)
    clean_keyword = clean_keyword.replace(r"\ ", r"[\s_]*")

    pattern = r"\b" + clean_keyword + r"\b"

    print(f'Pattern: {pattern}')

    mask = df[columns].str.contains(pattern, case=False, na=False)

    return df[mask]

def normalize_text(text):
    if text is None:
        return ""
    
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
import ahocorasick

def build_brand_automaton(brand_list):

    A = ahocorasick.Automaton()

    for brand in brand_list:

        brand_clean = normalize_text(brand)

        if brand_clean:
            A.add_word(brand_clean, brand)

    A.make_automaton()

    return A

def extract_brand(text, automaton):
    matches = []
    
    for end_idx, original_brand in automaton.iter(text.lower()):
        start_idx = end_idx - len(original_brand) + 1
        
        # Validasi word boundary kiri
        left_ok = (start_idx == 0) or (not text[start_idx - 1].isalnum())
        # Validasi word boundary kanan
        right_ok = (end_idx == len(text) - 1) or (not text[end_idx + 1].isalnum())
        
        if left_ok and right_ok:
            matches.append(original_brand)
    
    if not matches:
        return "Tidak Ada Merek"
    
    # Ambil match yang paling panjang = paling spesifik
    return max(matches, key=len)