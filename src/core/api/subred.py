from __future__ import annotations

import os
import json
import hashlib
import yfinance as yf
import polars as pl
import pandas as pds
import datetime as dt
import streamlit as st

from typing import Optional, List, Dict, Any

from src.core.api.client import get_trade_manager
from src.config.parameters import FUND_HV, SUBRED_BOOKS_FUNDS, SUBRED_STRUCT_COLUMNS, SUBRED_COLS_NEEDED
from src.config.paths import CASH_UPDATER_FX_VALUES_PATH
from src.utils.formatters import date_to_str, str_to_date, format_numeric_columns_to_string


def get_subred_by_date (
        
        date : Optional[str | dt.datetime | dt.date] = None,

        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        books_by_fund : Optional[Dict] = None,
        schema_overrides : Optional[Dict] = None,

    ) -> Optional[Dict] :
    """
    
    """

    dataframe, md5 = fetch_subred_by_date(date, books_by_fund, schema_overrides) if dataframe is None else (dataframe, md5)
    
    df_grouped = _clean_response_api(dataframe, books_by_fund)
    df_converted = _convert_to_base_ccy(df_grouped, base_ccy="EUR")
    #df_grouped = format_numeric_columns_to_string(df_grouped)

    aum_dict = _build_fund_dictionary(df_converted, books_by_fund)
    #aum_dict = format_aum_dict(aum_dict)  

    return aum_dict


def fetch_subred_by_date (
        
        date : Optional[str | dt.datetime | dt.date] = None,

        books_by_fund : Optional[Dict] = None,
        schema_overrides : Optional[Dict] = None,
    
    ) :
    """
    Docstring for get_df_subred_by_date
    
    :param date: Description
    :type date: Optional[str | dt.datetime | dt.date]
    :param books_by_fund: Description
    :type books_by_fund: Optional[Dict]
    :param schema_overrides: Description
    :type schema_overrides: Optional[Dict]
    """
    date = str_to_date(date)
    dataframe = api_call_subred(date, books_by_fund, schema_overrides)

    df_filter = dataframe.filter(pl.col("tradeType") == "SUBRED")
    #df_sort = dataframe.sort(pl.col("instrument").struct.field("deliveryDate").str.to_date(format))
    
    return df_filter, None# md5_hash



def api_call_subred (
        
        date : Optional[str | dt.datetime | dt.date] = None,

        books_by_fund : Optional[Dict] = None,
        schema_overrides : Optional[Dict] = None,

        trade_manager : Optional[Any] = None,
        loopback : int = 5

    ) -> Optional[pl.DataFrame] :
    """
    
    """
    if loopback < 0 : 
        
        print("\n[-] Error using the API, try later")
        return None
    
    date = str_to_date(date)
    trade_manager = get_trade_manager() if trade_manager is None else trade_manager

    schema_overrides = SUBRED_COLS_NEEDED if schema_overrides is None else schema_overrides
    specific_cols = list(schema_overrides.keys())

    books_by_fund = SUBRED_BOOKS_FUNDS if books_by_fund is None else books_by_fund
    books = [book for sublist in books_by_fund.values() for book in sublist]
    print(books)

    response : Dict[List] = trade_manager.get_info_trades_from_books(books=books)

    if response is None :

        print("\n[!] Retrying the API...")
        return api_call_subred(date, loopback=loopback-1)

    tradelegs : List[Dict] = response.get("tradeLegs")

    dataframe = pl.DataFrame(tradelegs, schema_overrides=schema_overrides).select(specific_cols)
    #print(dataframe)
    
    return dataframe


def _clean_response_api (
        
        dataframe : Optional[pl.DataFrame] = None,

        books_by_fund : Optional[Dict] = None,
        format : str = "%Y-%m-%d"

    ) -> Optional[pl.DataFrame] :
    """
    
    """
    if dataframe is None :
        
        return None

    books_by_fund = SUBRED_BOOKS_FUNDS if books_by_fund is None else books_by_fund

    df_sort = dataframe.sort(pl.col("instrument").struct.field("deliveryDate").str.to_date(format))
    df_filter = df_sort.filter(pl.col("tradeType") == "SUBRED")

    df = df_filter.with_columns(

        [
            pl.when(pl.col("tradeLegCode") == "RED")
                .then(-pl.col("instrument").struct.field("notional"))
                .otherwise(pl.col("instrument").struct.field("notional"))
                .alias("signed_notional")
        ]

    )

    df_grouped = (
        
        df.group_by("bookName")
        .agg(

            [
                pl.col("signed_notional").sum().alias("total_signed_notional").cast(pl.Int128),
                pl.col("instrument").struct.field("currency").first().alias("currency"),

            ]
        )

    )

    print(df_grouped)

    return df_grouped


def _convert_to_base_ccy (
        
        dataframe   : Optional[pl.DataFrame] = None,
        
        base_ccy    : str = "EUR",
        fx_filepath : Optional[str] = None,
    
    ) -> Optional[pl.DataFrame] :
    """
    Converts the total_signed_notional of each book row to base_ccy in-place.
    Adds a 'converted_notional' column and normalizes 'currency' to base_ccy.
    """
    if dataframe is None :
        return None

    fx_filepath  = CASH_UPDATER_FX_VALUES_PATH if fx_filepath is None else fx_filepath
    local_rates  = _load_local_fx_rates(fx_filepath)

    def convert_row (notional : float, ccy : str) -> float :
        """
        
        """
        rate = resolve_fx_rate(ccy, base_ccy, local_rates=local_rates)
        
        if rate is None or rate == 0.0 :

            print(f"[-] No FX rate for {ccy}, using 1.0")
            rate = 1.0

        return notional / rate

    converted = [
        convert_row(row["total_signed_notional"], row["currency"])
        for row in dataframe.to_dicts()
    ]

    dataframe = dataframe.with_columns(
        [
            pl.Series("total_signed_notional", converted, dtype=pl.Float64),
            pl.lit(base_ccy).alias("currency"),
        ]
    )

    return dataframe


def _build_fund_dictionary (
        
        dataframe     : Optional[pl.DataFrame] = None,
        books_by_fund : Optional[Dict] = None,
        base_ccy      : str = "EUR",
    
    ) -> Optional[Dict] :

    books_by_fund = SUBRED_BOOKS_FUNDS if books_by_fund is None else books_by_fund

    aum = {row["bookName"] : row for row in dataframe.to_dicts()}
    result = {}

    for fund, books in books_by_fund.items() :

        total        = 0.0
        missing_books = []

        for book in books :

            dict_by_book = aum.get(book)
            
            if dict_by_book is None :
            
                missing_books.append(book)
                continue
            
            total += float(dict_by_book["total_signed_notional"])

        if missing_books :
            print(f"[!] Fund '{fund}' — books not found: {missing_books}")

        result[fund] = {
            "amount"  :  f"{round(total, 2):,.2f}",
            "currency": base_ccy,
        }

    return result


def resolve_fx_rate (
        
        from_ccy : str,
        to_ccy : str = "EUR",
        
        local_rates : Optional[Dict[str, float]] = None,
        fx_filepath : Optional[str] = None,
    
    ) -> Optional[float] :
    """
    Resolve FX rate from_ccy -> to_ccy.
    1. Returns 1.0 immediately if same currency.
    2. Tries local JSON rates file.
    3. Falls back to yfinance live rate.
    """
    if from_ccy == to_ccy :
        return 1.0

    # Load local file if not already passed in
    fx_filepath = CASH_UPDATER_FX_VALUES_PATH if fx_filepath is None else fx_filepath
    local_rates = _load_local_fx_rates(fx_filepath) if local_rates is None else local_rates

    if local_rates is not None :

        rate = local_rates.get(from_ccy)

        if rate is not None:
        
            print(f"[+] [local] {from_ccy} -> {to_ccy} : {rate}")
            return rate
        
    # Fallback to yfinance
    print(f"[!] {from_ccy} not in local rates, falling back to yfinance...")
    
    return _get_fx_rate_yfinance(from_ccy, to_ccy)



def _load_local_fx_rates (file_abs_path : Optional[str] = None) -> Dict[str, float] :
    """
    Load FX rates from a local JSON file.
    Expected format: { "USD": 1.08, "GBP": 0.86, "CHF": 0.97, ... }
    Keys are currencies, values are rate TO EUR (i.e. 1 CCY = X EUR).
    """
    file_abs_path = CASH_UPDATER_FX_VALUES_PATH if file_abs_path is None else file_abs_path

    if not os.path.exists(file_abs_path) :
        
        print(f"[!] FX file not found at {file_abs_path}")
        return None

    with open(file_abs_path, "r") as f :
        return json.load(f)



def _get_fx_rate_yfinance (from_ccy : str, to_ccy : str = "EUR", loopback : int = 5) -> Optional[float] :
    """
    Fetch live FX rate from yfinance as fallback.
    Returns how much 1 unit of from_ccy is worth in to_ccy.
    """
    if loopback == 0 :
        
        print(f"[-] yfinance failed after retries for {from_ccy}->{to_ccy}")
        return 1.0
    
    if from_ccy == to_ccy :
        return 1.0

    ticker = f"{from_ccy}{to_ccy}=X"

    try :

        data = yf.Ticker(ticker).fast_info
        rate = data["lastPrice"]
        
        print(f"\n[+] [yfinance] {from_ccy} -> {to_ccy} : {rate}")
    
    except Exception as e :

        print(f"[!] Retrying the YFinance API...\n")
        return _get_fx_rate_yfinance(from_ccy, to_ccy, loopback - 1)
    
    return rate
