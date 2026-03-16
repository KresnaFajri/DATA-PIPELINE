import os 
import pandas as pd

def TransformFiles(df,suffix):
    df = df.copy()

    #Transform
    df.columns = df.columns.str.lower().str.replace(" ","_")

    df = df.drop_duplicates()

    df['Cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)
    df = df[df['Cost']>0]
    
    df.rename(columns=lambda col: f"{col}_{suffix}" if col.strip().lower() != 'campaign' else col, 
              inplace = True)

    return df
