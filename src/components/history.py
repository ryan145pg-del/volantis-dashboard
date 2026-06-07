"""
history.py — Panel 5: Historical Context (90-day rolling chart).

ATM IV for SPY and QQQ on the primary axis, VIX on a secondary axis.
RV20 as dotted lines to visualise the vol risk premium (IV − RV gap).
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from src.data_loader import get_history_data


def _history_chart(spy_df: pd.DataFrame, qqq_df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if not spy_df.empty:
        fig.add_trace(go.Scatter(
            x=spy_df["date"], y=spy_df["atm_iv"],
            name="SPY ATM IV", line=dict(color="#00D4FF", width=2),
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=spy_df["date"], y=spy_df["rv_20d"],
            name="SPY RV20", line=dict(color="#00D4FF", width=1, dash="dot"),
            showlegend=True,
        ), secondary_y=False)
        vix_series = spy_df.dropna(subset=["vix"])
        if not vix_series.empty:
            fig.add_trace(go.Scatter(
                x=vix_series["date"], y=vix_series["vix"],
                name="VIX", line=dict(color="#888888", width=1.2, dash="dash"),
            ), secondary_y=True)

    if not qqq_df.empty:
        fig.add_trace(go.Scatter(
            x=qqq_df["date"], y=qqq_df["atm_iv"],
            name="QQQ ATM IV", line=dict(color="#4B9FFF", width=2),
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=qqq_df["date"], y=qqq_df["rv_20d"],
            name="QQQ RV20", line=dict(color="#4B9FFF", width=1, dash="dot"),
            showlegend=True,
        ), secondary_y=False)

    fig.update_layout(
        title="90-day IV History",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111118",
        legend=dict(orientation="h", y=1.08),
        margin=dict(l=0, r=0, t=36, b=0),
        height=320,
    )
    fig.update_yaxes(title_text="Implied / Realised Vol", tickformat=".1%",
                     secondary_y=False)
    fig.update_yaxes(title_text="VIX", secondary_y=True)
    return fig


def render_history() -> None:
    st.subheader("Historical Context — 90 Days")

    spy_df = get_history_data("SPY")
    qqq_df = get_history_data("QQQ")

    if spy_df.empty and qqq_df.empty:
        st.warning("Historical data unavailable.")
        return

    st.plotly_chart(_history_chart(spy_df, qqq_df), use_container_width=True,
                    config={"displayModeBar": False})
    st.caption(
        "Solid lines = ATM implied vol · Dotted lines = 20-day realised vol · "
        "Grey dashed = VIX (right axis). "
        "Gap between IV and RV represents the vol risk premium."
    )
