import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Plotly theme yang sesuai dengan aurora background ────────────────────────
AURORA_TEMPLATE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="JetBrains Mono", color="#6e6a85", size=11),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.06)",
        tickcolor="rgba(255,255,255,0)",
        tickfont=dict(color="#6e6a85"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.06)",
        tickcolor="rgba(255,255,255,0)",
        tickfont=dict(color="#6e6a85"),
    ),
    margin=dict(l=0, r=0, t=24, b=0),
    hoverlabel=dict(
        bgcolor="rgba(20,17,30,0.95)",
        bordercolor="rgba(168,85,247,0.5)",
        font=dict(family="JetBrains Mono", color="#e2e0f0", size=11),
    ),
)
# Warna PyCharm page JetBrains — dari atas ke bawah funnel
PYCHARM_FUNNEL_COLORS = [
    "#9758EF",  # ungu       — Impressions
    "#CF4DC4",  # pink       — Clicks
    "#1D8FE1",  # biru       — Raw Leads
    "#0DCFCF",  # teal       — Probing
    "#21D789",  # hijau lime — Conversions
]
# ----------------------------------------------------------------------------------------------

# Palet warna aurora
AURORA_COLORS = ["#a855f7", "#22d3ee", "#e879f9", "#34d399", "#fbbf24"]

# ── Plotly theme yang sesuai dengan aurora background ────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="JetBrains Mono", color="#b8b5cc", size=11),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(255,255,255,0.08)",
        tickcolor="rgba(255,255,255,0.08)",
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(255,255,255,0.08)",
        tickcolor="rgba(255,255,255,0.08)",
    ),
    margin=dict(l=0, r=0, t=24, b=0),
)

PLOTLY_CONFIG = dict(
    displayModeBar=False,
)

def glass_section(title: str, content_fn, *args, **kwargs) -> None:
    """
    Wrapper glass panel dengan section header.
    Panggil fungsi `content_fn` di dalam panel.

    Contoh:
        glass_section("// TRAFFIC CHART", render_line_chart, data)
    """
    st.markdown(f"""
    <div class="glass-panel">
        <div class="section-header">{title}</div>
    </div>
    """, unsafe_allow_html=True)
    content_fn(*args, **kwargs)


def render_line_chart(x: list, y: list, label: str = "Value") -> None:
    """
    Line chart dengan styling aurora.

    Contoh:
        render_line_chart(
            x=["Jan","Feb","Mar","Apr","Mei"],
            y=[10, 25, 18, 32, 27],
            label="Connected Users"
        )
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode="lines+markers",
        name=label,
        line=dict(shape='spline',color="#a855f7", width=2),
        marker=dict(color="#e879f9", size=6),
        fill="tozeroy",
        fillcolor="rgba(124,58,237,0.10)",
    ))

    fig.update_layout(**AURORA_TEMPLATE)
    st.plotly_chart(fig, use_container_width=True)

def render_bar_chart(categories: list, values: list, label: str = "Value") -> None:
    """
    Bar chart dengan styling aurora.

    Contoh:
        render_bar_chart(
            categories=["Server A", "Server B", "Server C"],
            values=[120, 85, 200],
            label="Request Count"
        )
    """
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories, y=values,
        name=label,
        marker=dict(
            color="rgba(124,58,237,0.6)",
            line=dict(color="#a855f7", width=1),
        ),
    ))

    fig.update_layout(**AURORA_TEMPLATE)
    st.plotly_chart(fig, use_container_width=True)

def render_invertedbar_chart(categories: list, values: list, label: str = "Value") -> None:
    """
    Bar chart dengan styling aurora.

    Contoh:
        render_invertedbar_chart(
            categories=["Server A", "Server B", "Server C"],
            values=[120, 85, 200],
            label="Request Count"
        )
    """
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=values, y=categories,
        name=label,
        orientation = 'h',
        marker=dict(
            color="rgba(124,58,237,0.6)",
            line=dict(color="#a855f7", width=1),
        ),
    ))
    fig.update_layout(**AURORA_TEMPLATE)
    fig.update_layout(yaxis=dict(categoryorder='total ascending'))
    st.plotly_chart(fig, use_container_width=True)

def render_donut_chart(labels: list, values: list, title: str = "") -> None:
    """
    Donut / pie chart dengan styling aurora.

    Contoh:
        render_donut_chart(
            labels=["Online", "Idle", "Offline"],
            values=[12, 5, 3],
            title="Node Distribution"
        )
    """
    colors = ["#22d3ee", "#fbbf24", "#3d3a52"]
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#13111a", width=2)),
        textfont=dict(family="JetBrains Mono", color="#b8b5cc", size=11),
    ))
    if title:
        fig.update_layout(
            annotations=[dict(text=title, x=0.5, y=0.5, font_size=12,
                              font_color="#e2e0f0", showarrow=False)]
        )

    fig.update_layout(**AURORA_TEMPLATE)
    fig.update_layout(showlegend=True,
                      legend=dict(font=dict(color="#b8b5cc", size=10)))
    st.plotly_chart(fig, use_container_width=True)

def render_pie_chart(labels: list, values: list, title: str = "") -> None:
    colors = ["#cadf50", "#1FB43B99", "#D16309"]
    
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.45,  # ← tambah hole agar jadi donut, lebih cocok dengan aurora vibes
        marker=dict(colors=colors, line=dict(color="#13111a", width=2)),
        textfont=dict(family="JetBrains Mono", color="#b8b5cc", size=11),
        hovertemplate="<b>%{label}</b><br>%{value:,}<br>%{percent}<extra></extra>",
    ))

    annotations = []
    if title:
        annotations.append(dict(
            text=title,
            x=0.5, y=0.5,
            font_size=12,
            font_color="#e2e0f0",
            showarrow=False
        ))

    # Satu update_layout saja — gabung semua
    fig.update_layout(
        **AURORA_TEMPLATE,
        annotations=annotations,
        showlegend=True,
        legend=dict(
            font=dict(family="JetBrains Mono", color="#b8b5cc", size=10),
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def MarketFunnelPlot(df: pd.DataFrame, stages: list):
    missing = [s for s in stages if s not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")

    row = df.iloc[0]
    values = [row[stage] for stage in stages]

    fig = go.Figure()
    fig.add_trace(go.Funnel(
        x=values,
        y=stages,
        name=str(row.get('month_campaign', '')),
        textinfo='value+percent initial',
        textfont=dict(family="JetBrains Mono", color="#ffffff", size=11),
        marker=dict(
            color=PYCHARM_FUNNEL_COLORS[:len(stages)],  # sesuai jumlah stages
            line=dict(color="#13111a", width=2),
        ),
        connector=dict(
            line=dict(color="rgba(255,255,255,0.06)", width=1)
        ),
        hovertemplate="<b>%{y}</b><br>Value: %{x:,}<br>%{percentInitial}<extra></extra>",
    ))

    fig.update_layout(
        **AURORA_TEMPLATE,  # pakai template aurora yang sudah dibuat
        height=420)    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
