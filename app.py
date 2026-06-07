"""
app.py — Volantis public dashboard entry point.

Free tier: regime overview, implied vol, MFIV, BKM moments, 90-day history.
No signal logic, no composite ranks, no trade recommendations.
"""
import streamlit as st

from src.data_loader import UNAVAILABLE_MSG, get_regime_data
from src.components.regime import render_regime
from src.components.implied_vol import render_implied_vol
from src.components.mfiv import render_mfiv
from src.components.bkm import render_bkm
from src.components.history import render_history

st.set_page_config(
    page_title="Volantis | Volatility Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("Volantis")
st.caption("Quantitative volatility intelligence · SPY & QQQ · Updated daily after market close")

st.divider()

# Gate on data availability — all panels use the same bundle
regime_df = get_regime_data()
if regime_df.empty:
    st.error(UNAVAILABLE_MSG)
    st.stop()

render_regime(regime_df)
st.divider()

render_implied_vol()
st.divider()

render_mfiv()
st.divider()

render_bkm()
st.divider()

render_history()

st.divider()
st.caption("Volantis — Quantitative volatility intelligence. Updated daily after market close.")
