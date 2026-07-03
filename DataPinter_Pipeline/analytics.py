# ANALYTICAL MODULE
# USE THIS ANALYTICS TO DEEPEN ANALYSIS IN E-COMMERCE DATA
# ALWAYS USE STATICMETHOD DECORATOR FOR ALL FUNCTION IN THIS CLASS
import sys
sys.path.append(r"/home/user2/airflow")
import os
import logging
import logging
import json
import duckdb
import numpy as np
import psycopg2
import pandas as pd
import plotly.graph_objects as go
from dags.DataPinter_Runner.utils import *
from config import AutomatePipelineConfig
from kaleido import write_fig_sync
from DataCleaner import FeatureGenerator
from sklearn.preprocessing import MinMaxScaler
from automate_queries import *

#IO Type of python function

#create distribution of each column data, and save it using the same name of the analytical/categorical analysis process
def GetDistrib(df,column_name):
    log = logging.getLogger(__name__)
    """
    Only works in categorical data!
    df(pd.DataFrame): DataFrame of data that want to be analyzed the distributions
    column_name(df.columns):DataFrame columns, must be filled with name of column which filled with VARCHAR/string data.
    """
    result = df.groupby(column_name).agg({
        "nama_produk":'count'
    }).reset_index()
    return result

def GetDistribWithPrice(df,
                        category_column_name,
                        price_column, bin_method,
                        bins=10):
    """
    Calculate price distributions within new categorical distribution

    1.df(pd.DataFrame):Input the Dataframe (must contain categories and price)
    2.category_column_name(str):Input the categorical,
    3.price_column(str):Input the price column, only thSe string, and it must be contained within table columns!
    4.bin_method("quantile" or "sturges")
    """
    fgen = FeatureGenerator()

    df_copy = df.copy()

    df_copy = fgen.DataDistributions(
        df = df_copy,
        column_name="_price_bin",
        column_target_name=price_column,
        bin_method=bin_method,
        bins=bins)
    
    if "_price_bin" not in df_copy.columns:
        log.warning(f"Failed in creating 'price_bin' columns, skipping Price Distributions")
    
    result = (df_copy.groupby([category_column_name,'_price_bin']).agg(
        jumlah_produk=('nama_produk','count')).reset_index().rename(
            columns={category_column_name:'kategori',
                '_price_bin':'rentang_harga'
            }))
    df_copy.drop(columns=['_price_bin'],inplace=True)
    return result

def GetDistribTopSold(df,category_column_name):
    df_copy = df.copy()

    result = (df_copy.groupby(category_column_name).agg(
        sum_sold =('penjualan_30_hari','sum')).reset_index().rename(
            columns={category_column_name:'kategori'}))
    return result

    
#Weakness and Strength Analytics (for brand analysis)
def WeaknessStrengthAnalytics(df,target_path,toggle_official_check=False):
    #defining module
    scaler = MinMaxScaler()
    # Additional Analytics : Strength And Weaknesses
    # CAN ONLY BE USED ON DATAPINTER .csv DATA ONLY

    dataviz = FeatureGenerator().DataViz()
    if toggle_official_check:
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
        scaled_columns = ['Rata-rata Penjualan per bulan_scaled',
                'Reseller Count_scaled',
                'Umur Produk_Scaled',
                'Varian Produk_scaled',
                'Harga_scaled',
                'Rating_scaled',
                'ASP_scaled','Customer Acquired per Month_scaled','Market Penetration_scaled']
        
        scale_columns = ['rata_rata_penjualan_per_bulan','Reseller Count','umur_listing',
                                                                                'Varian Produk',
                                                                                'harga',
                                                                                'rating','ASP','Customer Acquired per Month',
                                                                                'Market Penetration']
        MetricDF[scaled_columns] = scaler.fit_transform(MetricDF[scale_columns])
        
        #MetricDF.to_excel(os.path.join(target_path,"BrandMetric.xlsx"))

        #Plot spider
        TopBrandMetric = MetricDF.reset_index().sort_values(by = 'rata_rata_penjualan_per_bulan',ascending = False).head(15)
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
            write_fig_sync(plot,path = os.path.join(target_path,name))
 
#Analytics for Category Analysis, to analyze the category based on BPOM Database, and compare the brand performance based on the variety of product they have in the market
def CategoryAnalysis(TARGET_PATH, brand_list,category,filter_category=None):
    def CheckBrandExist(conn,view_name, brand):
        query = f"SELECT 1 FROM {view_name} WHERE LOWER(product_brands) ILIKE %s"
        params = (f'%{brand}%',)

        with conn.cursor() as cursor:
            cursor.execute(query,params)
            result = cursor.fetchone()
            return result is not None   
        
    log =  logging.getLogger(__name__)
    fgen = FeatureGenerator()
    os.makedirs(TARGET_PATH, exist_ok=True)  # pastikan folder ada

    #Read Json Files
    with open(r'/home/user2/airflow/dags/DataPinter_Runner/pipeline_assets.json') as f:
        assets_json = json.load(f)
        categories_json = assets_json['postgres_view']
        skincare_categories = categories_json['skincare_db']   
        babycare_categories = categories_json['BabyCare_DB']
        supplement_categories = categories_json['Supplement_DB']

    # Mapping category → query & view_name
    category_map = {
        **{cat: ("SELECT * FROM skincare_db", "skincare_db") for cat in skincare_categories},
        **{cat: ("SELECT * FROM BabyCare_DB", "BabyCare_DB") for cat in babycare_categories},
        **{cat: ("SELECT * FROM Supplement_DB", "Supplement_DB") for cat in supplement_categories},
    }

    if category not in category_map:
        raise ValueError(f"Category '{category}' tidak ditemukan di semua DB.")

    query, view_name = category_map[category]

    # ✅ Pakai with agar koneksi otomatis ditutup
    with psycopg2.connect(
        dbname=AutomatePipelineConfig.POSTGRES_DBNAME,
        host=AutomatePipelineConfig.POSTGRES_HOST,
        port=AutomatePipelineConfig.POSTGRES_PORT,
        user=AutomatePipelineConfig.POSTGRES_USER,
        password=AutomatePipelineConfig.POSTGRES_PASSWORD) as conn:
        
        conn.autocommit = True
        print("Connection to BPOM Database established successfully.")

        with conn.cursor() as cursor:
            cursor.execute(query)
            fetch_data = cursor.fetchall()
            fetch_columns = [desc[0] for desc in cursor.description]

        df_all = pd.DataFrame(fetch_data, columns=fetch_columns)
        # Normalisasi index ke uppercase saat bikin matriks
        if filter_category:
            df_all = df_all[df_all['skincare_category'].isin(filter_category)]
            if df_all.empty:
                log.warning(f"BIG CATEGORY [BIG] isn't exist for category {category}")
                return

        ProductVar_Mat = (df_all.groupby(['product_brands','skincare_category'])['product_id']
                        .count()
                        .reset_index()
                        .pivot(index='product_brands', columns='skincare_category', values='product_id')
                        .fillna(0))

        ProductVar_Mat.index = ProductVar_Mat.index.str.upper()

        # Filter pakai brand_list yang sudah di-upper juga
        brand_list_upper = [b.upper() for b in brand_list]
        ProductVar_Mat = ProductVar_Mat.loc[ProductVar_Mat.index.isin(brand_list_upper)]
        ProductVar_scaled = ProductVar_Mat.div(ProductVar_Mat.max()).fillna(0)
        
        # Loop pakai brand_list_upper agar konsisten
        for brand in brand_list_upper:
            if not CheckBrandExist(conn, view_name=view_name, brand=brand):
                log.info(f"Warning: {brand} tidak ada di View {view_name}.")
                continue

            if brand not in ProductVar_scaled.index:
                log.info(f"Warning: {brand} tidak ada di matriks variasi produk, skip chart.")
                continue

            Spider_ProductVar = fgen.DataViz().plot_spider(
                data=ProductVar_scaled,
                category=brand,
                columns=ProductVar_scaled.columns.tolist())
            # Check if plot is matplotlib or plotly
            try:
                Spider_ProductVar.savefig(os.path.join(TARGET_PATH,f'{brand.lower()}.png'),
                                        dpi=300, bbox_inches='tight')
            except AttributeError:
                Spider_ProductVar.write_image(os.path.join(TARGET_PATH,f'{brand.lower()}.png'),
                                            engine='kaleido')

def FurtherAnalytics(df,product_column_name,
                     category,
                     assets_json,base_path = None):
    """
    df(pd.DataFrame) : DataFrame produk yang sudah diambil
    product_column_name(df.column): Kolom dataframe yg berisi nama produk. 
    Penting utk string matching kategori further analytics
    category(str) : String/text berisi kategori produk yang ingin dianalisis (kategori produk harus ada di DuckDB!)
    assets_json(.JSON) : file json dimana routing table Further Analytics utk masing-masing kategori produk berada
    """
    #Create logging 
    log = logging.getLogger(__name__)
    
    #Getting .json files
    further_analytics = assets_json.get('further analytics',{})

    #Skipping anaytics if product category isn't available in "Further Analytics JSON"
    if category not in further_analytics.keys():
        log.info(f"No further analytics defined {category},skipping analytics")
        return df
    
    #list of analytics to run
    analytics_to_run = further_analytics[category]

    for analytic_name in analytics_to_run:
        keyword_map = assets_json.get(analytic_name)
        if keyword_map is None:
            log.warning(f"Analytics {analytic_name} can't be found")
            continue

        keyword_processor = {label:build_keyword_processor(keywords)
                          for label, keywords in keyword_map.items()}

        col_name = analytic_name.replace(" ","_")
        
        def classify(product_name,keyword_processor=keyword_processor):
            if not isinstance(product_name,str):
                return "General" 
              
            if keyword_processor:
                product_lower = product_name.lower()
                for label, kp in keyword_processor.items():
                    matches = kp.extract_keywords(product_lower)
                    if matches:
                        return label 
                return "General"
        
        df[col_name] = df[product_column_name].apply(classify)

        #Create log, so that the analytical procedures can be visualized through Airflow
        log.info(f"Applied {analytic_name} column for {category} product data")    

    return df

def PricingAnalytics(category,time_start,time_end,filtering_category):
    log = logging.getLogger(__name__)
    
    with open(r"/home/user2/airflow/dags/DataPinter_Runner/pipeline_assets.json") as f:
        assets_json = json.load(f)
        skincare_db = assets_json["categories"]["skincare.duckdb"]
        babycare_db = assets_json["categories"]["babycare.duckdb"]
    
    try:
        if category                                                              in skincare_db:
            conn = duckdb.connect(r'mnt/c/KRESNA/ANALYSIS/SKINCARE/SKINCARE_DUCKDB/skincare.duckdb')
            df = conn.execute(PricingSalesAnalyticsPerCategory(category,
                                                               time_start,
                                                               time_end,
                                                               filtering_category)).fetchdf()
        elif category in babycare_db:
            conn = duckdb.connect(r'mnt/c/KRESNA/ANALYSIS/BABYCARE/BABYCARE_DUCKDB/babycare.duckdb')
            df = conn.execute(PricingSalesAnalyticsPerCategory(category,
                                                               time_start,
                                                               time_end,
                                                               filtering_category)).fetchdf()
        else:
            conn = duckdb.connect(r'/mnt/c/KRESNA/ANALYSIS/SUPPLEMENT/SUPPLEMENT_DUCKDB/suplemen.duckdb')
            df = conn.execute(PricingSalesAnalyticsPerCategory(category,
                                                               time_start,
                                                               time_end,
                                                               filtering_category)).fetchdf()
        conn.close()
        df.to_excel(os.path.join(AutomatePipelineConfig.BASE_PATH_TARGET,f'{category}_PricingAnalytics.xlsx'),index=False)
    except Exception as e:
        log.error(f"Category {category} isn't found in all database, skipping pricing analytics")


def ManufacturePortionAnalytics(category,duckdb_name,threshold=80):
    """
    Analisa brand kosmetik/suplemen utk lihat bikin produknya dimana aja
    1.category:str -> Ambil data kategori dari data tanggal di Google Cal, check apakah ada di pipeline_assets.json utk penempatan di Duckdb database
    2.duckdb_name:str ->Nama database duckdb dimana data brand-brand itu disimpan
    3.threshold:int -> Threshold utk fungsi Fuzzy Similarity Matching, default 80
    """
    log = logging.getLogger(__name__)
    #Connect to BPOM Database
    conn = connect_to_bpom()
    #Read JSON files, search category in pipeline_assets.json
    with open(r"/home/user2/airflow/dags/DataPinter_Runner/pipeline_assets.json") as f:
        assets_json = json.load(f)
        skincare_db = assets_json["categories"]["skincare.duckdb"]
        babycare_db = assets_json["categories"]["babycare.duckdb"]
    try:
        if category in skincare_db:     
            DUCKDB_CONN = duckdb.connect(r"/mnt/c/KRESNA/ANALYSIS/SKINCARE/DUCKDB/skincare.duckdb")
            marketplace_brand_df = DUCKDB_CONN.sql(f"""
                                        SELECT DISTINCT brand FROM 
                                                shopee_{category}""").df()
            cur = conn.cursor()
            cur.execute(f"""
                SELECT 
                    brand_ids,
                    brand_name
                    FROM brand_info
                    WHERE application ILIKE '%Kosmetika%'
                    """)
            
        elif category in babycare_db:
            DUCKDB_CONN = duckdb.connect(r"/mnt/c/KRESNA/ANALYSIS/SKINCARE/DUCKDB/babycare.duckdb")
            marketplace_brand_df = DUCKDB_CONN.sql(
                f"""
                SELECT brands FROM {category}""").df()
            
            cur.execute(
                f"""
                SELECT
                brand_id,
                brand_name
                FROM brand_info
                WHERE application ILIKE '%Kosmetika%'""")
        else:
            DUCKDB_CONN = duckdb.connect(r"/mnt/c/KRESNA/ANALYSIS/SKINCARE/DUCKDB/suplemen.duckdb")
            marketplace_brand_df = DUCKDB_CONN.sql(
                f"""
                SELECT 
                brands
                FROM {category}
                """).df()
            
            #Take data from Postgres Database
            cur.execute(f"""
                    SELECT 
                        brand_id,
                        brand_name,
                        FROM brand_info
                        WHERE appplication ILIKE '%Obat Tradisional%' OR application ILIKE '%pangan%'""")
        #Fetch all data
        bpom_tables = cur.fetchall()
        marketplace_brand_df = marketplace_brand_df[0].tolist()

        bpom_brand_data = [row[1] for row in bpom_tables]
        bpom_brand_ids = {row[1]:row[0] for row in bpom_tables}
        bpom_brand_norm = [normalize_name(n) for n in bpom_brand_data]
        marketplace_brand_norm = [normalize_name(n) for n in marketplace_brand_df]

        match_logs = []
        matched_ids = []

        for i,bpom_brand in enumerate(bpom_brand_norm):
            result = process.extractOne(
                bpom_brand,
                marketplace_brand_norm,
                scorer=fuzz.token_sort_ratio,
                score_cutoff = threshold)
            
            if result:
                match_str,score,idx=result
                original_bpom_name = bpom_brand_data[i]
                original_marketplace_name = marketplace_brand_norm[idx]
                matched_ids.append(bpom_brand_ids[original_bpom_name])
                match_logs.append({
                    'bpom_name':original_bpom_name,
                    'marketplace_name':original_marketplace_name,
                    'score':score
                })
        print(f'✅ Match found : {len(matched_ids)}')

        if match_logs:
            manufacture_portion = []
            for _, row in match_df.iterrows():
                marketplace_name = row["marketplace_name"]
                bpom_name = row["bpom_name"]
                cur.execute("""
                    SELECT
                        manufacturer_name,
                        COUNT(*) AS total_product,
                        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS manufacture_share_pct
                    FROM brand_info
                    WHERE product_brands = %s
                    GROUP BY manufacturer_name
                """, (bpom_name,))

                for manufacturer_name, total_product, share_pct in cur.fetchall():
                    manufacture_portion.append({
                        "marketplace_brand": marketplace_name,
                        "bpom_brand": bpom_name,
                        "manufacturer_name": manufacturer_name,
                        "total_product": total_product,
                        "manufacture_share_pct": share_pct})
                    
            manufacture_portion_df = pd.DataFrame(manufacture_portion)
            manufacture_portion_df.to_csv(F"Manufacture Portion Analytics_{category}.csv",index=False)

    except Exception as e:
        log.info(f'❗Your requested data does not exist in our database')
        log.info(f'❗Please, register your category data into pipeline_assets.json in "categories"')

def GMVPortionAnalytics(database_path,target_path,category,time_start,time_end,limit,is_supplement,per_sku=True):
    log = logging.getLogger(__name__)
    """
    Hitung persentase omzet yang dihasilkan oleh tiap produk dalam suatu brand. Utk cek apakah sumber omzet mereka hanya 1 atau >1
    1.data_path:Save csv file ke PATH yang diberikan oleh user
    2.category:category:str, string file utk define kategori
    3.time_start:datetime, time window utk membatasi jumlah data berdasarkan tanggal awal
    4.time_end:datetime, time window utk membatasi jumlah data berdasarkan tanggal akhir
    5.limit:int, tulis berapa banyak top brand yang ingin dianalisa persentase omzet per produknya
    6.per_sku:bool,default:True. Hitung per SKU, exclude semua data produk yang tergolong bundle
    """
    #Filter based on Top Sales
    conn = duckdb.connect(database_path)

    log.info(f"✅ Connected to DuckDB Database : {database_path}")
    with open(r"/home/user2/airflow/dags/DataPinter_Runner/pipeline_assets.json") as f:
        assets_json = json.load(f)
        categories = assets_json["categories"]

    for db,category_list in categories.items():
        if category in category_list:
            if db != "suplemen.duckdb":
                offcicial_store_filter = True
            else:
                official_store_filter = False

    top_sales = conn.execute(QUERY_SALES_BRAND(category,time_start,time_end,limit=limit,skip_official_store=skip_official_store)).df()

    top_sales_brand = top_sales['brand']

    #Check their top product from top n limit brand, then concat all of the brand into one dataframe
    #after that, convert the dataframe into excel files

    result_list = []
    for brand in top_sales_brand:
        product_pct = conn.execute(CalcDependencyPct(category=category,
                                                     brand = brand,
        time_start=time_start,
        time_end=time_end,
        per_sku=per_sku,
        is_supplement=is_supplement)).df()

        product_pct["brand"] = brand

        result_list.append(product_pct)
        
        final_df = pd.concat(result_list, ignore_index=True)
        final_df.to_csv(os.path.join(target_path,f'{category}_pct_analytics.csv'), index=False)
