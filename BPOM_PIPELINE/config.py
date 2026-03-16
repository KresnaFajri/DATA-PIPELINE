from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR/".env")

class Config:
    DB_NAME = os.getenv('DB_NAME')
    HOST = os.getenv('HOST')
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
    PORT = os.getenv('PORT')

    SUNSCREEN_REGEX = os.getenv("SUNSCREEN_REGEX")
    BABYCARE_REGEX = os.getenv("BABY_CARE_REGEX")

if Config.DB_NAME is None:
        raise ValueError("DB_NAME not found in .env")