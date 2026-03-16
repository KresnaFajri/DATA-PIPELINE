from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv()

class Config:
    TARGET_PATH = os.getenv('TARGET_PATH')
    SOURCE_PATH = os.getenv('SOURCE_PATH')