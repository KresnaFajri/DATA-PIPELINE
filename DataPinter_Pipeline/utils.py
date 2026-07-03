import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import psycopg2
import duckdb
from pathlib import Path
from rapidfuzz import fuzz, process
import ahocorasick
from config import AutomatePipelineConfig
from flashtext import KeywordProcessor
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pendulum
from pathlib import Path
import json
import platform

#For Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

SERVICE_ACCOUNT_FILE = AutomatePipelineConfig.GCAL_CRED

CALENDAR_ID = "analystnose@gmail.com"

def connect_to_bpom():
    IS_WSL = (platform.system() == "Linux" and "microsoft" in platform.uname().release.lower())
    if IS_WSL:
        conn = psycopg2.connect(
            dbname=AutomatePipelineConfig.DBNAME,
            host =AutomatePipelineConfig.HOST_LINUX,
            password=AutomatePipelineConfig.PASSWORD,
            user = 'postgres',
            port='5432')
    else:
        conn = psycopg2.connect(
            dbname=AutomatePipelineConfig.DBNAME,
            host ='localhost',
            password=AutomatePipelineConfig.PASSWORD,
            user='postgres',
            port='5432'
        )
    return conn

def CleaningPunct(df,columns):
    df = df.copy()
    df[columns]=df[columns].apply(lambda x: re.sub(r'[^\w\s]','',str(x)))
    return df[columns]

def FilterDatasetOnKeywords(df, columns, keywords, additional_keywords=None):
    df = df.copy()

    def build_pattern(kw):
        clean = kw.lower().replace("_", " ")
        clean = re.escape(clean)
        clean = clean.replace(r"\ ", r"[\s_]+")
        return clean

    # Pattern dari keyword utama (nama file)
    all_patterns = [build_pattern(keywords)]

    # Tambahkan pattern dari additional_keywords jika ada
    if additional_keywords:
        for kw in additional_keywords:
            all_patterns.append(build_pattern(kw))

    # Gabungkan semua pattern dengan OR
    combined_pattern = "|".join(all_patterns)
    print(f'Pattern: {combined_pattern}')

    mask = df[columns].str.contains(combined_pattern, case=False, na=False, regex=True)
    return df[mask]
    
def normalize_text(text):
    if text is None:
        return ""
    text = text.lower()
    try: text = text.encode("latin1").decode("utf-8")
    except :
        pass

    text = re.sub(r'[^a-z0-9\s\-]', ' ', text)
    
    text = re.sub(r'\s+', ' ', text).strip()

    return text.strip()

def normalize_name(text):
    if not isinstance(text,str):
        text = str(text)

    if not text:
        return ''
        
    keywords = ['PT','CV','PT.','CV.','UD','UD.',', PT','(Importir)','Importir','Tbk','tbk',', CV',', UD']

    for keyword in keywords:

        text = text.lower()

        cleaned_text = text.replace(keyword,'').strip()

    return cleaned_text

def build_brand_automaton(brand_list):
    A = ahocorasick.Automaton()
    for brand in brand_list:

        brand_clean = normalize_text(brand)
        if brand_clean:
            A.add_word(brand_clean, brand)
    A.make_automaton()
    return A

def build_keyword_processor(data_list:list[str]) ->KeywordProcessor:
    """
    Create Flashtext's Keyword Processor using list of data
    """
    kp = KeywordProcessor(case_sensitive=False)
    kp.add_keywords_from_list(data_list)
    return kp

def extract_brand(
    text: str,
    brand_list: list[str],
    automaton: ahocorasick.Automaton = None,
    keyword_processor: KeywordProcessor = None,
    fuzzy_threshold: int = 90,
    method: str = "fuzzy"
) -> str | list[str]:

    if method not in ("fuzzy", "flashtext"):
        raise ValueError("Method must be 'fuzzy' or 'flashtext'")

    text_lower = text.lower()

    # ===== FLASH TEXT =====
    if method == "flashtext":

        if keyword_processor is None:
            raise ValueError("KeywordProcessor must be provided")

        matches = keyword_processor.extract_keywords(text)

        return matches if matches else "Tidak Ada Merek"


    # ===== FUZZY METHOD =====
    if automaton is None:
        raise ValueError("You must build Ahocorasick automaton first")

    matches = []
    seen = set()

    # --- Exact match ---
    for end_idx, original_brand in automaton.iter(text_lower):

        start_idx = end_idx - len(original_brand) + 1

        left_ok = (start_idx == 0) or (not text_lower[start_idx - 1].isalnum())
        right_ok = (end_idx == len(text_lower) - 1) or (not text_lower[end_idx + 1].isalnum())

        if left_ok and right_ok:
            return original_brand


    # --- Fuzzy fallback ---
    words = text_lower.split()

    for brand in brand_list:

        brand_lower = brand.lower().strip()

        if brand in seen:
            continue

        if len(brand_lower.split()) == 1:

            for word in words:

                score = fuzz.ratio(word, brand_lower)

                if score >= fuzzy_threshold:

                    matches.append((brand, score))
                    seen.add(brand)
                    break

        elif len(brand_lower.split()) > 1:

            score = fuzz.partial_ratio(text_lower, brand_lower)

            if score >= fuzzy_threshold:

                matches.append((brand, score))
                seen.add(brand)


    if not matches:
        return "Tidak Ada Merek"

    best_match = max(matches, key=lambda x: (x[1], len(x[0])))

    return best_match[0]

def remove_bracket_noise(text: str) -> str:
    # hapus semua teks dalam (), [], {}
    cleaned = re.sub(r'[\(\[\{][^)\]\}]*[\)\]\}]', '', text)
    # rapikan spasi berlebih
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def match_product(name:str, choices:list[str],score:int):
    match = process.extractOne(
        name,
        choices,
        score_cutoff = score)
    if match:
        return match[0]
    return None

# ================== Google Calendar Modules ===================

def ParseEventCategories():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES)
    
    service = build("calendar","v3",credentials=creds)

    today = pendulum.now("Asia/Jakarta")
    START = today.start_of("day").strftime("%Y-%m-%dT%H:%M:%S+07:00")
    END = today.end_of("day").strftime("%Y-%m-%dT%H:%M:%S+07:00")

    print(f"CALENDAR_ID : {CALENDAR_ID}")
    print(f"start date: {repr(START)}")
    print(f"end date : {repr(END)}")
    
          
    events = service.events().list(
        calendarId = CALENDAR_ID,
        timeMin=START,
        timeMax=END,
        singleEvents =True,
        orderBy= "startTime",
        showDeleted=False).execute()
    
    categories = []
    month = None
    year = None

    for event in events.get("items",[]):
        if event.get("status") == "cancelled":
            continue

        title = event.get("summary","")

        if "RUN_PIPELINE:" in title:
            event_start = event["start"].get("dateTime", event["start"].get("date"))
            event_dt = pendulum.parse(event_start)

            month = str(event_dt.month)
            year = event_dt.year
            description = event.get("description","")

            if ":" in title:
                extracted = title.split(":", 1)[1]
            else:
                extracted = description

            for raw_cat in extracted.split(","):
                raw_cat = raw_cat.strip()
                #Detect name ends with "BIG"
                is_big = bool(re.search(r'\[BIG\]', raw_cat, re.IGNORECASE))
                clean_cat = re.sub(r'\[BIG\]','',raw_cat, flags=re.IGNORECASE)
                categories.append({"name":clean_cat,
                                  "is_big":is_big})

    return categories, month, year

#DirectoryGenerator
def DirectoryGenerator(BASE_PATH,category,month,year):

    category = category.replace("_","").title()

    with open(r"/home/user2/airflow/dags/DataPinter_Runner/pipeline_assets.json") as f:
        assets_json = json.load(f)
        months_json = assets_json["months"]
    parse_month = months_json[str(month)]
    return f"{BASE_PATH}/{category}/{category}{parse_month}{year}"

def SearchDBPath(BASE_RAW,category):
    BASE_RAW = str(BASE_RAW)

    with open(r"/home/user2/airflow/dags/DataPinter_Runner/pipeline_assets.json") as f:
        assets_json = json.load(f)
        categories_json = assets_json['categories']

    for db_path in categories_json.keys():
        if category in categories_json.get(db_path):
            db_target = db_path
            return Path(f"{BASE_RAW}/{db_target}")
    
    #If none of category match with list of values
    raise ValueError(f"Category :Requested {category} data can not be found in Database")

