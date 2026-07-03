import pandas as pd
from pathlib import Path
import sys
sys.path.append(r"/home/user2/airflow")
from DataCleaner import DataCleaner

def extract_files(input_path) -> pd.DataFrame:
    cleaner = DataCleaner()
    if input_path.endswith(".csv"):
        df = pd.read_csv(input_path,usecols =['Omset 30 Hari'])
        result = cleaner.DetectNumericDelimiter(df['Omset 30 Hari'])
        df= pd.read_csv(input_path,thousands = result)
        return df
    
    elif input_path.endswith(".xlsx"):
        df = pd.read_excel(input_path,usecols = ['Omset 30 Hari'])
        result = cleaner.DetectNumericDelimiter(df['Omset 30 Hari'])
        df = pd.read_excel(input_path,thousands = result)
        return df
    else:
        raise ValueError(f"Unsupported input_path type")