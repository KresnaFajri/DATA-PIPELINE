import duckdb

def LoadDuckDB(
        df,
        db_path,
        table_name,
        mode="replace"):
    
    con = duckdb.connect(db_path)
    con.register("df_view",df)
    
    if mode == "replace":
        con.execute(f"""
                    CREATE OR REPLACE TABLE {table_name} AS
                    SELECT * FROM df_view
                    """)
    elif mode == "append":
        con.execute(f"""
                    INSERT INTO {db_path}
                    SELECT * FROM df_view
                    """)
    else:
        raise ValueError("Mode must be filled with 'replace' or 'append'")
    
    con.close()
