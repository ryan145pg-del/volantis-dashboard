"""
mfiv.py — Panel 3: Model-Free Implied Volatility.

Compares MFIV (full-smile integral) vs ATM IV and shows the 60-day rolling trend.
Divergence = tails priced more richly than the ATM strike alone.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import get_mfiv_data

_CYAN = "#00D4FF"
_BLUE = "#4B9FFF"


def _mfiv_chart(spy_df: pd.DataFrame, qqq_df: pd.DataFrame) -> go.Figure:
    spy60 = spy_df.dropna(subset=["mfiv_30d"]).tail(60)
    qqq60 = qqq_df.dropna(subset=["mfiv_30d"]).tail(60)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=spy60["date"], y=spy60["mfiv_30d"],
        name="SPY MFIV", line=dict(color=_CYAN, width=2),
    ))
    fig.add_trace(go.Scatter(
        x=qqq60["date"], y=qqq60["mfiv_30d"],
        name="QQQ MFIV", line=dict(color=_BLUE, width=2),
    ))
    fig.update_layout(
        title="MFIV — 60 days",
        xaxis_title=None,
        yaxis_title="MFIV (annualised)",
        yaxis_tickformat=".1%",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111118",
        legend=dict(orientation="h", y=1.08),
        margin=dict(l=0, r=0, t=36, b=0),
        height=280,
    )
    return fig


def render_mfiv() -> None:
    st.subheader("Model-Free Implied Volatility")
    st.caption(
        "MFIV integrates the full option smile; ATM IV uses only the at-the-money strike. "
        "Divergence (MFIV > ATM IV) indicates elevated tail-risk pricing."
    )

    spy_df = get_mfiv_data("SPY")
    qqq_df = get_mfiv_data("QQQ")

    if spy_df.empty and qqq_df.empty:
        st.warning("MFIV data unavailable.")
        return

    def _latest_metrics(df: pd.DataFrame, symbol: str) -> None:
        last = df.dropna(subset=["mfiv_30d", "atm_iv"]).iloc[-1] if not df.empty else None
        if last is None:
            st.metric(f"{symbol} MFIV", "—")
            return
        mfiv = last["mfiv_30d"]
        atm  = last["atm_iv"]
        div  = mfiv - atm if not pd.isna(atm) else float("nan")
        col_mfiv, col_atm, col_div = st.columns(3)
        with col_mfiv:
            st.metric(f"{symbol} MFIV", f"{mfiv:.1%}")
        with col_atm:
            st.metric(f"{symbol} ATM IV", f"{atm:.1%}" if not pd.isna(atm) else "—")
        with col_div:
            st.metric("Divergence", f"{div:+.1%}" if not pd.isna(div) else "—",
                      help="MFIV − ATM IV; positive = tail premium elevated")

    _latest_metrics(spy_df, "SPY")
    _latest_metrics(qqq_df, "QQQ")

    if not spy_df.empty or not qqq_df.empty:
        st.plotly_chart(_mfiv_chart(spy_df, qqq_df), use_container_width=True,
                        config={"displayModeBar": False})
