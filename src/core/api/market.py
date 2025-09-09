from __future__ import annotations

import os
import hashlib
import datetime as dt
import streamlit as st
import polars as pl

from typing import List, Dict, Tuple, Optional

from src.config.parameters import FUND_HV
from src.core.api.client import get_ice_calculator, get_trade_manager

from src.utils.logger import log
from src.utils.formatters import date_to_str


@st.cache_resource
def fetch_raw_market_value_data (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fund : Optional[str] = None

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]] :
    """
    
    """
    date = date_to_str(date)
    fund = FUND_HV if fund is None else fund

    calculator = get_ice_calculator()

    try :

        mv_n_greeks = calculator.get_mv_n_greeks_daily(date)

    except Exception as e :

        log(f"[-] API exception during fetching Market value : {e}", "error")
        return None

    df_mv_greeks = pl.json_normalize(mv_n_greeks)
    md5_hash = hashlib.md5(df_mv_greeks.write_parquet()).hexdigest()

    return df_mv_greeks, md5_hash
