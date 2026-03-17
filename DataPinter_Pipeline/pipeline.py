# ----------------------PRODUCT ANALYSIS DATA PIPELINE-------------------------------
# Module installation
import pandas as pd
import os
import numpy as np
import sys
from kaleido import write_fig_sync
from pathlib import Path
import duckdb
import glob
from datetime import datetime
import re
import json
from sklearn.preprocessing import MinMaxScaler
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools")
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools\DATA PIPELINE\DataPinter_Pipeline\cleaning.py")

from DataCleaner import DataCleaner, FeatureGenerator
from config import PipelineConfig
from queries import QUERY_SALES_BRAND,QUERY_MSHARE_BRAND,QUERY_MPenetration_BRAND,QUERY_PRODUCT_SALES,QUERY_PRODUCT_REV,QUERY_DATAFRAME,PRICE_DIST
from cleaning import FilterDatasetOnKeywords,build_brand_automaton,extract_brand
import html

#Call python file module from extract,transform,load
from transform import transform
from extract import extract_files
from load import LoadDuckDB,ReadLog

#Define Python Module
cleaner = DataCleaner()
NLPCleaner = cleaner.NLPCleaner()
fgen = FeatureGenerator()
scaler = MinMaxScaler()

#LIST CATEGORIES
SKINCARE_CATEGORIES = {'toner','serum','cleanser','face wash','sunscreen','moisturizer','men care','parfum','perfume'}
BODYCARE_CATEGORIES = {'body wash','body lotion','body mask'}
HAIRCARE_CATEGORIES = {'hair','rambut','conditioner','shampoo','hair mask','hair serum'}
LIPCARE_CATEGORIES = {'lip serum','lip cream',"lip balm"}
DECORATIVE_CATEGORIES= {'lip tint','lip matte','lip vinyl','lip stick','cushion','foundation'}
SUPLEMEN_CATEGORIES = {'suplemen', 'kapsul','vitamin','creatine','fitness','gym','whey protein'}

#Fill the address of the data 1path
DATA_PATH =PipelineConfig.DATA_PATH
DATA_PATH_STR =str(PipelineConfig.DATA_PATH)
STOPWORDS_PATH =PipelineConfig.STOPWORDS_PATH 

BRAND_PATH_CSV=PipelineConfig.BRAND_PATH
BRAND_DATA = pd.read_csv(BRAND_PATH_CSV)

BRAND_DATA =BRAND_DATA.applymap(lambda x: html.unescape(x) if isinstance(x, str) else x)
# remove punctuation
BRAND_DATA = BRAND_DATA.applymap(lambda x: re.sub(r"[^\w\s]", "", x) if isinstance(x, str) else x)
brand_list = [b.strip().lower() for b in BRAND_DATA['product_brands'] if isinstance(b,str)]

#Read Stopwords Path
with open(STOPWORDS_PATH,'r') as f:
    STOPWORDS_LIST = f.read().splitlines()

print(STOPWORDS_LIST)

# -------------------------------------------------------PLACE INPUT WITHIN THIS LINE -------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------DATA PIPELINE CODE------------------------------------------------------------------

os.makedirs(PipelineConfig.TARGET_PATH,exist_ok = True)
print(PipelineConfig.TARGET_PATH)

for file in os.listdir(DATA_PATH):

    full_path = os.path.join(DATA_PATH,file)

    if ReadLog(DB_LOG=PipelineConfig.PIPELINE_DB_LOG, file_name=file):
        print(f"SKIPPING {file}")
        continue
    else:
    #Extract files and read it
        df = extract_files(full_path)

        #Perform data cleaning
        df = df.drop(columns = ['Gambar','Jumlah Stok','Nilai Stok'],errors = 'ignore')
        df['Nama Produk'] = df['Nama Produk'].fillna('')
        df['Nama Produk'] = df['Nama Produk'].astype(str).str.strip().apply(lambda x: NLPCleaner.CleanStopwords(x, STOPWORDS_LIST))

        #Parse Metadata from file name
        query_datasource, query_keywords,query_date = cleaner.ParseMetadata(filename = str(file))
        print(f'{file}, columns = {df.columns}')

        df['ECommerce Platform'] = query_datasource
        df['Query Keywords'] = query_keywords
        df['Query Date'] = query_date

        #Filter the dataset, exclude all irrelevant files
        clean_keywords = query_keywords.replace("_"," ").lower().strip()

        df = FilterDatasetOnKeywords(df,'Nama Produk',clean_keywords)
        
        df['Nama Produk'] = df['Nama Produk'].apply(lambda text:cleaner.ProductName_Clean(text))
        df['Nama Produk'] = df['Nama Produk'].apply(lambda text:text.title())
        
        df['Nama Produk'] = df['Nama Produk'].apply(lambda text: text.lower())

        automaton = build_brand_automaton(brand_list)

        # extract brand
        if 'Brand' not in df.keys():
            df["Brand"] = df["Nama Produk"].apply(lambda x: extract_brand(text = x,automaton=automaton,brand_list=brand_list))
            df['Brand'] = df['Brand'].str.lower()

        df = df.loc[~(df['Brand']=="Tidak Ada Merek")]

        #Create new columns using official_brand_recognizer from FeatureGenerator
        df['Store Type'] = df['Nama Toko'].apply(lambda text:fgen.official_brand_recognizer(brand_list = brand_list,store_name=text)) 
        
        #Check the age of product list                                                                                    store_name = str(text)))
        if 'Tanggal Listing' in df.keys():
            df['Tanggal Listing'] = pd.to_datetime(df['Tanggal Listing'],format="%b %d, %Y")
            df['Umur Listing'] = round((pd.to_datetime('now') - pd.to_datetime(df['Tanggal Listing']))/pd.Timedelta(days = 30),2)

        #Create Price Distributions
        df = fgen.DataDistributions(df = df,column_name = 'Price Distributions',bin_method = 'quantile',column_target_name = 'Harga',bins = 10)

        cols_to_keep = ['Nama Produk','Brand','Nama Toko','Lokasi','Tren','Umur Listing','Harga Asli','Harga','Omset 30 Hari','Penjualan 30 Hari','Rata-rata Omset per bulan', 'Omset Total','Rata-rata Penjualan per bulan','Penjualan Total',
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

        #TRANSFORM DATA
        df = transform(df)
        
        # Check whether filename contain certain character
        # If it contains certain char, categorize it into different .db files
        print(f'clean_keywords :{clean_keywords}')
        if any(k in clean_keywords for k in HAIRCARE_CATEGORIES):
            LoadDuckDB(
                df,
                db_path =PipelineConfig.PIPELINE_DB_HAIRCARE,
                table_name = f"{query_datasource}_{query_keywords}",
                DB_LOG=PipelineConfig.PIPELINE_DB_LOG,
                file_name=file,
                file_path=str(full_path))
        elif any(k in clean_keywords.split() for k in BODYCARE_CATEGORIES):
            LoadDuckDB(
                df,
                db_path =PipelineConfig.PIPELINE_DB_BODYCARE,
                table_name = f"{query_datasource}_{query_keywords}",
                DB_LOG=PipelineConfig.PIPELINE_DB_LOG,
                file_name=file,
                file_path=str(full_path))
        elif any(k in clean_keywords.split() for k in SKINCARE_CATEGORIES):
            #Load per file
            LoadDuckDB(
                df,
                db_path = PipelineConfig.PIPELINE_DB_SKCARE,
                table_name = f"{query_datasource}_{query_keywords}",
                DB_LOG=PipelineConfig.PIPELINE_DB_LOG,
                file_name=file,
                file_path=str(full_path))
        elif 'baby' in clean_keywords:
            LoadDuckDB(
                df,
                db_path = PipelineConfig.PIPELINE_DB_BABYCARE,
                table_name = f"{query_datasource}_{query_keywords}",
                DB_LOG=PipelineConfig.PIPELINE_DB_LOG,
                file_name=file,
                file_path=str(full_path))
        elif any(k in clean_keywords for k in LIPCARE_CATEGORIES):
            LoadDuckDB(
                df,
                db_path =PipelineConfig.PIPELINE_DB_LIPCARE,
                table_name = f"{query_datasource}_{query_keywords}",
                DB_LOG=PipelineConfig.PIPELINE_DB_LOG,
                file_name=file,
                file_path=str(full_path))
        elif any(k in clean_keywords for k in DECORATIVE_CATEGORIES):
            LoadDuckDB(
                df,
                db_path =PipelineConfig.PIPELINE_DB_DECORATIVE,
                table_name = f"{query_datasource}_{query_keywords}",
                DB_LOG=PipelineConfig.PIPELINE_DB_LOG,
                file_name=file,
                file_path=str(full_path))
        else:
            LoadDuckDB(
                df,
                db_path =PipelineConfig.PIPELINE_DB_SUPLEMEN,
                table_name = f"{query_datasource}_{query_keywords}",
                DB_LOG=PipelineConfig.PIPELINE_DB_LOG,
                file_name=file,
                file_path=str(full_path))

#Creating Spider Plot for Top Brand Analysis
files = glob.glob(DATA_PATH_STR + '/*.xlsx')
all_df = pd.concat([pd.read_excel(f) for f in files],ignore_index = True)

#Run Queries, place it into target PATH for saving data for Analysis Deck
#Connecting to DuckDB
conn = duckdb.connect(PipelineConfig.DB_PATH)

#Querying
SalesBrand = conn.execute(QUERY_SALES_BRAND).fetchdf()
SalesBrand.to_csv(os.path.join(PipelineConfig.TARGET_PATH,"SalesBrand.csv"),index = False)

MShareBrand = conn.execute(QUERY_MSHARE_BRAND).fetchdf()
MShareBrand.to_csv(os.path.join(PipelineConfig.TARGET_PATH,"MShareBrand.csv"),index = False)

MPentBrand = conn.execute(QUERY_MPenetration_BRAND).fetchdf()
MPentBrand.to_csv(os.path.join(PipelineConfig.TARGET_PATH,"MPentBrand.csv"), index = False)

ProductSales = conn.execute(QUERY_PRODUCT_SALES).fetchdf()
ProductSales.to_csv(os.path.join(PipelineConfig.TARGET_PATH,"ProductSales.csv"), index = False)

ProductRev = conn.execute(QUERY_PRODUCT_REV).fetchdf()
ProductRev.to_csv(os.path.join(PipelineConfig.TARGET_PATH,"ProductRev.csv"),index =False)

PriceDist = conn.execute(PRICE_DIST).fetchdf()
PriceDist.to_csv(os.path.join(PipelineConfig.TARGET_PATH,"PriceDist.csv"), index = False)

df = conn.execute(QUERY_DATAFRAME).fetchdf()

#Create plot
dataviz = FeatureGenerator().DataViz()
df = df[df['store_type'] == 'Official Store']

#Create a metric
MetricDF = df.loc[~(df['rating'] == 0.00)].groupby('brand').agg({
    'rata_rata_penjualan_per_bulan':'sum',
    'omset_30_hari':'sum',
    'penjualan_30_hari':'sum',
    'harga':'mean',
    'jumlah_ulasan':'sum',
    'umur_listing':'max',
    'rating':'mean',
    'nama_produk':'nunique',
    'store_type':'count'
})
if MetricDF.shape[0] == 0:
    print(f'Scaling Skipped, Rows Found {MetricDF.shape[0]}')
else:
    MetricDF['ASP'] = np.where(MetricDF['omset_30_hari'] == 0,0, MetricDF['omset_30_hari'] / MetricDF['penjualan_30_hari'])
    MetricDF['Customer Acquired per Month'] = np.where(MetricDF['umur_listing'] == 0, 0, MetricDF['jumlah_ulasan'] / MetricDF['umur_listing'])
    MetricDF['Market Penetration'] = np.where(MetricDF['jumlah_ulasan'].sum() == 0, 0, MetricDF['jumlah_ulasan']*100/MetricDF['jumlah_ulasan'].sum())

    MetricDF.rename(columns = {
        'nama_produk':'Varian Produk',
        'store_type':'Reseller Count'
    },inplace = True)

    MetricDF = MetricDF.sort_values(by = 'rata_rata_penjualan_per_bulan',ascending = False)

    print(MetricDF.columns)
    MetricDF[['Rata-rata Penjualan per bulan_scaled',
            'Reseller Count_scaled',
            'Umur Produk_Scaled',
            'Varian Produk_scaled',
            'Harga_scaled',
            'Rating_scaled',
            'ASP_scaled',
            'Customer Acquired per Month_scaled',
            'Market Penetration_scaled']] = scaler.fit_transform(MetricDF[['rata_rata_penjualan_per_bulan',
                                                                            'Reseller Count',
                                                                            'umur_listing',
                                                                            'Varian Produk',
                                                                            'harga',
                                                                            'rating',
                                                                            'ASP',
                                                                            'Customer Acquired per Month',
                                                                            'Market Penetration']])
    #Plot spider
    TopBrandMetric = MetricDF.reset_index().sort_values(by = 'rata_rata_penjualan_per_bulan',ascending = False).head(5)
    TopBrand = TopBrandMetric['brand'].tolist()
    MetricDF.rename(columns = {
        'Rata-rata Penjualan per bulan_scaled':'Rerata Penjualan per Bulan',
        'Umur Produk_Scaled':'Umur Produk',
        'Reseller Count_scaled':'Jumlah Reseller',
        'Varian Produk_scaled':'Jumlah Varian Produk',
        'Harga_scaled':'Harga Rata-Rata',
        'Rating_scaled':'Rating Brand',
        'ASP_scaled':'Average Selling Price',
        'Customer Acquired per Month_scaled':'Jumlah Customer per Bulan'
    },inplace = True)

    #Check brand strength
    for brand in TopBrand:
        name = f'{brand}Strength.png'
        plot = dataviz.plot_spider(category = brand,data = MetricDF,columns = ['Rerata Penjualan per Bulan','Jumlah Reseller','Jumlah Varian Produk','Umur Produk','Harga Rata-Rata','Rating Brand','Average Selling Price','Jumlah Customer per Bulan'])
        write_fig_sync(plot,path = os.path.join(PipelineConfig.TARGET_PATH,name))