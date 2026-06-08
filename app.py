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

# About / methodology / disclaimer — framed as research publication (FCA s21 FSMA exemption)
st.markdown(
    """
<div style="background:#111118;border:1px solid #1e1e2e;border-radius:8px;padding:28px 32px;margin:8px 0">

  <p style="color:#E8E8F0;font-size:1rem;margin:0 0 16px 0;font-family:monospace;font-weight:700">
    About Volantis
  </p>

  <p style="color:#bbb;font-size:0.85rem;line-height:1.65;margin:0 0 20px 0;font-family:monospace">
    Volantis is a quantitative research publication measuring volatility
    conditions in the SPY and QQQ options markets. Each trading day we publish
    readings of implied volatility, term structure, and market-wide sentiment
    indicators — the same inputs professional derivatives desks use to frame
    short-volatility risk.
  </p>

  <p style="color:#00D4FF;font-size:0.78rem;margin:0 0 8px 0;font-family:monospace;font-weight:700;letter-spacing:0.08em">
    WHAT WE MEASURE
  </p>
  <p style="color:#bbb;font-size:0.85rem;line-height:1.65;margin:0 0 20px 0;font-family:monospace">
    The dashboard tracks several distinct signals. <strong style="color:#E8E8F0">Implied volatility</strong>
    measures what the options market is pricing in as future realised movement.
    <strong style="color:#E8E8F0">Model-free IV (MFIV)</strong> integrates the entire options smile
    rather than a single at-the-money strike, giving a more complete picture of
    aggregate uncertainty. <strong style="color:#E8E8F0">BKM moments</strong> (risk-neutral skewness
    and kurtosis) reveal how the market is pricing the shape of the return
    distribution — not just its width. <strong style="color:#E8E8F0">Term structure slope</strong>
    captures whether near-dated volatility is trading at a premium to longer-dated
    volatility, a historically reliable stress indicator. These are read as a
    composite, not in isolation.
  </p>

  <p style="color:#00D4FF;font-size:0.78rem;margin:0 0 8px 0;font-family:monospace;font-weight:700;letter-spacing:0.08em">
    HOW WE VALIDATE
  </p>
  <p style="color:#bbb;font-size:0.85rem;line-height:1.65;margin:0 0 20px 0;font-family:monospace">
    The core problem in quantitative research is that if you test enough ideas,
    some will look good purely by chance. We address this directly. Every signal
    is evaluated on data it never touched during development — a held-out
    out-of-sample period starting January 2025. We apply Benjamini-Hochberg false
    discovery rate correction across all tests, which controls the expected
    proportion of false positives when testing many signals simultaneously.
    Confidence intervals are computed via stationary block bootstrap, a method
    that accounts for the autocorrelation present in daily volatility data —
    standard p-values assume independence between observations, which daily vol
    series do not have. Finally, we strip out common market factors (Fama-French
    5-factor + momentum) to confirm predictive power is genuine alpha rather than
    disguised exposure to broad market moves.
  </p>
  <p style="color:#bbb;font-size:0.85rem;line-height:1.65;margin:0 0 20px 0;font-family:monospace">
    The result: our primary composite signal shows an out-of-sample information
    coefficient of +0.55 across 343 trading days, with all five complete quarters
    independently statistically robust under block bootstrap. The factor-adjusted
    IC — after stripping market exposure — remains significant at +0.20.
  </p>

  <p style="color:#00D4FF;font-size:0.78rem;margin:0 0 8px 0;font-family:monospace;font-weight:700;letter-spacing:0.08em">
    WHAT THIS IS NOT
  </p>
  <p style="color:#888;font-size:0.82rem;line-height:1.65;margin:0;font-family:monospace">
    This dashboard presents research and historical data only. It is not
    investment advice, a personalised recommendation, or a signal service.
    We describe our own research observations and positioning; readers are
    responsible for their own trading decisions.
  </p>

</div>
    """,
    unsafe_allow_html=True,
)

# Email list capture — set buttondown_username in Streamlit Cloud secrets to activate
_bd_user = st.secrets.get("buttondown_username")
if _bd_user:
    st.markdown(
        f"""
<div style="background:#111118;border:1px solid #1e1e2e;border-radius:8px;
            padding:20px 24px;margin:8px 0;max-width:500px">
  <p style="color:#E8E8F0;font-size:0.9rem;margin:0 0 4px 0;font-family:monospace;font-weight:700">
    Daily vol regime updates
  </p>
  <p style="color:#888;font-size:0.8rem;margin:0 0 14px 0;font-family:monospace">
    One email per signal day · No spam · Unsubscribe anytime
  </p>
  <form action="https://buttondown.email/api/emails/embed-subscribe/{_bd_user}"
        method="post"
        target="popupwindow"
        onsubmit="window.open('https://buttondown.email/{_bd_user}', 'popupwindow')"
        style="display:flex;gap:8px;flex-wrap:wrap">
    <input type="email" name="email" placeholder="your@email.com"
           style="flex:1;min-width:200px;background:#0A0A0F;border:1px solid #333;
                  color:#E8E8F0;padding:9px 12px;border-radius:4px;
                  font-size:0.85rem;font-family:monospace"/>
    <input type="submit" value="Subscribe"
           style="background:#00D4FF;color:#0A0A0F;border:none;padding:9px 18px;
                  border-radius:4px;font-weight:700;font-size:0.85rem;
                  font-family:monospace;cursor:pointer;white-space:nowrap"/>
  </form>
</div>
        """,
        unsafe_allow_html=True,
    )

st.caption("Volantis — Quantitative volatility intelligence. Updated daily after market close.")
