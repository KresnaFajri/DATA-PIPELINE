import duckdb
import pandas as pd

def CreateDB(con, table_name):
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            nama_produk VARCHAR,
            brand VARCHAR,
            nama_toko VARCHAR,
            lokasi VARCHAR,
            tren VARCHAR,
            umur_listing INTEGER,
            harga_asli DOUBLE,
            harga DOUBLE,
            omset_30_hari DOUBLE,
            penjualan_30_hari DOUBLE,
            rata_rata_omset_per_bulan DOUBLE,
            omset_total DOUBLE,
            rata_rata_penjualan_per_bulan DOUBLE,
            penjualan_total DOUBLE,
            rating DOUBLE,
            wishlist INTEGER,
            url VARCHAR,
            query_date DATE,
            jumlah_ulasan INTEGER,
            price_distributions VARCHAR,
            store_type VARCHAR,
            ecommerce_platform VARCHAR,
            query_keywords VARCHAR
        )
    """)

def InsertLog(DB_LOG, file_name, file_path, status):
    con = duckdb.connect(DB_LOG)
    con.execute("""
            INSERT INTO pipeline_log (file_name,
            file_path, 
            status)
            VALUES (?,?,?)""",
            [file_name, file_path,status])

def LoadDuckDB(df, db_path, table_name,
               DB_LOG,file_name,file_path,status='FAILED'):
    try:
        table_name = table_name.lower()
        con = duckdb.connect(db_path)

        CreateDB(con,table_name)
        
        df.columns = [c.lower() for c in df.columns]
        con.register("df_view", df)

        # Check table existence
        table_exists = con.execute(f""" SELECT COUNT(*) FROM information_schema.tables WHERE lower(table_name) = '{table_name}' """).fetchone()[0] > 0

        # If table not exists → create and stop if not table_exists:
        if not table_exists:
            con.execute(f""" CREATE TABLE "{table_name}" AS SELECT * FROM df_view """)
            con.close()
            return
        
        # Delete existing records (idempotent behavior)
        con.execute(f""" DELETE FROM "{table_name}" USING df_view WHERE "{table_name}".url = df_view.url AND "{table_name}".query_date = df_view.query_date """)

        # Insert fresh data
        con.execute(f""" INSERT INTO "{table_name}" SELECT * FROM df_view """)
        InsertLog(DB_LOG,file_name, file_path,status="SUCCESS")
    except Exception as e:

        #lOG FAIL
        InsertLog(DB_LOG, file_name, file_path,status="FAILED")
        raise e
    
    con.close()

def ReadLog(DB_LOG, file_name):
    """
    Check folder whether it has been processed by matching filenames in folder
    and logfile.db
    Params:
    1.con : DB connection
    2.file_name: Path/string
    """
    con =duckdb.connect(DB_LOG)
    result = con.execute(
        """
        SELECT COUNT(*)
        FROM pipeline_log
        WHERE file_name = ?
        AND status = 'SUCCESS'
        """,[file_name]).fetchone()[0]
    
    return result > 0 
    