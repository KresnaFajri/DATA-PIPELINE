import pptx
import pandas as pd
import os
import duckdb
import sys
import datetime
from pptx import Presentation
from pptx.util import Inches,Pt
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools\DATA PIPELINE\DataPinter_Pipeline")
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools\DATA PIPELINE\DataPinter_Pipeline\dynamic-ppt")
from config import PPTConfig,PipelineConfig
from base_ppt import CreateBaseAndTitle,AddCharts, AddTextBox
from styling import KeepTextStyle

DB_PATH = r"C:\KRESNA\ANALYSIS\SKINCARE\SKINCARE_DUCKDB\skincare.duckdb"
query = f"SELECT * FROM skincare.main.shopee_{PipelineConfig.CATEGORY}"
TARGET_PATH = PipelineConfig.TARGET_PATH

#Create connection
conn = duckdb.connect(DB_PATH)
#Fetch dataframe
df = conn.execute(query).fetchdf()

#Create Presentation template
prs = Presentation(PPTConfig.TEMPLATE_PATH)

def CheckFiles(TARGET_PATH):
    csv_list = []
    xlsx_list = []

    for file in os.listdir(TARGET_PATH):
        if file.endswith('.csv'):
            csv_list.append(file)
        elif file.endswith('.xlsx'):
            xlsx_list.append(file)
    return [csv_list, xlsx_list]
    
def PieCharts(file_list,keyword_file,target_path,category_product,
              label_columns,
              value_columns,
              title_charts):
    #Create plotly pie charts
    csv_list = file_list[0]
    xlsx_list = file_list[1]

    mshare_csv = [f for f in csv_list if f'{keyword_file}' in f]
    mshare_xlsx = [f for f in xlsx_list if f'{keyword_file}' in f]

    if mshare_csv:
        df = pd.read_csv(os.path.join(target_path,mshare_csv[0]))
    elif mshare_xlsx:
        df = pd.read_excel(os.path.join(target_path,mshare_xlsx[0]))
    else:
        raise FileNotFoundError("File MShare can not be found")
    charts = go.Figure(
        data = [go.Pie(
            labels = df[label_columns],
            values = df[value_columns])])
    charts.update_traces(hoverinfo = 'label+percent', textinfo='percent',textfont_size=20)
    charts.update_layout(title = f'{title_charts} {category_product.title()}',
                                paper_bgcolor = 'rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font_color = 'white',
                                title_font_color = 'white',
                                width = 1500,
                                height = 900)
    
    path_img=os.path.join(target_path,f'{keyword_file}'+'charts.png')
    
    pio.write_image(charts,path_img,engine="kaleido")
    return path_img
#Read excel file
def ReadBrandData(file, top_k):
    """
    Check brand data to provide for PPT Text
    Params
    - file : Must be file with 'csv' or 'xlsx' format
    - top_k : Check top k data brand that will be provided for presentationt text
    """
    if file.endswith('csv'):
        df = pd.read_csv(file)
    elif file.endswith('xlsx'):
        df = pd.read_excel(file)

    BRAND = df['Brand'][top_k]
    VALUES = df['OmsetPerBrand'][top_k]

    return BRAND,VALUES

if __name__ == "__main__":

    file_list = CheckFiles(PipelineConfig.TARGET_PATH)

    MShare_IMG = PieCharts(file_list,keyword_file = 'MShare',
                          target_path = PipelineConfig.TARGET_PATH,
                          category_product=PipelineConfig.CATEGORY,
                          label_columns = 'brand',
                          value_columns = 'OmsetPerBrand',
                          title_charts = 'Market Share')
    
    PentCharts_IMG = PieCharts(file_list, keyword_file='MPent',
                            target_path = PipelineConfig.TARGET_PATH,
                            category_product = PipelineConfig.CATEGORY,
                            label_columns = 'brand',
                            value_columns = 'UlasanPerBrand',
                            title_charts = 'Market Penetration')
    
    prs = CreateBaseAndTitle(df = df,TEMPLATE_PATH =PPTConfig.TEMPLATE_PATH, 
                       PATH = PipelineConfig.TARGET_PATH,
                       category = PipelineConfig.CATEGORY.title(),
                       PPT_NAME = 'MoisturizerData.pptx')
    
    AddCharts(prs = prs, page_id = 4, chart_img = MShare_IMG, 
              size =(Inches(10),Inches(6)),position = (Inches(9),Inches(2)))
    
    brand,omz= ReadBrandData(os.path.join(PipelineConfig.TARGET_PATH,'MShareBrand.csv'))
    text = f"Di bulan ini, brand {brand} menjadi brand dengan market share tertinggi dengan nilai omset sebesar {omz}"
    AddTextBox(prs = prs,
               page_id = 4,
               text =  text,
               textfont='Open Sauce',
               textsize = Pt(25))
    prs.save(os.path.join(PipelineConfig.TARGET_PATH, 'MoisturizerData.pptx'))