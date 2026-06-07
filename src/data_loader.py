"""
data_loader.py — Download the dashboard bundle from Cloudflare R2 and expose
per-panel query functions, each cached independently for 1 hour.

Credentials are read exclusively from st.secrets["r2"] — never from .env or
environment variables. This repo is public; no secrets may appear in source.

Bundle key: db/dashboard_bundle.duckdb (~1.5 MB)
Tables available: vix_signal, macro_signal, mfiv_signal, bkm_signal, feature_store
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st
import boto3
from botocore.exceptions import BotoCoreError, ClientError

BUNDLE_R2_KEY = "db/dashboard_bundle.duckdb"
UNAVAILABLE_MSG = (
    "Dashboard data temporarily unavailable — pipeline updating. "
    "Please check back after 17:00 ET."
)


def _make_r2_client():
    r2 = st.secrets["r2"]
    return boto3.client(
        "s3",
        endpoint_url=r2["endpoint"],
        aws_access_key_id=r2["access_key_id"],
        aws_secret_access_key=r2["secret_access_key"],
        region_name="auto",
    )


@st.cache_resource(ttl=3600)
def _get_db_path() -> str | None:
    """Download the dashboard bundle from R2. Cached for 1 hour across all sessions."""
    try:
        client = _make_r2_client()
        bucket = st.secrets["r2"]["bucket"]
        db_path = Path(tempfile.gettempdir()) / "volantis_bundle.duckdb"
        client.download_file(bucket, BUNDLE_R2_KEY, str(db_path))
        return str(db_path)
    except (BotoCoreError, ClientError, KeyError, Exception):
        return None


def _query(sql: str, params: list | None = None) -> pd.DataFrame:
    db = _get_db_path()
    if not db:
        return pd.DataFrame()
    try:
        with duckdb.connect(db, read_only=True) as conn:
            return conn.execute(sql, params or []).df()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_regime_data() -> pd.DataFrame:
    """VIX + HY spread for the last 90 days. Used by the Regime panel."""
    return _query("""
        SELECT v.trade_date,
               v.vix, v.vix_9d, v.vix_3m, v.vvix,
               m.hy_spread
        FROM vix_signal v
        LEFT JOIN macro_signal m ON v.trade_date = m.trade_date
        ORDER BY v.trade_date DESC
        LIMIT 90
    """)


@st.cache_data(ttl=3600)
def get_iv_data(symbol: str) -> pd.DataFrame:
    """ATM IV, vol spread, term structure slope, RV20 — full history for percentile rank."""
    return _query(
        "SELECT date, atm_iv, vol_spread, ts_slope, rv_20d "
        "FROM feature_store WHERE symbol = ? ORDER BY date",
        [symbol],
    )


@st.cache_data(ttl=3600)
def get_mfiv_data(symbol: str) -> pd.DataFrame:
    """MFIV alongside ATM IV for divergence display."""
    return _query(
        "SELECT fs.date, fs.atm_iv, ms.mfiv_30d "
        "FROM feature_store fs "
        "LEFT JOIN mfiv_signal ms ON fs.date = ms.trade_date AND ms.symbol = fs.symbol "
        "WHERE fs.symbol = ? ORDER BY fs.date",
        [symbol],
    )


@st.cache_data(ttl=3600)
def get_bkm_data(symbol: str) -> pd.DataFrame:
    """Risk-neutral skewness and kurtosis from BKM moments."""
    return _query(
        "SELECT trade_date, rn_skew_30d, rn_kurt_30d "
        "FROM bkm_signal WHERE symbol = ? ORDER BY trade_date",
        [symbol],
    )


@st.cache_data(ttl=3600)
def get_history_data(symbol: str) -> pd.DataFrame:
    """90-day ATM IV + RV20 + VIX for the historical context chart."""
    return _query(
        "SELECT fs.date, fs.atm_iv, fs.rv_20d, vs.vix "
        "FROM feature_store fs "
        "LEFT JOIN vix_signal vs ON fs.date = vs.trade_date "
        "WHERE fs.symbol = ? "
        "  AND fs.date >= CURRENT_DATE - INTERVAL 90 DAYS "
        "ORDER BY fs.date",
        [symbol],
    )
