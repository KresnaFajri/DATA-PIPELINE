import pandas as pd
import os
from config import Config
import kaleido
from kaleido import write_fig_sync
import sys
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools\DATA PIPELINE\DatapinterToBPOM_Pipeline\repositories")
from sklearn.preprocessing import MinMaxScaler
from database_queries import get_manufacturer_query, get_top_products
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools")
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools\DATA PIPELINE\DatapinterToBPOM_Pipeline\EDA")
from graph import CreateSankey
from DataCleaner import DataCleaner,FeatureGenerator

#Define the module
cleaner = DataCleaner()
NLPCleaner = cleaner.NLPCleaner()
fgen = FeatureGenerator()
# ------------INPUT-----------
STOPWORDS_PATH = r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools\DataCleaner\assets\Skincare Corpora\STOPWORDS.txt"


with open(STOPWORDS_PATH,'r') as f:
    STOPWORDS_LIST = f.read().splitlines()

print(f'DB_NAME:{Config.DB_NAME}')
print(f'Excel Filename:{Config.EXCEL_FILENAME_1}')
print(f'Excel Filename:{Config.EXCEL_FILENAME_2}')
print(f'Table Name:{Config.TABLE_NAME}')


#Function
def ConnectAndSearch():
    df_sales = pd.read_csv(os.path.join(Config.DATASOURCE_PATH,Config.EXCEL_FILENAME_1))
    df_brand = pd.read_csv(os.path.join(Config.DATASOURCE_PATH,Config.EXCEL_FILENAME_2))
    
    #Get Manufacturer Query
    get_manufacturer_query(df_brand)
    
    #Get Top Products
    get_top_products(df_sales)
    FILE_NAME_2 = os.path.join(Config.DATASOURCE_PATH,f"{Config.FILE_NAME_2}_{Config.CATEGORY}.xlsx")
    df_sankey = pd.read_excel(FILE_NAME_2)

    df_sankey = (df_sankey.groupby(['Brand','Manufacturer'],as_index = False)['Total SKU'].sum())
    df_sankey = df_sankey.sort_values(by = 'Total SKU', ascending= False)
    
    fig_sankey = CreateSankey(df_sankey)
    fig_name = f"{Config.FILE_NAME_2}_Sankey.svg"

    #Save as SVG
    fig_sankey.write_image(os.path.join(Config.DATASOURCE_PATH,fig_name),
                           engine="kaleido")
    
def ReadAndCreateSpiderCharts(BPOM_DATASOURCE, TARGET_PATH, brand_list, 
                              filter_category=None):
    os.makedirs(TARGET_PATH, exist_ok=True)  # pastikan folder ada
    
    df_all = pd.read_excel(BPOM_DATASOURCE)

    if filter_category:
        df_all = df_all[df_all['product_category'].isin(filter_category)]

    ProductVar_Mat = (df_all.groupby(['Brand','product_category'])['product_register']
                      .count()
                      .reset_index()
                      .pivot(index='Brand', columns='product_category', values='product_register')
                      .fillna(0))

    # Filter brand_list
    ProductVar_Mat = ProductVar_Mat.loc[ProductVar_Mat.index.isin(brand_list)]
    ProductVar_scaled = ProductVar_Mat.div(ProductVar_Mat.max()).fillna(0)


    for brand in brand_list:
        if brand not in ProductVar_scaled.index:
            print(f"Warning: {brand} tidak ada di dataset, skip chart.")
            continue
        
        Spider_ProductVar = fgen.DataViz().plot_spider(
            data=ProductVar_scaled,
            category=brand,
            columns=ProductVar_scaled.columns.tolist()
        )

        # Check if plot is matplotlib or plotly
        try:
            Spider_ProductVar.savefig(os.path.join(TARGET_PATH,f'{brand.lower()}.png'),
                                    dpi=300, bbox_inches='tight')
        except AttributeError:
            # kemungkinan plotly
            Spider_ProductVar.write_image(os.path.join(TARGET_PATH,f'{brand.lower()}.png'),
                                        engine='kaleido')


if __name__ == "__main__":
    ConnectAndSearch()
    ReadAndCreateSpiderCharts(Config.CLEAN_BPOMDB_PATH, 
                              TARGET_PATH=Config.BRAND_PRODUCT_VAR_PATH,
                              brand_list = ['ERHAIR','SOFT CARE'],
                              filter_category = None)