        
from config import PipelineConfig

QUERY_SALES_BRAND = f"""
SELECT 
DISTINCT brand as brand,
sum(penjualan_30_hari) as penjualan_30_hari
from "shopee_{PipelineConfig.CATEGORY}"
WHERE store_type = 'Official Store' and query_date between '{PipelineConfig.TIME_WINDOW_START}' and '{PipelineConfig.TIME_WINDOW_END}'
GROUP BY brand
ORDER BY penjualan_30_hari DESC
LIMIT {PipelineConfig.Top_N}
"""

QUERY_MSHARE_BRAND = f"""
SELECT 
DISTINCT brand,
sum(omset_30_hari) as OmsetPerBrand
from "shopee_{PipelineConfig.CATEGORY}"
WHERE store_type = 'Official Store' AND query_date BETWEEN '{PipelineConfig.TIME_WINDOW_START}' AND '{PipelineConfig.TIME_WINDOW_END}'
GROUP BY brand
ORDER BY sum(omset_30_hari) DESC
LIMIT {PipelineConfig.Top_N}
"""
QUERY_MPenetration_BRAND = f"""
SELECT 
DISTINCT brand,
sum(jumlah_ulasan) as UlasanPerBrand
FROM "shopee_{PipelineConfig.CATEGORY}"
WHERE store_type = 'Official Store' and query_date between '{PipelineConfig.TIME_WINDOW_START}' and '{PipelineConfig.TIME_WINDOW_END}'
GROUP BY brand
ORDER BY UlasanPerBrand DESC
LIMIT {PipelineConfig.Top_N}
"""

QUERY_PRODUCT_SALES = f"""
SELECT 
    nama_produk as nama_produk,
    brand,
    sum(penjualan_30_hari) as TotalPenjualan30Hari
FROM "shopee_{PipelineConfig.CATEGORY}"
WHERE store_type = 'Official Store' and query_date between '{PipelineConfig.TIME_WINDOW_START}' and '{PipelineConfig.TIME_WINDOW_END}'
GROUP BY nama_produk,brand
ORDER BY TotalPenjualan30Hari DESC
limit {PipelineConfig.Top_N}
"""

QUERY_PRODUCT_REV = f"""
SELECT
    nama_produk as nama_produk,
sum(omset_30_hari) as TotalOmset30Hari
FROM "shopee_{PipelineConfig.CATEGORY}"
WHERE store_type = 'Official Store' and query_date between '{PipelineConfig.TIME_WINDOW_START}' and '{PipelineConfig.TIME_WINDOW_END}'
GROUP BY nama_produk
ORDER BY TotalOmset30Hari DESC
limit {PipelineConfig.Top_N}
"""

PRICE_DIST = f"""
SELECT price_distributions,
SUM(penjualan_30_hari) AS TotalPenjualan
FROM "shopee_{PipelineConfig.CATEGORY}"
WHERE store_type = 'Official Store' and query_date between '{PipelineConfig.TIME_WINDOW_START}' and '{PipelineConfig.TIME_WINDOW_END}'
GROUP BY price_distributions
ORDER BY TotalPenjualan DESC
"""
QUERY_DATAFRAME = f"""
SELECT * FROM "shopee_{PipelineConfig.CATEGORY}"
"""