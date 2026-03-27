import streamlit as st


def render_metrics(metrics: list[dict]) -> None:
    cards = []
    for m in metrics:
        delta = m.get("delta", "")
        delta_class = m.get("delta_class", "")
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>' if delta else ""

        card = (
            '<div class="metric-card">'
            '<div class="scan-line"></div>'
            f'<div class="metric-label">{m["label"]}</div>'
            f'<div class="metric-value {m.get("value_class", "")}">{m["value"]}</div>'
            + delta_html +
            '</div>'
        )
        cards.append(card)

    html = '<div class="metric-grid">' + "".join(cards) + "</div>"
    st.markdown(html, unsafe_allow_html=True)