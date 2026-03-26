import streamlit as st
import sys
import duckdb
sys.path.append("C:\KRESNA\Tools-20251201T015117Z-1-001\Tools\DATA PIPELINE\DataAds_Pipeline")
from EDA import GetDataForMetrics,GetData
from EDA import *
from config import DashboardConfig
from pathlib import Path
from dateutil.relativedelta import relativedelta
from queries import *
from components.metrics import render_metrics
from components.charts import render_line_chart

#----------------------------------------Background and Styling------------------------#
st.set_page_config(
    page_title="Dashboard",
    page_icon="🔐",
    layout="wide",
)

# ── Helper: load CSS dari file ────────────────────────────────────────────────
def load_css(*paths: str) -> None:
    css = ""
    for path in paths:
        css += Path(path).read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css(r"styles\background.css", r"styles\metrics.css")
# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="jb-title">Dashboard Ads</div>
<div class="jb-subtitle">PT NOSE HERBALINDO</div>
""", unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════════
# DATA — ganti nilai di sini dengan data asli kamu
# ══════════════════════════════════════════════════════════════════════════════
con = duckdb.connect(r"C:\KRESNA\ANALYSIS\Ads Analysis\DUCKDB_ADS_DATASET\campaign.duckdb")

@st.cache_data(ttl=60)

def GetPeriod():
    df = con.execute("""
        SELECT DISTINCT 
        month_campaign
        FROM CampaignReport
        ORDER BY month_campaign DESC
                      """).df()
    return df

#Period List
PERIOD_LIST = GetPeriod()
MONTH_NAME= ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]
CHOICE = st.selectbox(
    "Pilih Periode",
    options=PERIOD_LIST["month_campaign"].tolist(),
    format_func=lambda x:f"{MONTH_NAME[x.month-1]} {x.year}")

df_filtered = con.execute("""
                           SELECT * FROM CampaignReport
                           WHERE month_campaign = ?
                           """,[CHOICE.to_pydatetime()]).df()
def CalculateDelta(current,before):
     delta = current - before
     delta_class = "green" if delta >=0 else "danger"
     delta_text = f"+{delta:,.0f}" if delta >= 0 else f"{delta:,.0f}"
     return delta_class, delta_text

ConvCurrent = GetDataForMetrics(db_path=DashboardConfig.DB_CAM_PATH,
                                    query = QueryConversionPerMonth(db_name = "campaign",
                                                                    table = DashboardConfig.CAMP_TABLE,
                                                                    date_choice = CHOICE)).iloc[0,0]
ConvBefore = GetDataForMetrics(db_path=DashboardConfig.DB_CAM_PATH,
                                query = QueryConversionPerMonth(db_name="campaign",
                                                                table = DashboardConfig.CAMP_TABLE,
                                                                date_choice=CHOICE-relativedelta(months=1))).iloc[0,0]
ImprCurrent = GetDataForMetrics(db_path=DashboardConfig.DB_CAM_PATH,
                                query = QueryImpressionPerMonth(db_name="campaign",
                                                                table = DashboardConfig.CAMP_TABLE,
                                                                date_choice=CHOICE)).iloc[0,0]
ImprBefore = GetDataForMetrics(db_path = DashboardConfig.DB_CAM_PATH,
                               query=QueryImpressionPerMonth(db_name="campaign",
                                                             table=DashboardConfig.CAMP_TABLE,
                                                             date_choice=CHOICE-relativedelta(months=1))).iloc[0,0]
ActiveCampaignCount = GetDataForMetrics(db_path=DashboardConfig.DB_CAM_PATH,
                                        query=CountRunningCampaign(db_name="campaign",
                                        table=DashboardConfig.CAMP_TABLE,
                                        date_choice=CHOICE)).iloc[0,0]

ImpressionDelta_class, ImpressionDelta_text = CalculateDelta(ImprCurrent, ImprBefore)
ConvDelta_class, ConvDelta_text = CalculateDelta(ConvCurrent,ConvBefore)

# ══════════════════════════════════════════════════════════════════════════════
# DATA — ganti nilai di sini dengan data asli kamu
# ══════════════════════════════════════════════════════════════════════════════
metrics_data = [
    {
        "label": "Jumlah Impressions per Campaign",
        "value": ImprCurrent,
        "value_class": "teal",   # pilihan: "" | "teal" | "green" | "amber" | "red"
        "delta": f"{ImpressionDelta_text} impressions", # teks kecil di bawah angka
        "delta_class": ImpressionDelta_class,       # pilihan: "" | "warn" | "danger"
    },
    {
        "label": "Jumlah Conversions per Campaign",
        "value": ConvCurrent,
        "value_class": "orange",
        "delta": f"{ConvDelta_text} Conversions",
        "delta_class": ConvDelta_class,
    },
    {
        "label": "Jumlah Campaign yang Sedang Running",
        "value": f"{ActiveCampaignCount} Campaign Aktif",
        "value_class": "green"
    },
]
render_metrics(metrics_data)
# ══════════════════════════════════════════════════════════════════════════════
# Charts
# ══════════════════════════════════════════════════════════════════════════════
# 1. Grafik 1 : Whole Conversion Chart 2024-2026
ConversionTimeline = GetData(db_path=DashboardConfig.DB_CAM_PATH,
                                 query=QueryConversionData(db_name="campaign",
                                                           table="CampaignReport"))
render_line_chart(x = ConversionTimeline['month_campaign'],
                  y = ConversionTimeline['TotalConversions'])

