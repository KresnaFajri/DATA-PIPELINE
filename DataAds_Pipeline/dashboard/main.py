import streamlit as st
import sys
import os
import duckdb
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools\DATA PIPELINE\DataAds_Pipeline")
from EDA import *
from config import DashboardConfig
from pathlib import Path
from dateutil.relativedelta import relativedelta
from queries import *
from components.metrics import render_metrics
from components.charts import *

#----------------------------------------Background and Styling------------------------#
st.set_page_config(
    page_title="Dashboard",
    page_icon="🔐",
    layout="wide",
)

# ── Helper: load CSS dari file ────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent

def load_css(*paths: str) -> None:
    css = ""
    for path in paths:
        css += Path(path).read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


load_css(os.path.join(BASE_DIR,styles,"background.css"), os.path.join(BASE_DIR,"styles","metrics.css")
# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="jb-title">Dashboard Ads</div>
<div class="jb-subtitle">PT NOSE HERBALINDO</div>
""", unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════════
# DATA — ganti nilai di sini dengan data asli kamu
# ══════════════════════════════════════════════════════════════════════════════

#Connection
con = GetConnection(database_name = "campaign",
                    ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN)

@st.cache_data(ttl=60)
def GetPeriod():
    con = GetConnection(database_name = "campaign",
                    ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN)
    
    df = con.execute("""
        SELECT DISTINCT 
        month_campaign
        FROM CampaignReport
        ORDER BY month_campaign DESC
                      """).df()
    return df


#Period List
PERIOD_LIST = GetPeriod()

if "CHOICE" not in st.session_state:
    st.session_state.CHOICE = PERIOD_LIST["month_campaign"].tolist()[0]
if "selected_campaign"not in st.session_state:
    st.session_state.selected_campaign = None

MONTH_NAME= ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]
CHOICE = st.selectbox(
    "Pilih Periode",
    options=PERIOD_LIST["month_campaign"].tolist(),
    format_func=lambda x:f"{MONTH_NAME[x.month-1]} {x.year}",
    key = "CHOICE")

df_filtered = con.execute("""
                           SELECT * FROM CampaignReport
                           WHERE month_campaign = ?
                           """,[CHOICE.to_pydatetime()]).df()

CAMPAIGN_LIST = GetData(db_path = DashboardConfig.DB_CAM_PATH,
                        ACCESS_TOKEN =DashboardConfig.ACCESS_TOKEN,
                        query = GetCampaignList(period_choice=CHOICE))

def CalculateDelta(current,before):
     delta = current - before
     delta_class = "green" if delta >=0 else "danger"
     delta_text = f"+{delta:,.0f}" if delta >= 0 else f"{delta:,.0f}"
     return delta_class, delta_text

ConvCurrent = GetData(db_path = DashboardConfig.DB_CAM_PATH,
                      USE_MOTHERDUCK = DashboardConfig.USE_MOTHERDUCK,
                      #ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                    query = QueryConversionPerMonth(db_name = "campaign",table = DashboardConfig.CAMP_TABLE,
                                                                    date_choice = CHOICE)).iloc[0,0]

ConvBefore = GetData(db_path = DashboardConfig.DB_CAM_PATH,
                                USE_MOTHERDUCK = DashboardConfig.USE_MOTHERDUCK,
                                #ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                                query = QueryConversionPerMonth(db_name = "campaign",table = DashboardConfig.CAMP_TABLE,
                                                                    date_choice = CHOICE-relativedelta(months=1))).iloc[0,0]

ClicksCurrent = GetData(db_path = DashboardConfig.DB_CAM_PATH,
                        USE_MOTHERDUCK = DashboardConfig.USE_MOTHERDUCK,
                        #ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                        query = QueryClickPerMonth(db_name = "campaign",table = DashboardConfig.CAMP_TABLE,
                                                        date_choice=CHOICE)).iloc[0,0]
ClicksBefore = GetData(db_path = DashboardConfig.DB_CAM_PATH,
                       USE_MOTHERDUCK = DashboardConfig.USE_MOTHERDUCK,
                       #ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                       query=QueryClickPerMonth(db_name = "campaign",
                                                table = DashboardConfig.CAMP_TABLE,
                                                date_choice=CHOICE-relativedelta(months=1))).iloc[0,0]
ClicksCurrent = GetData(db_path = DashboardConfig.DB_CAM_PATH,
                        USE_MOTHERDUCK = DashboardConfig.USE_MOTHERDUCK,
                        #ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                        query = QueryClickPerMonth(db_name = "campaign",table = DashboardConfig.CAMP_TABLE,
                                                        date_choice=CHOICE)).iloc[0,0]
ClicksBefore = GetData(db_path = DashboardConfig.DB_CAM_PATH,
                       USE_MOTHERDUCK = DashboardConfig.USE_MOTHERDUCK,
                       #ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                       query=QueryClickPerMonth(db_name = "campaign",table = DashboardConfig.CAMP_TABLE,
                                                             date_choice=CHOICE-relativedelta(months=1))).iloc[0,0]
ActiveCampaignCount = GetData(db_path = DashboardConfig.DB_CAM_PATH,
                              USE_MOTHERDUCK = DashboardConfig.USE_MOTHERDUCK,
                              #ACCESS_TOKEN=DashboardConfig.ACCESS_TOKEN,
                              query=CountRunningCampaign(db_name = "campaign",table = DashboardConfig.CAMP_TABLE,
                                                      date_choice=CHOICE)).iloc[0,0]

ClickDelta_class, ClickDelta_text = CalculateDelta(ClicksCurrent, ClicksBefore)
ConvDelta_class, ConvDelta_text = CalculateDelta(ConvCurrent,ConvBefore)

# ══════════════════════════════════════════════════════════════════════════════
# DATA — ganti nilai di sini dengan data asli kamu
# ══════════════════════════════════════════════════════════════════════════════
metrics_data = [
    {
        "label": "Jumlah Clicks/Pengunjung Website Bulan Ini",
        "value": ClicksCurrent,
        "value_class": "teal",   # pilihan: "" | "teal" | "green" | "amber" | "red"
        "delta": f"{ClickDelta_text} Clicks", # teks kecil di bawah angka
        "delta_class": ClickDelta_class,       # pilihan: "" | "warn" | "danger"
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
                                 query=QueryConversionData(db_name = "campaign",table="CampaignReport"))

st.header("Total Konversi Visitor Menjadi Potential Client Sepanjang Tahun")
render_line_chart(x = ConversionTimeline['month_campaign'],
                  y = ConversionTimeline['TotalConversions'])

col1,col2 = st.columns(2)

# 2.Percentage of Effective Campaign in gaining customer
CampaignConversionData = GetData(db_path = DashboardConfig.DB_CAM_PATH,
                                 query=QueryCampaignConv(db_name = "campaign",table="CampaignReport",
                                                   period_choice=CHOICE))

CampaignBudgetData = GetData(db_path=DashboardConfig.DB_CAM_PATH,
                            query=QueryCostCampaign(db_name = "campaign",table="CampaignReport",
                                                   period_choice=CHOICE))

FunnelDF = GetData(db_path=DashboardConfig.DB_CAM_PATH,
                             query=FunnelStaging(period_choice=CHOICE))
funneling_stage = FunnelDF.columns.tolist()

#3rd rows
with col1:
    st.header("Kontribusi Tiap Campaign terhadap Jumlah Konversi")
    render_pie_chart(labels = CampaignConversionData['campaign'],
                       values=CampaignConversionData['TotalConversions'])
with col2:
    st.header("Persentase Cost Tiap Campaign")
    render_pie_chart(labels=CampaignBudgetData["campaign"],
                     values=CampaignBudgetData["TotalCost"])
    
col3,col4 = st.columns(2)
with col3:
    st.header(f"Marketing Funnel in {pd.to_datetime(CHOICE,yearfirst=True).strftime('%B, %Y')}")
    MarketFunnelPlot(df = FunnelDF,stages = funneling_stage)

TopKeywords = GetData(db_path=DashboardConfig.DB_KEY_PATH,
                      query=QueryTopKeywords(period_choice=CHOICE))
with col4:
    st.header(f"Top Keywords in {pd.to_datetime(CHOICE,yearfirst=True).strftime('%B, %Y')}")
    render_invertedbar_chart(categories=TopKeywords["Keywords"],values=TopKeywords["Total Conversions"])

@st.cache_data(ttl=60)
def GetImpressionShare(campaign,period_choice):
    return GetData(
        db_path = DashboardConfig.DB_CAM_PATH,
        ACCESS_TOKEN = DashboardConfig.ACCESS_TOKEN,
        query = QueryImpressionShare(campaign=campaign, period_choice = period_choice))

#4th row
st.header(f"Impression Share per Campaign in {pd.to_datetime(CHOICE,yearfirst=True).strftime('%B, %Y')}")
selected_campaign = st.selectbox("Pilih Campaign",
                                 CAMPAIGN_LIST['campaign'],
                                 key = "selected_campaign")
if selected_campaign:
    ImpressionShareData = GetImpressionShare(selected_campaign, CHOICE)
    if not ImpressionShareData.empty:
        labels = ["Impression Share", "Lost IS"]
        values = [ImpressionShareData["Impression Share"].iloc[0]*100, 
                    ImpressionShareData["Lost IS"].iloc[0]*100]
        render_pie_chart(labels = labels,
                        values = values)
    else:
        st.warning("Tidak ditemukan data untuk campaign ini")
else:
    st.info("Silahkan pilih nama campaign untuk divisualkan")
    
        
