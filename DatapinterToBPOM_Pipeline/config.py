from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Config:
    DB_NAME = os.getenv('DB_NAME')
    HOST = os.getenv('HOST')
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
    PORT = os.getenv('PORT')

    #Excel
    DATASOURCE_PATH = os.getenv('DATASOURCE_PATH')
    EXCEL_FILENAME_1 = os.getenv('EXCEL_FILENAME_1')
    EXCEL_FILENAME_2 = os.getenv('EXCEL_FILENAME_2')
    TABLE_NAME = os.getenv('TABLE_NAME')
    CATEGORY = os.getenv('CATEGORY')
    FILE_NAME = os.getenv('FILE_NAME')
    FILE_NAME_2 = os.getenv('FILE_NAME_2')
    N_ROWS = int(os.getenv('N_ROWS'))
    CLEAN_BPOMDB_PATH=os.getenv('CLEAN_PATH_BPOMDB')
    BRAND_PRODUCT_VAR_PATH = os.getenv('BRAND_PRODUCT_VAR')
