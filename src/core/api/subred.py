from __future__ import annotations

import os
import hashlib
import polars as pl
import pandas as pd
import datetime as dt
import streamlit as st

from typing import Optional, List, Dict, Any

from src.core.api.client import get_trade_manager
from src.config.parameters import FUND_HV, SUBRED_BOOKS_FUNDS, SUBRED_STRUCT_COLUMNS, SUBRED_COLS_NEEDED
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
    df_grouped = format_numeric_columns_to_string(df_grouped)
    
    aum_dict = _build_fund_dictionary(df_grouped, books_by_fund)

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
    books = list(books_by_fund.values())

    response : Dict[List] = trade_manager.get_info_trades_from_books(books=books)

    if response is None :

        print("\n[!] Retrying the API...")
        return api_call_subred(date, loopback=loopback-1)

    tradelegs : List[Dict] = response.get("tradeLegs")

    dataframe = pl.DataFrame(tradelegs, schema_overrides=schema_overrides).select(specific_cols)
    print(dataframe)
    
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


def _build_fund_dictionary (
        
        dataframe : Optional[pl.DataFrame] = None,
        books_by_fund : Optional[Dict] = None
    
    ) -> Optional[Dict] :
    """


    """
    books_by_fund = SUBRED_BOOKS_FUNDS if books_by_fund is None else books_by_fund

    aum = {

        row["bookName"] : row
        for row in dataframe.select(dataframe.columns).to_dicts()

    }

    result = {}

    for fundation, book in books_by_fund.items() :

        result[fundation] = {}
        dict_by_book : Dict[str, str] = aum.get(book)

        result[fundation]["amount"] = dict_by_book["total_signed_notional"]
        result[fundation]["currency"] = dict_by_book["currency"]

    print(result)
    return result


        
