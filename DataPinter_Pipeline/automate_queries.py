from config import AutomatePipelineConfig
import duckdb
# =============== DEFINE YOUR OWN QUERY HERE =====================================================
def APPENDING_COLUMN_QUERY(category,column_name,data_type,table_name):
    return f""" 
    ALTER TABLE {table_name}
    ADD COLUMN {column_name} {data_type} CONSTRAINT;
    """
def QUERY_SALES_BRAND(category, time_start,time_end,limit):
    return f"""
    SELECT 
    DISTINCT brand as brand,
    sum(penjualan_30_hari) as penjualan_30_hari
    from "shopee_{category}"
    WHERE store_type = 'Official Store' and query_date between '{time_start}' and '{time_end}'
    GROUP BY brand
    ORDER BY penjualan_30_hari DESC
    LIMIT {limit}
    """

def QUERY_MSHARE_BRAND(category,time_start,time_end,limit):
    return f"""
    SELECT 
    DISTINCT brand,
    sum(omset_30_hari) as OmsetPerBrand
    from "shopee_{category}"
    WHERE store_type = 'Official Store' AND query_date BETWEEN '{time_start}' AND '{time_end}'
    GROUP BY brand
    ORDER BY sum(omset_30_hari) DESC
    LIMIT {limit}
    """

def QUERY_MPenetration_BRAND(category, time_start, time_end,limit): 
    return f"""
    SELECT 
    DISTINCT brand,
    sum(jumlah_ulasan) as UlasanPerBrand
    FROM "shopee_{category}"
    WHERE store_type = 'Official Store' and query_date between '{time_start}' and '{time_end}'
    GROUP BY brand
    ORDER BY UlasanPerBrand DESC
    LIMIT {limit}
    """

def QUERY_PRODUCT_SALES(category,time_start,time_end,limit,official_store_filter=True):
    excluded_official_filter = "AND store_type == 'Official Store'" if official_store_filter else ""
    return f"""
    SELECT 
        nama_produk as nama_shopee,
        name_produk_pendek as nama_produk_pendek,
        brand,
        sum(penjualan_30_hari) as TotalPenjualan30Hari
    FROM "shopee_{category}"
    WHERE query_date between '{time_start}' and '{time_end}' {excluded_official_filter}
    GROUP BY nama_produk,name_produk_pendek,brand
    ORDER BY TotalPenjualan30Hari DESC
    limit {limit}
    """

def QUERY_PRODUCT_REV(category,time_start,time_end,limit,official_store_filter=True):
    excluded_official_filter = "AND store_type == 'Official Store'" if official_store_filter else ""
    return f"""
    SELECT
        name_produk_pendek as nama_produk,
    sum(omset_30_hari) as TotalOmset30Hari
    FROM "shopee_{category}"
    WHERE store_type = 'Official Store' and query_date between '{time_start}' and '{time_end}'
    GROUP BY name_produk_pendek
    ORDER BY TotalOmset30Hari DESC
    limit {limit}
    """

def PRICE_DIST(category, time_start, time_end):
    return f"""
    SELECT price_distributions,
    SUM(penjualan_30_hari) AS TotalPenjualan
    FROM "shopee_{category}"
    WHERE store_type = 'Official Store' and query_date between '{time_start}' and '{time_end}'
    GROUP BY price_distributions
    ORDER BY TotalPenjualan DESC
    """
def QUERY_DATAFRAME(category):
    return f"""
    SELECT * FROM "shopee_{category}"
    """

# ========================================== UN-FILTERED QUERIES ==================================
# Query ini ditujukan untuk data-data yang tidak perlu filter Official Store, cth : Data Suplemen
def PRICE_DIST_UNFILTERED(category, time_start, time_end):
    return f"""
    SELECT 
    price_distributions,
    SUM(penjualan_30_hari) AS TotalPenjualan
    FROM "shopee_{category}"
    WHERE query_date BETWEEN '{time_start}' AND '{time_end}'
    GROUP BY price_distributions
    ORDER BY price_distributions ASC
    """

def QUERY_BRAND_SALES_UNFILTERED(category,time_start,time_end,limit):
    return f"""
    SELECT 
    DISTINCT brand,
    SUM(penjualan_30_hari) AS TotalPenjualan
    FROM "shopee_{category}"
    WHERE query_date BETWEEN '{time_start}' and '{time_end}'
    GROUP BY brand
    ORDER BY TotalPenjualan DESC
    LIMIT {limit}
    """
def QUERY_MPenetration_UNFILTERED(category, time_start, time_end,limit):
    return f"""
    SELECT 
    DISTINCT brand,
    sum(jumlah_ulasan) as UlasanPerBrand
    FROM "shopee_{category}"
    WHERE query_date between '{time_start}' and '{time_end}'
    GROUP BY brand
    ORDER BY UlasanPerBrand DESC
    LIMIT {limit}
    """
def QUERY_MSHARE_BRAND_UNFILTERED(category, time_start,time_end,limit):
    return f"""
    SELECT 
    DISTINCT brand,
    sum(omset_30_hari) as OmsetPerBrand
    from "shopee_{category}"
    WHERE query_date BETWEEN '{time_start}' AND '{time_end}'
    GROUP BY brand
    ORDER BY sum(omset_30_hari) DESC
    LIMIT {limit}
    """
def QUERY_PRODUCT_SALES_UNFILTERED(category, time_start, time_end,limit):
    return f"""
    SELECT 
    nama_produk,
    name_produk_pendek,
    SUM(penjualan_30_hari) AS TotalPenjualan,
    url AS link_produk
    FROM "shopee_{category}"
    WHERE query_date BETWEEN '{time_start}' AND '{time_end}'
    GROUP BY name_produk_pendek,penjualan_30_hari,nama_produk,url
    ORDER BY TotalPenjualan DESC
    LIMIT {limit}
    """

def QUERY_PRODUCT_REV_UNFILTERED(category,time_start,time_end,limit):
    return f"""
    SELECT
    nama_produk,
    name_produk_pendek,
    SUM(omset_30_hari) AS TotalOmset
    FROM "shopee_{category}"
    WHERE query_date BETWEEN '{time_start}' AND '{time_end}'
    GROUP BY nama_produk,name_produk_pendek,omset_30_hari
    ORDER BY TotalOmset DESC
    LIMIT {limit}
    """
def CategoryPriceDistrib(category,time_start=None,time_end=None):
    if time_start is None :
        return f"""
        SELECT
        skincare_function as "Additional Effect Skincare",
        harga,
        query_date,
        SUM(penjualan_30_hari) AS 'TotalSales30'
        FROM "shopee_{category}
        GROUP BY skincare_function,harga,penjualan_30_hari,query_date
        ORDER BY query_date ASC
        """
    return f"""
    SELECT
    skincare_function,
    harga,
    SUM(penjualan_30_hari) AS 'TotalSales30'
    FROM "shopee_{category}
    WHERE query_date BETWEEN {time_start} AND {time_end}
    GROUP BY skincare_function,harga,penjualan_30_hari
    """
def PricingSalesAnalyticsPerCategory(category, time_start, time_end, filtering_category="skincare_function"):
    """
    This functions aims to search for the best price point for each products. Filtered with product's attribute in filtering category,

    --Variable Explanation--

    1.category (str):Name of the table located in the database. Database must exist in the DuckDB instance
    2.time_start(str) : String of DATE in format "YYYY-MM-DD". Example : "2026-04-01"
    3.time_end(str) : String of DATE in format "YYYY-MM-DD".Example : "2026-04-30".Must be larger than time_start
    4.fitering_category (str):Column name located inside every table, attributes of product that want to be analyzed, 
    such as skincare effects, product medium (tablet, capsule,softgel,powder,etc)

    """
    ALLOWED_FILTER = {"skincare_function","product_form"}
    if filtering_category not in ALLOWED_FILTER:
        raise ValueError(f"Filtering Category Not Found!")
    
    return f"""        
        SELECT 
        brand,
        AVG(harga) AS "AveragePrice",
        sum(penjualan_30_hari) AS "TotalSales30",
        '{filtering_category}'
        FROM 'shopee_{category}'
        WHERE price_distributions IN (
            SELECT
            price_distributions FROM shopee_{category} 
            GROUP BY price_distributions 
            ORDER BY SUM(penjualan_30_hari)DESC 
            LIMIT 1
            ) 
        AND query_date BETWEEN '{time_start}' AND '{time_end}'
        GROUP BY brand,{filtering_category}
        ORDER BY "TotalSales30" DESC
        """

def CalcDependencyPct(category,brand,time_start,time_end,per_sku=True,is_supplement=False):
    exclude_clause = "AND NOT regexp_matches(nama_produk,'(bundle|set|kit|paket|bndl)')" if per_sku else ""
    exclude_official_store = "AND store_type = 'Official Store'" if is_supplement else ""
    #fill white space in category name with "_"
    return f"""
    SELECT
    name_produk_pendek,
    omset_30_hari*100/SUM(omset_30_hari) OVER() as prd_dependency_pct
    FROM shopee_{category}
    WHERE nama_toko ILIKE '%{brand}%' AND query_date BETWEEN '{time_start}' AND '{time_end}' {exclude_clause} {exclude_official_store}
    GROUP BY name_produk_pendek, omset_30_hari, nama_toko, query_date
    ORDER BY prd_dependency_pct DESC
    LIMIT 10
    """

def CalculateMarketGrowthRate(category,time_start,time_end):
    category = category.replace(" ","_")
    return f"""
    SELECT
    query_date,
    (market_size_cat - lag(market_size_cat) OVER(ORDER BY query_date))*100/lag(market_size_cat) OVER (ORDER BY query_date) AS mkt_growth_pct
    FROM
    (SELECT 
    query_date,
    SUM(omset_30_hari) as market_size_cat
    FROM shopee_{category}
    WHERE store_type = 'Official Store' AND query_date BETWEEN '{time_start}' AND '{time_end}'
    GROUP BY query_date)sub
    ORDER BY query_date ASC
    """