"""
regime.py — Panel 1: Regime Overview.

Displays current VIX level, VIX term structure (contango/backwardation),
HY credit spread, and a regime classification badge.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _regime_label(vix: float) -> tuple[str, str]:
    """Return (label, colour) for VIX level."""
    if vix <= 18:
        return "CALM", "#00D4FF"
    if vix <= 25:
        return "ELEVATED", "#FFB347"
    return "STRESS", "#FF4B4B"


def _ts_label(vix_9d: float, vix: float, vix_3m: float) -> str:
    if pd.isna(vix_9d) or pd.isna(vix_3m):
        return "Term structure unavailable"
    if vix_9d < vix < vix_3m:
        return "Contango — normal"
    if vix_9d > vix:
        return "Backwardation — stress signal"
    return "Flat"


def _hy_label(hy: float) -> tuple[str, str]:
    if pd.isna(hy):
        return "N/A", "#888"
    if hy < 3.0:
        return "CLEAR", "#00D4FF"
    if hy <= 5.0:
        return "ELEVATED", "#FFB347"
    return "STRESS", "#FF4B4B"


def _sparkline(series: pd.Series) -> go.Figure:
    fig = go.Figure(go.Scatter(
        y=series,
        mode="lines",
        line=dict(color="#00D4FF", width=1.5),
        hoverinfo="skip",
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=48,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def render_regime(df: pd.DataFrame) -> None:
    st.subheader("Regime Overview")

    if df.empty:
        st.warning("Regime data unavailable.")
        return

    latest = df.iloc[0]
    vix     = latest["vix"]
    vix_9d  = latest["vix_9d"]
    vix_3m  = latest["vix_3m"]
    hy      = latest.get("hy_spread", float("nan"))

    label, colour = _regime_label(vix)
    hy_label, hy_colour = _hy_label(hy)
    ts_text = _ts_label(vix_9d, vix, vix_3m)

    # Regime badge
    st.markdown(
        f"<span style='font-size:1.4rem;font-weight:700;color:{colour}'>"
        f"● {label}</span>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("VIX", f"{vix:.2f}" if not pd.isna(vix) else "—")
    with col2:
        st.metric("Term Structure", ts_text)
    with col3:
        hy_val = f"{hy:.2f}" if not pd.isna(hy) else "—"
        st.metric(
            "HY Spread",
            hy_val,
            delta=hy_label,
            delta_color="off",
        )

    # VIX 5-day sparkline
    vix_series = df["vix"].dropna().iloc[:5][::-1]
    if len(vix_series) >= 2:
        st.plotly_chart(_sparkline(vix_series), use_container_width=True,
                        config={"displayModeBar": False})

    # VVIX context
    vvix = latest.get("vvix")
    if not pd.isna(vvix):
        st.caption(f"VVIX (vol-of-vol): {vvix:.1f}")

    # Freshness
    last_date = df["trade_date"].max()
    st.caption(f"Last updated: {last_date}")
