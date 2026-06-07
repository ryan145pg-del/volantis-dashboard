"""
implied_vol.py — Panel 2: Implied Volatility (SPY / QQQ tabs).

Shows ATM IV vs 20-day mean, vol spread, IV percentile rank, and term structure slope.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import get_iv_data

_CYAN = "#00D4FF"
_BLUE = "#4B9FFF"


def _iv_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    df30 = df.tail(90)
    mean20 = df["atm_iv"].rolling(20).mean().reindex(df.index).tail(90)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df30["date"], y=df30["atm_iv"],
        name="ATM IV",
        line=dict(color=_CYAN, width=2),
    ))
    fig.add_trace(go.Scatter(
        x=df30["date"], y=mean20,
        name="20d mean",
        line=dict(color=_BLUE, width=1.2, dash="dot"),
    ))
    fig.update_layout(
        title=f"{symbol} ATM IV — 90 days",
        xaxis_title=None,
        yaxis_title="Implied Volatility",
        yaxis_tickformat=".1%",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111118",
        legend=dict(orientation="h", y=1.08),
        margin=dict(l=0, r=0, t=36, b=0),
        height=280,
    )
    return fig


def _render_symbol(symbol: str) -> None:
    df = get_iv_data(symbol)
    if df.empty:
        st.warning(f"{symbol} IV data unavailable.")
        return

    latest = df.iloc[-1]
    atm_iv  = latest["atm_iv"]
    vol_spr = latest["vol_spread"]
    ts_slope = latest["ts_slope"]

    # IV percentile rank over full history
    iv_rank = df["atm_iv"].rank(pct=True).iloc[-1]

    mean20_current = df["atm_iv"].rolling(20).mean().iloc[-1]
    iv_vs_mean = atm_iv - mean20_current if not pd.isna(mean20_current) else float("nan")

    col1, col2, col3 = st.columns(3)
    with col1:
        delta_str = f"{iv_vs_mean:+.1%}" if not pd.isna(iv_vs_mean) else None
        st.metric("ATM IV", f"{atm_iv:.1%}", delta=delta_str,
                  delta_color="inverse", help="vs 20-day rolling mean")
    with col2:
        spr_str = f"{vol_spr:+.1%}" if not pd.isna(vol_spr) else "—"
        st.metric("Vol Spread (IV − RV20)", spr_str,
                  help="Positive = IV > realised; favours short-vol")
    with col3:
        st.metric("IV Rank (full history)", f"{iv_rank:.0%}")

    st.plotly_chart(_iv_chart(df, symbol), use_container_width=True,
                    config={"displayModeBar": False})

    if not pd.isna(ts_slope):
        slope_label = "Contango (normal)" if ts_slope > 0 else "Backwardation (stress)"
        st.caption(f"Term structure slope: {ts_slope:+.4f} — {slope_label}")


def render_implied_vol() -> None:
    st.subheader("Implied Volatility")
    spy_tab, qqq_tab = st.tabs(["SPY", "QQQ"])
    with spy_tab:
        _render_symbol("SPY")
    with qqq_tab:
        _render_symbol("QQQ")
