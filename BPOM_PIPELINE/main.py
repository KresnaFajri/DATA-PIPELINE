import psycopg2
import numpy as np
import pandas as pd
from psycopg2.extras import execute_batch
from config import Config

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname = Config.DB_NAME,
            host = Config.HOST,
            user = Config.USER,
            password = Config.PASSWORD,
            port = Config.PORT
        )
        print("✅ Connected to PostGres")
        return conn
    except Exception as e:
        print("❌ ERROR: Failed to connect to PostGres Database")
        print(e)

        raise 

def load_data(conn):
    try:
        query = """
        SELECT id,product_name
        FROM bpom_products
        """

        df = pd.read_sql(query,conn)

        print(f"LOADED {len(df)} rows")

        return df
    
    except Exception as e:
        print("❌ ERROR:Faild to load data")
        print(e)

        raise



def skincare_categorizer_function(df, column_name):
    foundation_cond = df[column_name].str.contains('foundation',na =False, case = False)
    mask_cond =  df[column_name].str.contains('mask',na = False, case = False)
    lip_cond = df[column_name].str.contains(r'(?=.*lip)(?=.*serum|balm)',case = False, na = False)
    toner_cond = df[column_name].str.contains('toner|essence toner|acne toner', na = False, case = False) 
    perf_cond= df[column_name].str.contains('toilette|toilet|eau de', na = False,case=False)
    soap_cond = df[column_name].str.contains('soap|sabun|bodywash|handwash|body wash',na = False,case = False)
    cleanser_cond = df[column_name].str.contains('cleanser|micellar|facial wash|facewash|face wash|facialwash',na = False, case = False)
    moist_cond = df[column_name].str.contains('moisturizer|lotion|cream|moist', na = False, case =False)
    men_cond = df[column_name].str.contains('shave|shaving', na = False, case =False)
    sunscreen_cond = df[column_name].str.contains(Config.SUNSCREEN_REGEX, na = False, case =False)
    deo_cond = df[column_name].str.contains('deodorant|deo|deospray|tawas|deodorizer', na = False, case =False)
    mout_cond = df[column_name].str.contains('mouth|mouthspray|mouth wash|mouth spray', na =False, case = False)
    hair_cond = df[column_name].str.contains(r'(?=.*hair)(?=.*shampoo)',case = False, na = False)
    baby_cond = df[column_name].str.contains(Config.BABYCARE_REGEX,case =False, na = False)
    eye_cond = df[column_name].str.contains('eye|brow|eyebrow|eyegel',case = False, na = False)
    peeling_cond = df[column_name].str.contains('peel|peeling',na = False, case = False)
    decor_cond = df[column_name].str.contains('eyeliner|cushion|loose powder|cake|cushion|mascara|blushon|blush on|blush|nail polish|cheek|nailcolour|nailcolor|skin tint|skintint|lip tint|lip vinyl|lip matte|lipstick|lip stick',na = False, case = False)
    serum_cond = df[column_name].str.contains('serum',na=False, case = False)
    hair_serum_cond = df[column_name].str.contains(r'(?=.*hair)(?=.*(serum|ampoule|essence))', na = False,case = False)
    hair_oil_cond = df[column_name].str.contains(r'(?=.*hair)(?=.*oil)',na = False, case = False)
    hair_mask_cond = df[column_name].str.contains(r'(?=.*hair)(?=.*mask)',na = False,case =False)
    hair_tonic_cond = df[column_name].str.contains(r'(?=.*hair)(?=.*tonic)',na = False, case = False)
    hair_styling_cond = df[column_name].str.contains(r'(?=.*hair)(?=.*(gel|wax|pomade|clay|spray))',na =False,case = False)
    hair_coloring_cond = df[column_name].str.contains(r'(?=.*hair)(?=.*color)',na= False, case = False)
    hair_mist_cond = df[column_name].str.contains(r'(?=.*hair)(?=.*(mist|spray|perfume))',na = False, case = False)
    hair_conditioner_cond = df[column_name].str.contains(r'(?=.*hair)(?=.*conditioner)',na = False,case = False)

    conditions = [foundation_cond,mask_cond,
              lip_cond, toner_cond,perf_cond,
              soap_cond,cleanser_cond,moist_cond,men_cond, sunscreen_cond,deo_cond,mout_cond,hair_cond,
              baby_cond,eye_cond,peeling_cond,decor_cond,serum_cond,
              hair_serum_cond,
              hair_oil_cond,
              hair_mask_cond, 
              hair_tonic_cond,
              hair_styling_cond,
              hair_coloring_cond,
              hair_mist_cond,
              hair_conditioner_cond]
    
    choices = ['Foundation','Mask',
           'Lip Care','Toner','Perfume',
           'Body Wash','Cleanser','Moisturizer','Men Care','Sunscreen','Deodorant',
           'Mouth Care',
           'Shampoo',
           'Baby Care',
           'Eye Makeup',
           'Peeling Skincare',
           'Decorative Skincare',
           'Serum',
           'Hair Serum',
           'Hair Oil',
           'Hair Mask',
           'Hair Tonic',
           'Hair Styling',
           'Hair Coloring',
           'Hair Mist',
           'Hair Conditioner']

    df['product_category'] = np.select(conditions,choices, default = 'Other')

    return df
    
def upload_temp_table(conn,df):

    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS temp_category")

    cur.execute("""
    CREATE TEMP TABLE temp_category(
                id INT,
                product_category TEXT)
                """)
    
    data = list(zip(df["id"],df["product_category"]))

    execute_batch(
        cur,
        "INSERT INTO temp_category VALUES (%s,%s)",data)
    
    conn.commit()

def update_main_table(conn):
    try:
        cur = conn.cursor()

        cur.execute("""
        UPDATE bpom_products p
        SET product_category = t.product_category
        FROM temp_category t
        WHERE p.id = t.id
                    """)
        conn.commit()

        print("✅ Main table updated successfully")

    except Exception as e:
        conn.rollback()
        print("❌ ERROR: Failed to update main table")
        print(e)
        raise
        

def run_pipeline():
    #Connect to PostGres 
    conn = connect_db()

    #Load dataframe
    df = load_data(conn)

    updated_df = skincare_categorizer_function(df,'product_name')

    upload_temp_table(conn, updated_df)

    #Update main table
    update_main_table(conn)
    print("✅ Process completed! Closing PostGres Connection...")
    conn.close()

if __name__== '__main__':
    run_pipeline()