from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv()

print("Looking for .env at:", BASE_DIR / ".env")
print("File exists?", (BASE_DIR / ".env").exists())

class PipelineConfig:
    """
    DataPinter Pipeline Configuration
    """

    # Path Configuration
    TARGET_PATH = os.getenv("TARGET_PATH")
    DB_PATH = os.getenv("DB_PATH")
    DATA_PATH = os.getenv("DATA_PATH")
    STOPWORDS_PATH = os.getenv("STOPWORDS_PATH")
    BRAND_PATH = os.getenv("BRAND_PATH")

    #Pipeline DB Path
    PIPELINE_DB_SKCARE=os.getenv("PIPELINE_DB_SKCARE")
    PIPELINE_DB_HAIRCARE=os.getenv("PIPELINE_DB_HAIRCARE")
    PIPELINE_DB_BABYCARE= os.getenv("PIPELINE_DB_BABYCARE")
    PIPELINE_DB_SUPLEMEN=os.getenv("PIPELINE_DB_SUPLEMEN")
    PIPELINE_DB_BODYCARE=os.getenv("PIPELINE_DB_BODYCARE")
    PIPELINE_DB_LIPCARE=os.getenv("PIPELINE_DB_LIPCARE")
    PIPELINE_DB_DECORATIVE=os.getenv("PIPELINE_DB_DECORATIVE")
    PIPELINE_DB_LOG = os.getenv("DB_LOG_PATH")

    #Database Filtering Config
    TIME_WINDOW_START =  os.getenv("TIME_WINDOW_START")
    TIME_WINDOW_END = os.getenv("TIME_WINDOW_END")
    CATEGORY = os.getenv("category")
    Top_N = os.getenv("Top_N")

if PipelineConfig.DB_PATH is None:
        raise ValueError("DB_PATH not found in .env")

class PPTConfig:
      """
      PPT Configuration only for automatic PPT creation
      """
      TITLE_TEXT = os.getenv('TITLE_TEXT')
      MONTH = os.getenv('MONTH')
      PPT_NAME = os.getenv('PPT_NAME')
      TEMPLATE_PATH = os.getenv('template_path')