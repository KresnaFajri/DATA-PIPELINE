from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR/".env")

class DashboardConfig:
    
    DB_AGE_PATH = os.getenv("DB_AGE")
    DB_LOC_PATH = os.getenv("DB_LOC")
    DB_CAM_PATH = os.getenv("DB_CAM")
    DB_KEY_PATH = os.getenv("DB_KEY")

    db_loc = os.getenv("db_loc")
    db_campaign = os.getenv("db_camp")
    db_keyword = os.getenv("db_keyword")
    db_age = os.getenv("db_age")

    LOC_TABLE = os.getenv("LOC_TABLE")
    KEY_TABLE = os.getenv("KEY_TABLE")
    CAMP_TABLE = os.getenv("CAMP_TABLE")
    AGE_TABLE = os.getenv("AGE_TABLE")

