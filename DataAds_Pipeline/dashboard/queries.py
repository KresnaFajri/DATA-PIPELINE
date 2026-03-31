from config import DashboardConfig
import streamlit as st

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

def QueryClickPerMonth(db_name,table,date_choice) -> str:
    return f""" SELECT 
SUM("clicks_{db_name}")
FROM {table}
WHERE month_{db_name} = '{date_choice}'
"""
def QueryConversionData(db_name, table)-> str:
    return f"""SELECT 
    month_{db_name},
    SUM(conversions_{db_name}) AS TotalConversions
    FROM {table}
    WHERE campaign_status_{db_name}='Enabled'
    GROUP BY month_{db_name}
    ORDER BY month_{db_name} ASC """

def QueryCampaignConv(db_name, table,period_choice)-> str:
    return f"""SELECT
    campaign,
    SUM(conversions_{db_name}) AS TotalConversions
    FROM {table}
    WHERE campaign_status_{db_name}='Enabled' and month_{db_name} = '{period_choice}'
    GROUP BY campaign
    """
def QueryCostCampaign(db_name,table,period_choice)->str:
    return f"""SELECT
    campaign,
    SUM(cost_{db_name}) AS TotalCost
    FROM {table}
    WHERE month_{db_name} = '{period_choice}'
    GROUP BY campaign
    """

def FunnelStaging(period_choice):
    return f""" 
    SELECT 
    SUM("impr._campaign") AS "Total Impression",
    SUM(clicks_campaign) AS "Total Visitor",
    SUM(conversions_campaign) AS "Total Conversion",
    SUM(phone_call_lead_campaign + submit_lead_form_campaign + leads_from_messages_campaign) AS "Total Potential Leads"
    FROM CampaignReport
    WHERE month_campaign = '{period_choice}'
    """
def QueryTopKeywords(period_choice):
    return f"""
    SELECT 
    keyword_keyword AS "Keywords",
    SUM(conversions_keyword) AS "Total Conversions"
    FROM keyword.KeywordReport
    WHERE month_keyword = '{period_choice}'
    GROUP BY keyword_keyword
    ORDER BY "Total Conversions" DESC
    LIMIT 10
    """
def QueryImpressionShare(campaign,period_choice):
    return f"""
    SELECT
    campaign,
    CAST("search_impr._share_campaign" AS FLOAT) AS "Impression Share",
    CAST("search_lost_is_(rank)_campaign" AS FLOAT) AS "Lost IS"
    FROM CampaignReport
    WHERE month_campaign = '{period_choice}' AND campaign = '{campaign}'
    ORDER BY "Impression Share" DESC 
    """
def GetCampaignList(period_choice):
    return f"""
    SELECT 
    DISTINCT campaign
    FROM CampaignReport
    WHERE month_campaign = '{period_choice}'
    """
