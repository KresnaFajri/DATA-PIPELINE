from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR/".env")

class DashboardConfig:
    
    DB_AGE = os.getenv("DB_AGE")
    DB_LOC = os.getenv("DB_LOC")
    DB_CAM = os.getenv("DB_CAM")
    DB_KEY = os.getenv("DB_KEY")