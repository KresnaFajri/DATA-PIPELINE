import pandas as pd
import os
import numpy as np
import sys
import re
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001")
from Tools.DataCleaner import DataCleaner,FeatureGenerator

cleaner = DataCleaner()
fgen = FeatureGenerator()

# --- INPUT DATA_PATH (.csv,.xlsx)
DATA_PATH = r"C:\KRESNA\ANALYSIS\DATA BPOM\db_fetch\BPOM DATA 2022-2026.csv"
# -- Place your desired folder path
TARGET_PATH = r"C:\KRESNA\ANALYSIS\DATA BPOM\db_fetch\CLEAN_DB"
ANALYSIS_PATH = r"C:\KRESNA\ANALYSIS\DATA BPOM\db_fetch\ANALYSIS_2026"

# ---------------------------PIPELINE CODE --------------------------------------- 
if DATA_PATH.endswith("csv"):
    df = pd.read_csv(DATA_PATH) 
elif DATA_PATH.endswith(".xlsx"):
    df = pd.read_excel(DATA_PATH)

# --Check nullity
print(f"Searching for null columns : {df.isnull().sum()}")
def CheckNullity(df):
    #Count amount of rows:
    rows = len(df)

    #Count rows of null in each columns
    null_data = df.isnull().sum()

    #NullColumns
    NullColumns = null_data[null_data>0]
    problematic_columns = NullColumns.index.tolist()

    #Check pct
    if NullColumns.empty:
        print('DataFrame is clean, you are good to go!')
        return pd.DataFrame(),[]
    
    else:
        report = pd.DataFrame({
                'Null Amount':NullColumns,
                'Percentage':((NullColumns) *100 / len(df)).round(2)
            }).sort_values(by = 'Percentage', ascending =False)
        
        print(report)
        return report,problematic_columns

report,problematic_columns = CheckNullity(df)

#Fill the null values
#Check the dtypes of the columns
if problematic_columns:
    for column in problematic_columns:
        if df[column].dtypes == 'int64' or df[column].dtypes == 'float64':
            df[column] = df[column].fillna(0)
        elif df[column].dtypes == 'object':
            df[column] = df[column].fillna("Unknown")

print(f'Amount of null entry after cleaning : \n{df.isnull().sum()}')

#Check Duplicated Sum
print(f'Amount of Duplicated Data in Excel : {df.duplicated().sum()}')

#Remove data duplicacy
df = df.drop_duplicates()
print(f'Amount of Duplicated Data in Excel after cleaning : {df.duplicated().sum()}')

#Check manufacturer name format
def ManufacturerNameFormatter(text):
    text = str(text)
    if "," in text:
        subtext = re.split(",",text)
        new_text = f"{subtext[1].strip()} {subtext[0].strip()}"
        return new_text
    else:
        return text
if 'manufacturer_name' in df.columns:
    df['manufacturer_name'] = df['manufacturer_name'].apply(ManufacturerNameFormatter)

#Clean HTML Entities
df['product_name'] = df['product_name'].apply(cleaner.CleanHTMLEntities)
df['product_brands'] = df['product_brands'].apply(cleaner.CleanHTMLEntities)
df['manufacturer_name'] = df['manufacturer_name'].apply(cleaner.CleanHTMLEntities)

# Feature Engineering on Dataframe
foundation_cond = df['product_name'].str.contains('foundation',na =False, case = False)
mask_cond =  df['product_name'].str.contains('mask',na = False, case = False)
lip_cond = df['product_name'].str.contains('lip serum|lipserum|lipbalm|lip balm',case = False, na = False)
toner_cond = df['product_name'].str.contains('toner|essence toner|acne toner', na = False, case = False) 
perf_cond= df['product_name'].str.contains('toilette|toilet|eau de', na = False,case=False)
soap_cond = df['product_name'].str.contains('soap|sabun|bodywash|handwash|body wash',na = False,case = False)
cleanser_cond = df['product_name'].str.contains('cleanser|micellar|facial wash|facewash|face wash|facialwash',na = False, case = False)
moist_cond = df['product_name'].str.contains('moisturizer|lotion|cream|moist', na = False, case =False)
men_cond = df['product_name'].str.contains('pomade|shave|shaving', na = False, case =False)
sunscreen_cond = df['product_name'].str.contains('sunscreen|sunblock|sunveil|sunveila|uv shield|uv protect|sun block|spf|sunguard|sun guard|surya|suncare|sun care', na = False, case =False)
deo_cond = df['product_name'].str.contains('deodorant|deo|deospray|tawas|deodorizer', na = False, case =False)
mout_cond = df['product_name'].str.contains('mouth|mouthspray|mouth wash|mouth spray', na =False, case = False)
hair_cond = df['product_name'].str.contains(r'(?=.*hair)(?=.*shampoo)',case = False, na = False)
baby_cond = df['product_name'].str.contains('baby balm|babylotion|babyoil|babybalm|calmingoil|calming oil',case =False, na = False)
eye_cond = df['product_name'].str.contains('eye|brow|eyebrow|eyegel',case = False, na = False)
peeling_cond = df['product_name'].str.contains('peel|peeling',na = False, case = False)
decor_cond = df['product_name'].str.contains('eyeliner|cushion|loose powder|cake|cushion|mascara|blushon|blush on|blush|nail polish|cheek|nailcolour|nailcolor|skin tint|skintint|lip tint|lip vinyl|lip matte|lipstick|lip stick',na = False, case = False)
serum_cond = df['product_name'].str.contains('serum',na=False, case = False)
hair_serum_cond = df['product_name'].str.contains(r'(?=.*hair)(?=.*(serum|ampoule|essence))', na = False,case = False)
hair_oil_cond = df['product_name'].str.contains(r'(?=.*hair)(?=.*oil)',na = False, case = False)
hair_mask_cond = df['product_name'].str.contains(r'(?=.*hair)(?=.*mask)',na = False,case =False)
hair_tonic_cond = df['product_name'].str.contains(r'(?=.*hair)(?=.*tonic)',na = False, case = False)
hair_styling_cond = df['product_name'].str.contains(r'(?=.*hair)(?=.*(gel|wax|pomade|clay|spray))',na =False,case = False)
hair_coloring_cond = df['product_name'].str.contains(r'(?=.*hair)(?=.*color)',na= False, case = False)
hair_mist_cond = df['product_name'].str.contains(r'(?=.*hair)(?=.*(mist|spray|perfume))',na = False, case = False)
hair_conditioner_cond = df['product_name'].str.contains(r'(?=.*hair)(?=.*conditioner)',na = False,case = False)


#Create conditions and replace Skincare Categories
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

#Granularize SUBMIT_DATE DATA
df['submit_year'] = pd.to_datetime(df['submit_date']).dt.year

#Create Sub Dataframe
ManufacturerDF = df.groupby('manufacturer_name').agg({
    'product_brands':'nunique'
})

ManufacturerDF['Manufacturer Type'] = ManufacturerDF['product_brands'].apply(fgen.OEMClassifier)
manufacturer_status = ManufacturerDF['Manufacturer Type'].to_dict()

df['Manufacture Status'] = df['manufacturer_name'].map(manufacturer_status)

df.rename(columns = {
    'manufacturer_name':'pabrik',
    'product_brands':'Brand',
    'product_name':'Nama Produk',
    'product_form':'Sediaan',
    'product_package':'Kemasan'},inplace = True)

#IO Code 
# Jika TARGET_PATH merupakan directory yang ada, pake kode ini
# Ambil substring terakhir dari string DATA_PATH untuk dimasukkan ke dalam filename
if not os.path.exists(TARGET_PATH):
    os.makedirs(TARGET_PATH)

#Jika target_path merupakan directory yang belum ada, buat dulu directorynya
substring =  re.split(r'\\',DATA_PATH)
base_name = os.path.splitext(substring[-1])[0]
filename = f"Clean{base_name}.xlsx"
save_path = os.path.join(TARGET_PATH,filename)
df.to_excel(save_path,index =False)

print(f"✨ Process Complete! File saved to: {save_path}")
