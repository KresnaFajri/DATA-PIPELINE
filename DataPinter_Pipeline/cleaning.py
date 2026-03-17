import pandas as pd
import sys
import re
from rapidfuzz import fuzz
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

def extract_brand(text, automaton,brand_list,fuzzy_threshold=80):
    matches = []
    text_lower = text.lower()

        # --- 1. Exact match via Aho-Corasick ---
    for end_idx, original_brand in automaton.iter(text_lower):
        start_idx = end_idx - len(original_brand) + 1

        left_ok = (start_idx == 0) or (not text_lower[start_idx - 1].isalnum())
        right_ok = (end_idx == len(text_lower) - 1) or (not text_lower[end_idx + 1].isalnum())

        if left_ok and right_ok:
            matches.append((original_brand, 100))
    
    if not matches:
        words = text_lower.split()
        for brand in brand_list:
            brand_lower = brand.lower().strip()

            for word in words:
                score=fuzz.ratio(word, brand_lower)
                if score >= fuzzy_threshold:
                    matches.append((brand,score))
                    break
            if len(brand_lower.split())>1:
                score = fuzz.partial_ratio(text_lower, brand_lower)
                if score >= fuzzy_threshold:
                    matches.append((brand,score))
    if not matches:
        return "Tidak Ada Merek"

    best_match = max(matches, key=lambda x:(x[1],len(x[0])))
    return best_match[0]