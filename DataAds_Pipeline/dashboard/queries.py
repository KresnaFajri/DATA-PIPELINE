from config import DashboardConfig

def QueryConversionPerMonth(db_name,table,date_choice)->str:
    return f"""
SELECT SUM(conversions_{db_name})
FROM {table}
WHERE CAST(month_{db_name} AS DATE) = CAST('{date_choice}' AS DATE)
"""

def CountRunningCampaign(db_name,table,date_choice)->str:
    return f"""
    SELECT COUNT(campaign)
    FROM {table}
    WHERE campaign_status_{db_name} = 'Enabled' AND month_{db_name} = '{date_choice}'
    """

def QueryImpressionPerMonth(db_name,table,date_choice) -> str:
    return f""" SELECT 
SUM("impr._{db_name}")
FROM {table}
WHERE month_{db_name} = '{date_choice}'
"""
def QueryConversionData(db_name, table)-> str:
    return f"""SELECT 
    month_{db_name},
    SUM(conversions_{db_name}) AS TotalConversions
    FROM {table}
    WHERE campaign_status_{db_name}='Enabled'
    GROUP BY month_{db_name}, conversions_{db_name}
    ORDER BY month_{db_name} ASC """
