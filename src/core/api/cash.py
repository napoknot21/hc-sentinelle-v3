from __future__ import annotations

import os
import pandas as pd
import polars as pl
import yfinance as yf
import datetime as dt

from typing import List, Dict, Optional, Tuple, Any

from src.core.api.client import get_ice_calculator, get_trade_manager
from src.config.parameters import FUND_NAME_MAP, PAIRS
from src.utils.formatters import date_to_str, normalize_fx_dict


def get_cash (
        
        fund : Optional[str] = None,
        date : Optional[str] = None,

        books : Optional[List[str]] = None,

        tm : Optional[Any] = None,
        ic : Optional[Any] = None,

    ) -> Optional[pl.DataFrame] :
    """
    
    """
    fund = FUND_NAME_MAP if fund is None else fund
    date = date_to_str(date) if date is None else date


    ic = get_ice_calculator() if tm is None else tm
    tm = get_trade_manager() if ic is None else ic



def call_api_for_pairs (
    
        target_date : Optional[str | dt.datetime] = None,
        pairs : Optional[List[str]] = None,
        loopback : int = 3
    
    ) -> Optional[Dict[str, float]] :
    """
    
    """
    if loopback == 0 :

        print("\n[-] YFinance API error. Reload the script")
        return None

    pairs = PAIRS if pairs is None else pairs
    target_date = date_to_str(target_date)

    conversion = yf.download(tickers=pairs, start=target_date, progress=False, threads=True, auto_adjust=False)

    conversion.index = pd.to_datetime(conversion.index)

    if target_date in conversion.index :
        row = conversion.loc[target_date]
        
    else :
        row = conversion.loc[conversion.index.get_indexer([target_date], method="nearest")][0]

    close_values = row["Close"].to_dict()

    if check_nan_into_values(target_date, pairs, close_values) :

        print("\n[!] Missing value for conversion. Retrying...")
        return call_api_for_pairs(target_date, pairs, loopback - 1)

    print(f"\n[+] Close values at {target_date} :")

    return normalize_fx_dict(close_values)


def check_nan_into_values (
        
        target_date : Optional[str | dt.datetime] = None,
        pairs : Optional[List[str]] = None,
        conversion : Optional[dict[str, float]] = None
    
    ) -> bool :
    """
    
    """
    conversion = call_api_for_pairs(target_date, pairs) if conversion is None else conversion

    for v in conversion.values() :

        if pd.isna(v) :
            return True

    return False



