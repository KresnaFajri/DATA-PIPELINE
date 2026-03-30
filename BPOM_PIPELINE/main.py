import psycopg2
import numpy as np
import pandas as pd
from load import load_data,upload_temp_table,update_main_table
from transform import skincare_categorizer_function

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