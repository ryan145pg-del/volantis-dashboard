"""
bkm.py — Panel 4: BKM Risk-Neutral Moments.

Displays risk-neutral skewness and kurtosis from the Bakshi-Kapadia-Madan (2003)
spanning formula. Shows last available values with explicit data freshness.
Never crashes on staleness — shows a warning instead.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import get_bkm_data

_CYAN = "#00D4FF"
_BLUE = "#4B9FFF"

# 5 trading days ≈ 7 calendar days
_STALE_CALENDAR_DAYS = 7


def _skew_chart(spy_df: pd.DataFrame, qqq_df: pd.DataFrame) -> go.Figure:
    spy60 = spy_df.dropna(subset=["rn_skew_30d"]).tail(60)
    qqq60 = qqq_df.dropna(subset=["rn_skew_30d"]).tail(60)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=spy60["trade_date"], y=spy60["rn_skew_30d"],
        name="SPY skew", line=dict(color=_CYAN, width=2),
    ))
    fig.add_trace(go.Scatter(
        x=qqq60["trade_date"], y=qqq60["rn_skew_30d"],
        name="QQQ skew", line=dict(color=_BLUE, width=2),
    ))
    fig.add_hline(y=0, line=dict(color="#555", width=1, dash="dot"))
    fig.update_layout(
        title="Risk-Neutral Skewness — 60 days",
        xaxis_title=None,
        yaxis_title="RN Skewness",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111118",
        legend=dict(orientation="h", y=1.08),
        margin=dict(l=0, r=0, t=36, b=0),
        height=240,
    )
    return fig


def _render_symbol(df: pd.DataFrame, symbol: str) -> None:
    last = df.dropna(subset=["rn_skew_30d"]).iloc[-1] if not df.empty else None
    skew = last["rn_skew_30d"] if last is not None else float("nan")
    kurt = last["rn_kurt_30d"] if last is not None else float("nan")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"{symbol} RN Skewness",
                  f"{skew:.3f}" if not pd.isna(skew) else "—",
                  help="Negative = left tail heavier (put fear)")
    with col2:
        st.metric(f"{symbol} RN Kurtosis",
                  f"{kurt:.1f}" if not pd.isna(kurt) else "—",
                  help="High kurtosis = fat tails / elevated vol-of-vol")


def render_bkm() -> None:
    st.subheader("BKM Risk-Neutral Moments")

    spy_df = get_bkm_data("SPY")
    qqq_df = get_bkm_data("QQQ")

    if spy_df.empty and qqq_df.empty:
        st.warning("BKM data unavailable.")
        return

    # Staleness check
    last_date = None
    for df in (spy_df, qqq_df):
        if not df.empty:
            d = pd.to_datetime(df["trade_date"]).max()
            last_date = d if last_date is None else max(last_date, d)

    if last_date is not None:
        days_stale = (pd.Timestamp.today().normalize() - last_date).days
        if days_stale > _STALE_CALENDAR_DAYS:
            st.warning(
                f"BKM data last updated {days_stale} days ago — "
                "cloud pipeline optimisation in progress. "
                "Values below reflect last available reading."
            )

    _render_symbol(spy_df, "SPY")
    _render_symbol(qqq_df, "QQQ")

    if not spy_df.empty or not qqq_df.empty:
        st.plotly_chart(_skew_chart(spy_df, qqq_df), use_container_width=True,
                        config={"displayModeBar": False})

    if last_date is not None:
        st.caption(f"BKM data as of {last_date.date()}")
