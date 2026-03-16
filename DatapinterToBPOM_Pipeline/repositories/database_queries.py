import traceback
import sys
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools\DATA PIPELINE\Datapinter_BPOM_Pipeline")
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001")
from Tools.DataCleaner import DataCleaner,FeatureGenerator
from config import Config
import pandas as pd
import psycopg2
import os

cleaner = DataCleaner()
NLPCleaner = cleaner.NLPCleaner()
fgen = FeatureGenerator()

STOPWORDS_PATH = r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools\DataCleaner\assets\Skincare Corpora\STOPWORDS.txt"

def get_manufacturer_query(df):
    cur = None
    conn = None
    try:
        print('Connecting to Postgres...')
        if 'brand' not in df.columns:
            raise ValueError('"brand" column not found in DataFrame')
        
        brands = df['brand'].str.lower().unique().tolist()

        conn = psycopg2.connect(
            dbname = Config.DB_NAME,
            user = Config.USER,
            password = Config.PASSWORD,
            host = Config.HOST,
            port = Config.PORT
        )

        cur = conn.cursor()
        #conditions = " OR ".join(["product_brands ILIKE %s"] * len(brands))
        query = f"""
                SELECT
                product_brands as Brand,
                manufacturer_name,
                COUNT(DISTINCT product_name) AS sku_created,
                MIN(submit_date) AS first_submission,
                MAX(submit_date) AS last_submission
                FROM {Config.TABLE_NAME}
                WHERE LOWER(product_brands) = ANY(%s)
                GROUP BY product_brands, manufacturer_name
                ORDER BY sku_created DESC
            """
        cur.execute(query,(brands,))
        results = cur.fetchall()
            
        cur.close()
        conn.close()
            
        df_result = pd.DataFrame(results,columns=[
                "Brand",
                "Manufacturer",
                "Total SKU",
                "First Submission",
                "Last Submission"
            ])
        output_file_name = f"{Config.FILE_NAME_2}_{Config.CATEGORY}.xlsx"
        df_result.to_excel(os.path.join(Config.DATASOURCE_PATH,output_file_name), index=False)
        print(f'Manufacturer Query and Brand Completed. Saved as {output_file_name}')
        print(f'Closing Postgres Connection...')

    except Exception as e:
        print(f'Error: {e}')
        traceback.print_exc()

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_top_products(df):

    #Clean product name using stopwords
    with open(STOPWORDS_PATH,'r') as f:
        STOPWORDS_LIST = f.read().splitlines()

    conn = None
    cur = None

    try:
        print('Connecting to Postgres...')
        conn = psycopg2.connect(
            dbname=Config.DB_NAME,
            user=Config.USER,
            password=Config.PASSWORD,
            host=Config.HOST,
            port=Config.PORT
        )

        cur = conn.cursor()
        enriched_results = []

        print('Reading Excel File')
        df = pd.read_csv(os.path.join(Config.DATASOURCE_PATH, Config.EXCEL_FILENAME_1))
        df.columns = df.columns.str.strip()
        print(df.columns)
        if 'nama_produk' not in df.columns or 'brand' not in df.columns:
            raise ValueError('"nama_produk" and "brand" columns not found')

        
        for _, row in df.iterrows():
            product = row['nama_produk']
            brand = row['brand']

            substrings = NLPCleaner.ExtractName(
                product,
                stopwords=STOPWORDS_LIST,
                max_words = 5,
                substring_count=5,
                min_combination=2)
            
            found = False

            for sub in substrings:
                query = f"""
                    SELECT 
                    manufacturer_name, 
                    submit_date,
                    product_package
                    FROM bpom_products
                    WHERE product_brands ILIKE %s
                    AND product_name ILIKE %s
                    LIMIT 1
                """

                cur.execute(query, (f"%{brand}%", f"%{sub}%"))
                result = cur.fetchone()

                if result:
                    manufacturer_name,submit_date,product_package = result
                    found = True
                    break

                else:
                    manufacturer_name,submit_date,product_package = 'NOT FOUND','NOT FOUND','NOT FOUND'

            enriched_results.append({
                'manufacturer_name': manufacturer_name,
                'Volume Variant': product_package,
                'BPOM Submission Date':submit_date
            })

        df_result = pd.concat([df, pd.DataFrame(enriched_results)], axis=1)

        output_file_name = f"{Config.FILE_NAME}_{Config.CATEGORY}.xlsx"
        df_result.to_excel(os.path.join(Config.DATASOURCE_PATH,output_file_name), index=False)

        print(f"Data Searching Completed. Saved as {output_file_name}")

    except Exception as e:
        print(f'Error: {e}')
        traceback.print_exc()

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()