import psycopg2
import pandas as pd
from psycopg2.extras import execute_batch

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