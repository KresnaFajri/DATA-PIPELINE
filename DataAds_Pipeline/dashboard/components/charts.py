import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


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
        line=dict(color="#a855f7", width=2),
        marker=dict(color="#e879f9", size=6),
        fill="tozeroy",
        fillcolor="rgba(124,58,237,0.10)",
    ))
    fig.update_layout(**PLOTLY_THEME)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)


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
    fig.update_layout(**PLOTLY_THEME)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)


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
    fig.update_layout(**PLOTLY_THEME)
    fig.update_layout(showlegend=True,
                      legend=dict(font=dict(color="#b8b5cc", size=10)))
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
