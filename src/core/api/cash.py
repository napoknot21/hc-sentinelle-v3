from __future__ import annotations

import os
import subprocess
import pandas as pd
import polars as pl
import yfinance as yf
import datetime as dt

from typing import List, Dict, Optional, Tuple, Any

from src.core.api.client import get_ice_calculator, get_trade_manager
from src.config.parameters import FUND_NAME_MAP, PAIRS
from src.config.paths import CASH_UPDATER_PATH
from src.utils.formatters import date_to_str, normalize_fx_dict


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


def run_cash_updater (

        date : Optional[str | dt.date | dt.datetime] = None,
        fund : Optional[str] = None,

        cash_updater_path : Optional[str] = None,
        fund_map : Optional[Dict] = None,

    ) -> Dict[str, Any] :
    """
    Launch the external cash-updater project for one fund and one date.
    """
    date = date_to_str(date)
    
    fund_map = FUND_NAME_MAP if fund is None else fund
    cash_updater_path = CASH_UPDATER_PATH if cash_updater_path is None else cash_updater_path

    full_fund = fund_map.get(fund, None)

    if full_fund is None :
        return None

    command = [
    
        "python", "main.py", "--start-date", date, "--end-date", date, "--fund", fund,
    
    ]

    try :

        completed_process = subprocess.run(

            command,
            cwd=cash_updater_path,
            capture_output=True,
            text=True,

        )

        success = completed_process.returncode == 0

        return {

            "success" : success,
            "message" : (
                f"Cash refreshed for {fund} on {date}"
                if success
                else f"Cash refresh failed for {fund} on {date}"
            ),
            "command" : " ".join(command),
            "returncode" : completed_process.returncode,
            "stdout" : completed_process.stdout,
            "stderr" : completed_process.stderr,

        }

    except Exception as e :

        return {

            "success" : False,
            "message" : f"Cash refresh failed for {fund} on {date}: {e}",
            "command" : " ".join(command),
            "returncode" : None,
            "stdout" : "",
            "stderr" : str(e),

        }


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



