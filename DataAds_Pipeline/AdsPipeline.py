import os 
import pandas as pd
import duckdb
import re
from pathlib import Path
from config import Config
import sys
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools")
from DataCleaner import DataCleaner
import warnings
from extract import ExtractFiles
from transform import TransformFiles
from load import LoadDuckDB

warnings.filterwarnings("ignore", category=UserWarning, module='openpyxl')

cleaner = DataCleaner()
SOURCEFILES = [d for d in os.listdir(Config.SOURCE_PATH) if os.path.isdir(os.path.join(Config.SOURCE_PATH, d))]
print("Folders:", SOURCEFILES)

campaign_df = []
keyword_df = []
location_df = []
age_df = []

for dir in SOURCEFILES:
    month_match = re.search(r"\d{2}-\d{4}",dir)
    month = month_match.group() if month_match else None

    for file in os.listdir(os.path.join(Config.SOURCE_PATH,dir)):
        AGE_DATAPATH = os.path.join(Config.SOURCE_PATH,dir,file)
        if 'Age' in file:
            if os.path.exists(AGE_DATAPATH):
                print(f'Files Exist : {AGE_DATAPATH}')
                df = ExtractFiles(AGE_DATAPATH)
                df['Month'] = month
                recap_df,main_df = cleaner.SplitRecapRows(df)
                age_df.append(main_df)
            else:
                print(f'Age files can not be found')

        elif 'keyword' in file:
            KEYWORD_DATAPATH = os.path.join(Config.SOURCE_PATH,dir,file)
            if os.path.exists(KEYWORD_DATAPATH):
                print(f'Keywords File Exists : {KEYWORD_DATAPATH}')
                df = ExtractFiles(KEYWORD_DATAPATH)
                df['Month'] = month
                recap_df,main_df = cleaner.SplitRecapRows(df)
                keyword_df.append(main_df)
            else:
                print(f'Keywords file can not be found')

        elif 'Campaign' in file:
            CAMPAIGN_DATAPATH = os.path.join(Config.SOURCE_PATH,dir,file)
            if os.path.exists(CAMPAIGN_DATAPATH):
                print(f'Campaign file exists : {CAMPAIGN_DATAPATH}')
                df = ExtractFiles(CAMPAIGN_DATAPATH)
                df['Month'] = month
                recap_df, main_df = cleaner.SplitRecapRows(df)
                campaign_df.append(main_df)
            else:
                print(f'Campaign file can not be found')

        elif 'Location' in file:
            LOCATION_DATAPATH = os.path.join(Config.SOURCE_PATH,dir,file)
            if os.path.exists(LOCATION_DATAPATH):
                print(f'Location file exits: {LOCATION_DATAPATH}')
                df = ExtractFiles(LOCATION_DATAPATH)
                df['Month'] = month
                recap_df,main_df = cleaner.SplitRecapRows(df)
                location_df.append(main_df)
            else:
                print(f'Location file can not be found')

TARGET_FILES = os.listdir(Config.TARGET_PATH)
#Transform data,eliminate all 0 and NULL columns, and automatically set all data into DuckDB
if campaign_df:
    campaign_df = pd.concat(campaign_df, ignore_index = True)
    campaign_df.to_excel(os.path.join(Config.TARGET_PATH,'campaign_raw.xlsx'))
    campaign_df = TransformFiles(campaign_df,suffix='campaign')
    LoadDuckDB(
        df = campaign_df,
        db_path = os.path.join(Config.TARGET_PATH,'campaign.duckdb'),
        table_name = 'CampaignReport',
        mode = 'replace'
    )
if keyword_df:
    keyword_df = pd.concat(keyword_df,ignore_index = True)
    keyword_df.to_excel(os.path.join(Config.TARGET_PATH,'keyword_raw.xlsx'))
    print(keyword_df.columns)
    keyword_df = TransformFiles(keyword_df,suffix='keyword')
    LoadDuckDB(
        df = keyword_df,
        db_path = os.path.join(Config.TARGET_PATH,'keyword.duckdb'),
        table_name = 'KeywordReport',
        mode = 'replace'
    )
if location_df:
    location_df = pd.concat(location_df, ignore_index = True)
    location_df.to_excel(os.path.join(Config.TARGET_PATH,'location_raw.xlsx'))
    location_df = TransformFiles(location_df,suffix='loc')
    LoadDuckDB(
        df = location_df,
        db_path = os.path.join(Config.TARGET_PATH,'location.duckdb'),
        table_name = 'LocationReport',
        mode = 'replace')
if age_df:
    age_df = pd.concat(age_df, ignore_index = True)
    age_df.to_excel(os.path.join(Config.TARGET_PATH,'age_raw.xlsx'))
    age_df = TransformFiles(age_df,suffix='age')
    LoadDuckDB(
        df = age_df,
        db_path = os.path.join(Config.TARGET_PATH,'age.duckdb'),
        table_name = 'AgeReport',
        mode = 'replace')

#Check Whether file already stored in DuckDB
con = duckdb.connect(r"C:\KRESNA\ANALYSIS\Ads Analysis\DUCKDB_ADS_DATASET\location.duckdb")
print(con.execute("SHOW TABLES").fetchdf())