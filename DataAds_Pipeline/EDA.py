import duckdb

def GetData(db_path,query):
    conn = duckdb.connect(db_path)
    df = conn.execute(query).fetchdf()
    return df

