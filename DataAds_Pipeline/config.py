from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv()

class Config:
    TARGET_PATH = os.getenv('TARGET_PATH')
    SOURCE_PATH = os.getenv('SOURCE_PATH')

    LOC_DB_PATH = os.getenv("LOC_DB_PATH")
    CAMPAIGN_DB_PATH = os.getenv("CAMP_DB_PATH")
    AGE_DB_PATH = os.getenv("AGE_DB_PATH")
    KEYWORD_DB_PATH = os.getenv("KEYWORD_DB_PATH")

    db_loc = os.getenv("db_loc")
    db_campaign=os.getenv("db_camp")
    db_age = os.getenv("db_age")
    db_keywords = os.getenv("db_keyword")

    month = os.getenv("MONTh")
    year = os.getenv("YEAR")

    


