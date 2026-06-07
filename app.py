"""
app.py — Volantis public dashboard entry point.

Free tier: regime overview, implied vol, MFIV, BKM moments, 90-day history.
No signal logic, no composite ranks, no trade recommendations.
"""
import streamlit as st

from src.data_loader import UNAVAILABLE_MSG, get_regime_data, get_download_error
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

# Gate on data availability — surface the real error if download fails
regime_df = get_regime_data()
if regime_df.empty:
    err = get_download_error()
    if err:
        st.error(f"Data load failed: {err}")
        st.info(
            "Check that Streamlit Cloud secrets are set correctly. "
            "Expected format in the Secrets manager:\n\n"
            "```toml\n"
            "[r2]\n"
            'endpoint = "https://ACCOUNT_ID.r2.cloudflarestorage.com"\n'
            'access_key_id = "YOUR_KEY"\n'
            'secret_access_key = "YOUR_SECRET"\n'
            'bucket = "volantis-data"\n'
            "```"
        )
    else:
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
