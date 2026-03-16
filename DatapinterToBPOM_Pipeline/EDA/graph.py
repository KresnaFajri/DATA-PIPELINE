import plotly.graph_objects as go 
import plotly.express as px
import sys
import random
sys.path.append(r"C:\KRESNA\Tools-20251201T015117Z-1-001\Tools\DATA PIPELINE\Datapinter_BPOM_Pipeline")
import pandas as pd
import os
from config import Config


def GetRandomColor():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    return f'rgba({r}, {g},{b},0.8)'

def add_opacity(color, alpha=0.4):
    if isinstance(color, str) and color.startswith("rgb"):
        nums = color[color.find("(")+1 : color.find(")")].split(",")
        r, g, b = [int(n) for n in nums]
        return f"rgba({r},{g},{b},{alpha})"
    return color

def CreateSankey(df):
    df.columns = df.columns.str.strip()  # Remove leading/trailing whitespace from column names

    required_cols = ['Brand', 'Manufacturer', 'Total SKU']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f'{col} column not found in dataframe')
    
    brands = df['Brand'].unique().tolist()
    manufacturers = df['Manufacturer'].unique().tolist()

    all_nodes = brands + manufacturers

    palette = px.colors.qualitative.Set3
    node_colors = [palette[i % len(palette)] for i in range(len(all_nodes))]
    
    #Mapping to index
    brand_index = {brand:i for i, brand in enumerate(brands)}
    manufacturer_index = {mnf : i+len(brands) for i, mnf in enumerate(manufacturers)}

    source = df['Brand'].map(brand_index)
    target = df['Manufacturer'].map(manufacturer_index)
    value = df['Total SKU']

    fig = go.Figure(data = [go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = all_nodes,
          color = node_colors
        ),
        link = dict(
          source = source,
          target = target,
          value = value
      ))])
    
    fig.update_layout(title_text=f"Sankey Diagram of Brands and Manufacturers in {Config.CATEGORY} Brands",
                      width = 100 * Config.N_ROWS,
                      height = 45 * Config.N_ROWS,
                      font_size=10)
    
    return fig
    