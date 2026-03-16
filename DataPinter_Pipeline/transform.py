import pandas as pd
import sys
import re
#CAN ONLY BE USED ON DATAPINTER CSV
def transform(df):
    df = df.copy()
    #Transform
    #df = df.drop_duplicates(subset=['Nama Produk','Nama Toko'])
    df.columns = df.columns.str.lower().str.replace(" ","_")
    return df
