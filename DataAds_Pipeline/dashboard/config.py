from dotenv import load_dotenv
import os
from pathlib import Path
import streamlit as st

#BASE_DIR = Path(__file__).resolve().parent
#load_dotenv(BASE_DIR/".streamlit/secrets.toml")

class DashboardConfig:
    
    DB_AGE_PATH = st.secrets.get("DB_AGE") 
    DB_LOC_PATH = st.secrets.get("DB_LOC") 
    DB_CAM_PATH = st.secrets.get("DB_CAM") 
    DB_KEY_PATH = st.secrets.get("DB_KEY")

    db_loc = st.secrets.get("db_loc") 
    db_campaign = st.secrets.get("db_camp")
    db_keyword = st.secrets.get("db_keyword")
    db_age = st.secrets.get("db_age") 

    LOC_TABLE = st.secrets.get("LOC_TABLE")
    KEY_TABLE = st.secrets.get("KEY_TABLE")
    CAMP_TABLE = st.secrets.get("CAMP_TABLE")
    AGE_TABLE = st.secrets.get("AGE_TABLE")

    USE_MOTHERDUCK = st.secrets.get("USE_MOTHERDUCK")
    ACCESS_TOKEN = st.secrets.get("ACCESS_TOKEN")


