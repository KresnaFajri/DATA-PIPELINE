import duckdb
import pandas as pd
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

@st.cache_resource
def GetConnection(database_name,ACCESS_TOKEN):
    conn = duckdb.connect(f"md:?motherduck_token={ACCESS_TOKEN}")
    conn.execute(f"ATTACH IF NOT EXISTS 'md:{database_name}' as {database_name}")
    return conn

def GetData(query:str,ACCESS_TOKEN=None,USE_MOTHERDUCK = False,db_name = None,db_path=None):
    if USE_MOTHERDUCK:
         #Streamlit cloud  -> MotherDuck
         conn = GetConnection(database_name = db_name,ACCESS_TOKEN = ACCESS_TOKEN)
    else:
        conn = duckdb.connect(db_path)
    df = conn.execute(query).fetchdf()
    return df

def DataGroupingConversions(db_name:str,df:pd.DataFrame,categories:list):

    GroupDataframe = df.groupby(categories).agg({
        f"conversions._{db_name}":'sum'
    }).reset_index().sort_values(by = 'categories')

    return GroupDataframe

def LinePlot(df:pd.DataFrame,x_name:str,y_name:str,title:str):
        
        """
        Params:
        1.df :pd.Dataframe
        2.x_name: X columns for Plotly Line Chart
        3.y_name: Y columns for Plotly Line Chart
        4.title: Title of the charts 
        """

        fig = go.Figure()

        fig.add_trace(go.Scatter(
        x = df[x_name],
        y =df[y_name],
        mode='lines+markers+text',
        marker = dict(opacity = 0.5),
        text = [f"{val}" for val in df[y_name]],
        yaxis = 'y2',
        textposition = 'top center',
        line = dict(shape = 'spline', smoothing = 0.8, width = 2)))

        fig.update_layout(title = title,
                             xaxis = dict(title = f'{x_name}'),
                             yaxis = dict(
                                        title = title,
                                        tickfont = dict(color = 'green')),
                             height = 600,
                             width = 1200,
                             template = 'simple_white',
                             plot_bgcolor = 'white')
        st.plotly_chart(fig,use_container_width=True)

def MarketFunnelPlot(df:pd.DataFrame,stages:list):

    """
    Params:
    - df : DataFrame input(1 baris kata)
    - stages : List, kolom data yang akan dijadikan marketing funnel. 
    Contoh : ["Clicks","Conversions","Raw Leads"]
    """

    missing = [s for s in stages if s not in df.columns]    

    if missing:
         raise ValueError(f"Columns can not be found in DataFrame")
    
    row = df.iloc[0]

    #stages = ['Clicks','Conversions','Raw Leads','customer_name_probing','customer_name_success']

    stages = stages

    values = [row[stage] for stage in stages]

    fig = go.Figure()

    fig.add_trace(
         go.Funnel(x = values, 
                    y = stages ,
                    name = row['Month'],
                    textinfo = 'value+percent initial'))
    return fig

def change_label_style(label, font_size='12px', font_color='black', font_family='sans-serif'):
    html = f"""
    <script>
        var elems = window.parent.document.querySelectorAll('p');
        var elem = Array.from(elems).find(x => x.innerText == '{label}');
        elem.style.fontSize = '{font_size}';
        elem.style.color = '{font_color}';
        elem.style.fontFamily = '{font_family}';
    </script>
    """
    st.components.v1.html(html)