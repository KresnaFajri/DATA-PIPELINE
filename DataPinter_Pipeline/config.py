from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR/".env")

print("Looking for .env at:", BASE_DIR / ".env")
print("File exists?", (BASE_DIR / ".env").exists())

class AutomatePipelineConfig:
    """
    DataPinter Pipeline Configuration
    """
    #POSTGRES
    POSTGRES_DBNAME = os.getenv("DB_NAME")
    POSTGRES_HOST = os.getenv("HOST")
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = os.getenv("PASSWORD")
    POSTGRES_PORT = os.getenv("PORT")

    # Path Configuration
    GCAL_CRED = os.getenv("GCAL_CRED")
    BASE_PATH_DB = os.getenv("BASE_PATH_DB")
    BASE_PATH_TARGET = os.getenv("BASE_PATH_TARGET")
    DATA_PATH = os.getenv("DATA_PATH")
    STOPWORDS_PATH = os.getenv("STOPWORDS_PATH")
    BRAND_PATH_SKCARE = os.getenv("BRAND_PATH_SKCARE")
    BRAND_PATH_SUPP = os.getenv("BRAND_PATH_SUPP")
    BRAND_PATH_BABYCARE = os.getenv("BRAND_PATH_BABYCARE")

    #Pipeline DB Path
    PIPELINE_DB_SKCARE=os.getenv("PIPELINE_DB_SKCARE")
    PIPELINE_DB_BABYCARE=os.getenv("PIPELINE_DB_BABYCARE")
    PIPELINE_DB_SUPLEMEN=os.getenv("PIPELINE_DB_SUPLEMEN")
    PIPELINE_DB_LOG = os.getenv("DB_LOG_PATH")

    #Database Filtering Config
    TIME_WINDOW_START =  os.getenv("TIME_WINDOW_START")
    TIME_WINDOW_END = os.getenv("TIME_WINDOW_END")
    CATEGORY = os.getenv("category")
    Top_N = os.getenv("Top_N")
