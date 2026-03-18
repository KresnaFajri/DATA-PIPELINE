import streamlit as st
import sys
sys.path.append("C:\KRESNA\Tools-20251201T015117Z-1-001\Tools\DATA PIPELINE\DataAds_Pipeline")
from EDA import GetData
from config import DashboardConfig

QUERY_LOC = """
SELECT * FROM LocationReport
"""
QUERY_AGE = """
SELECT * FROM AgeReport
"""

QUERY_CAM = """
SELECT * FROM CampaignReport
"""

QUERY_KEYWORD = """
SELECT * FROM KeywordReport
"""

df_loc = GetData(DashboardConfig.DB_LOC,query = QUERY_LOC)
df_age = GetData(DashboardConfig.DB_AGE,query = QUERY_AGE)
df_camp = GetData(DashboardConfig.DB_CAM,query = QUERY_CAM)
df_keyword = GetData(DashboardConfig.DB_KEY,query = QUERY_KEYWORD)



#Create Charts
st.title('Nose Ads Dashboard')

st.set_page_config(layout="wide")

if "counter" not in st.session_state:
    st.session_state.counter = 0
st.session_state.counter += 1
st.header(f"This page has run {st.session_state.counter} times.")
st.button('Run It Again')