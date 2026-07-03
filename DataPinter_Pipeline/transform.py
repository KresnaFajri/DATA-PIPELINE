import pandas as pd
import sys
import json
import logging
import psycopg2
import re
sys.path.append(r"/home/user2/airflow")
from DataCleaner import DataCleaner,FeatureGenerator
import html
from config import AutomatePipelineConfig
from utils import build_brand_automaton,extract_brand,remove_bracket_noise

STOPWORDS_PATH = AutomatePipelineConfig.STOPWORDS_PATH

#CAN ONLY BE USED ON DATAPINTER CSV
def transform(df, query_keywords):
    fgen = FeatureGenerator()
    log = logging.getLogger(__name__)

    #Defining brand list for Aho-Corasick Automaton
    BRAND_SUPP = pd.read_csv(AutomatePipelineConfig.BRAND_PATH_SUPP)
    BRAND_SKCARE = pd.read_csv(AutomatePipelineConfig.BRAND_PATH_SKCARE)
    BRAND_BABYCARE = pd.read_csv(AutomatePipelineConfig.BRAND_PATH_BABYCARE)

    BRAND_SUPP = BRAND_SUPP.map(lambda x: html.unescape(x) if isinstance(x,str) else x)
    BRAND_SKCARE = BRAND_SKCARE.map(lambda x: html.unescape(x) if isinstance(x, str) else x)
    BRAND_BABYCARE = BRAND_BABYCARE.map(lambda x: html.unescape(x) if isinstance(x, str) else x)

    # remove punctuation
    BRAND_SKCARE = BRAND_SKCARE.map(lambda x: re.sub(r"[^\w\s]", "", x) if isinstance(x, str) else x)
    BRAND_SUPP = BRAND_SUPP.map(lambda x: re.sub(r"[^\w\s]", "", x) if isinstance(x, str) else x)
    BRAND_BABYCARE = BRAND_BABYCARE.map(lambda x: re.sub(r"[^\w\s]", "", x) if isinstance(x, str) else x)
    
    brand_list_skcare = [b.strip().lower() for b in BRAND_SKCARE['product_brands'] if isinstance(b,str)]
    brand_list_supp = [b.strip().lower() for b in BRAND_SUPP['product_brands'] if isinstance(b,str)]
    brand_list_babycare = [b.strip().lower() for b in BRAND_BABYCARE['product_brands'] if isinstance(b,str)]

    print(brand_list_supp)

    df = df.copy()

    with open(r"/home/user2/airflow/dags/DataPinter_Runner/pipeline_assets.json") as f:
        assets_json = json.load(f)
        categories = assets_json["categories"]
        skincare_db =categories["skincare.duckdb"]
        supplement_db =categories["suplemen.duckdb"]
        babycare_db = categories["babycare.duckdb"]
    
    #Transform
    #df = df.drop_duplicates(subset=['Nama Produk','Nama Toko'])
    #Perform data cleaning

    df = df.drop(columns = ['Gambar','Jumlah Stok','Nilai Stok','Slug'],errors = 'ignore')
    df['Nama Produk'] = df['Nama Produk'].fillna('')

    #Clean product name data
    keyword_processor = DataCleaner.NLPCleaner.LoadStopwords(file = STOPWORDS_PATH)

    #Automaton for string matching
    automaton_skcare = build_brand_automaton(brand_list_skcare)
    automaton_supp = build_brand_automaton(brand_list_supp)
    automaton_babycare = build_brand_automaton(brand_list_babycare)
    
    #product name data cleaning
    df['Nama Produk'] = df['Nama Produk'].apply(lambda text:remove_bracket_noise(text))
    df['Nama Produk'] = df['Nama Produk'].apply(lambda text:DataCleaner.NLPCleaner.CleaningText(text))
    df['Nama Produk'] = df['Nama Produk'].apply(lambda text:DataCleaner.NLPCleaner.CleanStopwords(text,keyword_processor))
    df['Nama Produk Pendek'] = df['Nama Produk'].apply(lambda text:DataCleaner.NLPCleaner.ShortenProductString(text,query_keywords,
                                                                                                       10))
    log.info(f"Before Entering Brand Extraction Function")
    # extract brand and brand filtering
    # Ganti semua bagian pengecekan DB

    query_list = [query_keywords] if isinstance(query_keywords, str) else query_keywords

    if 'Brand' not in df.keys():
        if any(kw in supplement_db for kw in query_list):
            df["Brand"] = df["Nama Produk"].apply(lambda x: extract_brand(text = x,automaton=automaton_supp,
                                                                          fuzzy_threshold = 70,brand_list=brand_list_supp,method = "fuzzy"))
        elif any(kw in skincare_db for kw in query_list):
            df["Brand"] = df["Nama Produk"].apply(lambda x: extract_brand(text = x,automaton=automaton_skcare,
                                                                      fuzzy_threshold = 70,brand_list=brand_list_skcare,
                                                                      method = "fuzzy"))
        elif any(kw in babycare_db for kw in query_list):
            df["Brand"] = df["Nama Produk"].apply(lambda x: extract_brand(text = x,automaton=automaton_babycare,
                                                                      fuzzy_threshold = 70,brand_list=brand_list_babycare,
                                                                      method = "fuzzy"))
        else:
            df["Brand"]="Unknown"
    else:
        df['Brand'] = df['Brand'].str.lower()

    log.info(query_keywords)

    log.info(f"Branch masuk: supplement={any(kw in supplement_db for kw in query_keywords)}, skincare={any(kw in skincare_db for kw in query_keywords)}, babycare={any(kw in babycare_db for kw in query_keywords)}")
    
    log.info(f"Brand sample SETELAH extract: {df['Brand'].head(5).tolist()}")

    df['Brand'] = df['Brand'].replace("Tidak Ada Merek", "Unknown Brand")

    if any(kw in skincare_db for kw in query_list):
        df['Store Type'] = df['Nama Toko'].apply(lambda text:fgen.official_brand_recognizer(brand_list = brand_list_skcare,store_name=text))
    elif any(kw in supplement_db for kw in query_list):
        df['Store Type'] = df['Nama Toko'].apply(lambda text:fgen.official_brand_recognizer(brand_list = brand_list_supp,store_name=text)) 
    else:
        df['Store Type'] = 'Reseller'

    #Check the age of product list                                                                                    store_name = str(text)))
    if 'Tanggal Listing' in df.keys():
        df['Tanggal Listing'] = pd.to_datetime(df['Tanggal Listing'],format="%b %d, %Y")
        df['Umur Listing'] = round((pd.to_datetime('now') - pd.to_datetime(df['Tanggal Listing']))/pd.Timedelta(days = 30),2)

    #Create Price Distributions
    df = fgen.DataDistributions(df = df,column_name = 'Price Distributions',bin_method = 'quantile',column_target_name = 'Harga',bins = 10)
    cols_to_keep = ['Nama Produk',
                    'Nama Produk Pendek',
                    'Brand','Nama Toko',
                    'Umur Listing','Harga Asli',
                    'Harga',
                    'Omset 30 Hari','Penjualan 30 Hari',
                    'Rata-rata Omset per bulan',
                    'Omset Total','Rata-rata Penjualan per bulan',
                    'Penjualan Total',
                    'Rating', 
                    'Wishlist',
                    'URL',
                    'Query Date',
                    'Jumlah Ulasan',
                    'Price Distributions',
                    'Store Type',
                    'ECommerce Platform',
                    'Query Keywords']
    
    df = df[cols_to_keep]
    df['Price Distributions'] = df['Price Distributions'].astype(str)

    df.columns = df.columns.str.lower().str.replace(" ","_")

    return df
