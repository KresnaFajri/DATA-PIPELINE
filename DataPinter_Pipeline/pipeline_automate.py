# ----------------------PRODUCT ANALYSIS DATA PIPELINE-------------------------------
# Module installation
import sys
import pandas as pd
import os
import duckdb
import glob
import json
import logging
from sklearn.preprocessing import MinMaxScaler
sys.path.append(r"/home/user2/airflow")
sys.path.append(r"/home/user2/airflow/dags/DataPinter_Runner")
from DataCleaner import DataCleaner, FeatureGenerator
from analytics import *
from utils import FilterDatasetOnKeywords, SearchDBPath,DirectoryGenerator
from transform import transform
from extract import extract_files
from load import LoadDuckDB,ReadLog,CreateLog
from config import AutomatePipelineConfig
from automate_queries import *
from scipy.stats import entropy

#Call python file module from extract,transform,load
#Define Python Module
#LIST CATEGORIES
#SKINCARE_CATEGORIES = {'skincare','toner','serum','cleanser','face wash','sunscreen','moisturizer','men care','parfum','perfume','body wash','body lotion','body mask',
                      # 'hair','rambut','conditioner','shampoo','hair mask','hair serum','lip serum','lip cream',"lip balm",
                      # 'lip tint','lip matte','lip vinyl','lip stick','cushion','foundation'}
#BABYCARE_CATEGORIES = {"baby oil","baby moisturizer","rub cream"}
#SUPLEMEN_CATEGORIES = {'suplemen', 'kapsul','vitamin','creatine','fitness','gym','whey protein','eye cream','asi booster',
                       #'suplemen herbal daya tahan','probiotik','pre biotik herbal','wellness drink','antiinflamasi','suplemen kulit herbal'}

with open(r"/home/user2/airflow/dags/DataPinter_Runner/pipeline_assets.json") as f:
    assets_json = json.load(f)
    additional_keywords= assets_json["additional keywords"]

#Fill the address of the data 1path
DATA_PATH =AutomatePipelineConfig.DATA_PATH
DATA_PATH_STR =str(AutomatePipelineConfig.DATA_PATH)

#Does not need context, only need connection to FileSensor.
def run_pipeline():
    cleaner= DataCleaner()
    skip_filter = assets_json["skip filter"]
    categories_json = assets_json["categories"]
    skincare_duckdb = categories_json["skincare.duckdb"]
    babycare_duckdb = categories_json["babycare.duckdb"]
    suplemen_duckdb = categories_json["suplemen.duckdb"]
    
    for file in os.listdir(DATA_PATH):
        full_path = os.path.join(DATA_PATH,file)

        if not os.path.exists(AutomatePipelineConfig.PIPELINE_DB_LOG):
            CreateLog(AutomatePipelineConfig.PIPELINE_DB_LOG)

        if ReadLog(DB_LOG=AutomatePipelineConfig.PIPELINE_DB_LOG, file_name=file):
            print(f"SKIPPING {file}")
            continue
        else:
            #Extract files and read it
            df = extract_files(full_path)

            #Parse Metadata from file name
            query_datasource, query_keywords,query_date = cleaner.ParseMetadata(filename = str(file))

            df['ECommerce Platform'] = query_datasource
            df['Query Keywords'] = query_keywords
            df['Query Date'] = query_date

            #Filter the dataset, exclude all irrelevant files
            clean_keywords = query_keywords.replace("_"," ").lower().strip()
            additional = additional_keywords.get(clean_keywords)
            if clean_keywords not in skip_filter:
                df = FilterDatasetOnKeywords(df,'Nama Produk',clean_keywords,additional_keywords=additional)
            else:
                print(f"SKIP FILTERING FOR {clean_keywords}")
            #TRANSFORM DATA
            df_transformed = transform(df, query_keywords = query_keywords)
            print("Df Columns after transformation:", df_transformed.columns.tolist())
            # Check whether filename contain certain character
            # If it contains certain char, categorize it into different .db files
            print(f'clean_keywords :{clean_keywords}')

            if any(k in [query_keywords] for k  in babycare_duckdb):
                LoadDuckDB(
                    df_transformed,
                    db_path =AutomatePipelineConfig.PIPELINE_DB_BABYCARE,
                    table_name = f"{query_datasource}_{query_keywords}",
                    DB_LOG=AutomatePipelineConfig.PIPELINE_DB_LOG,
                    file_name=file,
                    file_path=str(full_path))
            elif any(k in [query_keywords] for k in skincare_duckdb):
                LoadDuckDB(
                    df_transformed,
                    db_path=AutomatePipelineConfig.PIPELINE_DB_SKCARE,
                    table_name=f"{query_datasource}_{query_keywords}",
                    DB_LOG=AutomatePipelineConfig.PIPELINE_DB_LOG,
                    file_name=file,
                    file_path=str(full_path))
            else:
                LoadDuckDB(
                    df_transformed,
                    db_path =AutomatePipelineConfig.PIPELINE_DB_SUPLEMEN,
                    table_name = f"{query_datasource}_{query_keywords}",
                    DB_LOG=AutomatePipelineConfig.PIPELINE_DB_LOG,
                    file_name=file,
                    file_path=str(full_path))
                
    files = glob.glob(DATA_PATH_STR + '/*.xlsx')

#Run Queries, place it into target PATH for saving data for Analysis Deck
#Connecting to DuckDB
def run_queries(**context):
    log = logging.getLogger(__name__)
    #Pulling context from pipeline parse gcal_data
    ti = context['ti']

    category_list = ti.xcom_pull(task_ids='parse_gcal_data', key = 'return_value') 
    log.info(category_list)

    with open(r"/home/user2/airflow/dags/DataPinter_Runner/pipeline_assets.json") as f:
        assets_json = json.load(f)
    categories_json = assets_json['categories']
    suplemen_json = categories_json["suplemen.duckdb"]

    for item in category_list:
        category = item['category']
        month = item['month']
        year = item['year']

        START_DATE = f"{year}-{month.zfill(2)}-01"
        END_DATE = f"{year}-{month.zfill(2)}-28"
    
        category_striped = category.replace(" ","_").lower() #Use this variable to connect requested data from GCal to DuckDB Tables

        #Checking .db to search what kind of categories cached
        conn = duckdb.connect(SearchDBPath(BASE_RAW =AutomatePipelineConfig.BASE_PATH_DB,
                                            category=category),read_only=True)
        
        category = category.replace(" ","") #Use this variable to create directories 
        TARGET_PATH = DirectoryGenerator(AutomatePipelineConfig.BASE_PATH_TARGET,
                                    category = category,
                                    month=month,
                                    year = year)

        if category_striped in suplemen_json:
            queries = {'SalesBrand.csv':lambda:QUERY_BRAND_SALES_UNFILTERED(category_striped,START_DATE,END_DATE,AutomatePipelineConfig.Top_N),
                       'ProductSales.xlsx':lambda:QUERY_PRODUCT_SALES_UNFILTERED(category_striped,START_DATE,END_DATE,AutomatePipelineConfig.Top_N),
                       'MShareBrand.csv':lambda:QUERY_MSHARE_BRAND_UNFILTERED(category_striped,START_DATE,END_DATE,AutomatePipelineConfig.Top_N),
                       'MPenetrationBrand.csv':lambda:QUERY_MPenetration_UNFILTERED(category_striped,START_DATE,END_DATE,AutomatePipelineConfig.Top_N),
                       'ProductRev.csv':lambda:QUERY_PRODUCT_REV_UNFILTERED(category_striped,START_DATE,END_DATE,AutomatePipelineConfig.Top_N),
                       'PriceDistrib.csv':lambda:PRICE_DIST_UNFILTERED(category_striped,START_DATE, END_DATE)
                       }
        else:
            queries = {'SalesBrand.csv':lambda:QUERY_SALES_BRAND(category_striped,START_DATE,END_DATE,AutomatePipelineConfig.Top_N),
                       'ProductSales.xlsx':lambda:QUERY_PRODUCT_SALES(category_striped,START_DATE,END_DATE,AutomatePipelineConfig.Top_N),
                       'MShareBrand.csv':lambda:QUERY_MSHARE_BRAND(category_striped,START_DATE,END_DATE,AutomatePipelineConfig.Top_N),
                       'MPenetrationBrand.csv':lambda:QUERY_MPenetration_BRAND(category_striped,START_DATE,END_DATE,AutomatePipelineConfig.Top_N),
                       'ProductRev.csv':lambda:QUERY_PRODUCT_REV(category_striped,START_DATE,END_DATE,AutomatePipelineConfig.Top_N),
                       'PriceDistrib.csv':lambda:PRICE_DIST(category_striped,START_DATE,END_DATE)
                       }

            
        for filename,query_func in queries.items():
            data = conn.execute(query_func()).fetchdf()
            filepath = os.path.join(TARGET_PATH,filename)
            if "MShare" in filename:
                #Calculate HHINDEX
                proportions = data['OmsetPerBrand']/data['OmsetPerBrand'].sum()
                sum_square_mshare = ((proportions*100)**2).sum()
                data['HHIndex'] = sum_square_mshare.sum()

                #Calculate Shannon's Entropy
                data['Shannons_Entropy'] = entropy(proportions,base=2)
            if filename.endswith(".xlsx"):
                data.to_excel(os.path.join(TARGET_PATH,filepath),index=False)
            else:
                data.to_csv(os.path.join(TARGET_PATH,filepath),index=False)
            
#Use analytics module, to generate weakness and strength analytics
#Query all dataframes based on QUERY_DATAFRAME in queries
def run_analytics(**context):
    fgen = FeatureGenerator()
    log = logging.getLogger(__name__)
    ti = context['ti']

    category_list = ti.xcom_pull(task_ids= 'parse_gcal_data',
                                  key = 'return_value')
    
    with open(r"/home/user2/airflow/dags/DataPinter_Runner/pipeline_assets.json") as f:
        assets_json = json.load(f)

    with open(r"/home/user2/airflow/dags/DataPinter_Runner/analytics.json") as o:
        analytics_json = json.load(o)

    #Further Analytics : Analytics that involved rigorous process of product differentiation and categorization
    further_analytics = analytics_json['further analytics']
    duckdb_database_name = assets_json['categories']
    #categorizing which data goes to which database
    category_groups = assets_json["category_groups"]

    #check which product category that must be skipped for "Official Store and Reseller" categorization
    skip_official_store_check = assets_json["skip_official_store_check"]
    skip_category_analysis = analytics_json["skip_category_analysis"]

    for item in category_list:
        category = item['category']
        month = item["month"]
        year = item["year"]
        is_big = item.get('is_big',False)

        START_DATE = f"{year}-{month.zfill(2)}-01"
        END_DATE = f"{year}-{month.zfill(2)}-28"

        TARGET_PATH = DirectoryGenerator(AutomatePipelineConfig.BASE_PATH_TARGET,
                                category = category,
                                month = month,
                                year = year)
    
        category = category.replace(" ","_").lower()
        conn = duckdb.connect(SearchDBPath(BASE_RAW = AutomatePipelineConfig.BASE_PATH_DB, category=category))

        df = conn.execute(QUERY_DATAFRAME(category)).fetchdf()
        get_top_sales = conn.execute(QUERY_SALES_BRAND(category, START_DATE, END_DATE,limit=20)).fetchdf()
        brand_list = (get_top_sales.sort_values('penjualan_30_hari',
                                               ascending=False)['brand'].drop_duplicates().head(20).tolist())
        if category in skip_official_store_check:
            WeaknessStrengthAnalytics(df,target_path = DirectoryGenerator(BASE_PATH = AutomatePipelineConfig.BASE_PATH_TARGET,
                                                                      category = category,
                                                                      month = month,
                                                                      year = year),toggle_official_check=False)
        else:
            WeaknessStrengthAnalytics(df,target_path = DirectoryGenerator(BASE_PATH = AutomatePipelineConfig.BASE_PATH_TARGET,
                                                                      category = category,
                                                                      month = month,
                                                                      year = year),toggle_official_check=True)
        #if it contains [BIG] flags, branching to BIG CATEGORY analytical process (skincare, bodycare, haircare, pet care, babycare, multivitamins)
        if is_big:
            sub_categories = category_groups.get(category,{}).get("filter_categories",[])
            if not sub_categories:
                log.warning(f"[BIG] Categories doesn't have any sub categories in JSON files, skipping Category Analytics")
    
            else:
                CategoryAnalysis(TARGET_PATH = DirectoryGenerator(BASE_PATH = AutomatePipelineConfig.BASE_PATH_TARGET,
                                                                  category = category,
                                                                  month = month,
                                                                  year = year),
                                                                  category = category,
                                                                  brand_list = brand_list,
                                                                  filter_category = sub_categories)
        #Analyzing for SMALL CATEGORY (moisturizer,serum,hair serum, shampoo, conditioner,toner,acne spot,clay mask,deodorant)
        else: 
            if category in skip_category_analysis:
                log.info(f"Skipping Category Analysis for {category} as it is listed in skip_category_analysis")
            else:
                CategoryAnalysis(TARGET_PATH = DirectoryGenerator(BASE_PATH = AutomatePipelineConfig.BASE_PATH_TARGET,
                                                                  category = category,
                                                                  month = month,
                                                                  year = year),
                                                                  category = category,
                                                                  brand_list = brand_list,
                                                                  filter_category = None)
        result_df = FurtherAnalytics(df,
                            product_column_name = 'nama_produk',
                            category =  category,
                            assets_json = analytics_json)
        
        if category not in further_analytics.keys():
            log.info(f'Searched {category} category not found in further analytics JSON.Skipping further analytics for {category}...')
            log.info(f'❗Please modify analytics.JSON if you think this is a mistake.')
            continue
        
        for process in further_analytics[category]:  #Indexing every analytical process inside JSON files
            process = process.replace(" ","_") #Replacing all the spaces in the entry with "_"
            if process not in result_df.columns:
                log.warning(f"{process} is not exist in columns, skipping")
                continue
            
            category_distribution = GetDistrib(result_df,process)
            price_per_category_distribution = GetDistribWithPrice(result_df,
                                                        category_column_name=process,
                                                        price_column='harga', 
                                                        bin_method='quantile',
                                                        bins=10)
            
            top_sold_per_category = GetDistribTopSold(result_df,
                                                        category_column_name=process)
            
            output_path = os.path.join(TARGET_PATH,f"{process}.xlsx")

            price_per_category_distribution.to_excel(os.path.join(TARGET_PATH,
                                                                    f"{process}_price_distrib.xlsx"),
                                                                    index=False)
            top_sold_per_category.to_excel(os.path.join(TARGET_PATH,
                                                        f"{process}_top_sold.xlsx"),
                                                        index=False)
            
            category_distribution.to_excel(output_path,index=False)

            #Logging the result of analytics process
            log.info(f"Saved distribution for '{process}' to {TARGET_PATH}")
            log.info(f"Saved Price Analysis per Category in {output_path}")

        #Analyze product (SKU) to define which product produce highest gmv for the brands?
            category_striped = category.replace(" ","_").lower()
            for db,db_category in duckdb_database_name.items():
                if category_striped not in db_category:
                    log.info(f"Category {category_striped} not found in {db}, skipping GMV Portion Analytics")
                    continue
                else:
                    if db == "suplemen.duckdb":
                        is_supplement = True
                    else:
                        is_supplement = False
                    #Run GMV Dependency Analytics
                    GMVPortionAnalytics(
                        database_path = os.path.join(AutomatePipelineConfig.BASE_PATH_DB,db),
                        target_path = TARGET_PATH,
                        category=category_striped,
                        time_start=START_DATE,
                        time_end=END_DATE,
                        limit=10,
                        per_sku=True,
                        is_supplement = is_supplement)

                    log.info(f"Saved GMV Portion Analytics of {category} in {TARGET_PATH}")
            
            
