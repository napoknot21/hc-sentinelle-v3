from __future__ import annotations

import os
import polars as pl
import datetime as dt
import streamlit as st

from typing import Optional, List, Tuple
from st_aggrid import AgGrid

from src.ui.styles.base import screeners_js_code, screeners_custom_css

from src.ui.components.text import center_h1, center_h2, left_h5
from src.ui.components.tables import show_screener_tarf_table

from src.core.data.screeners import read_fx_carry_by_date, read_tail_trades_by_date, read_tarf_by_date, find_most_recent_file_by_date

from src.utils.formatters import filter_token_col_from_df, filter_groupby_col_from_df, exclude_token_cols_from_df, str_to_date, date_to_str

from src.config.parameters import SCREENER_TOKEN_FILTER, SCREENER_TOKEN_EXCLUDE

def screeners (
    
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    center_h2("Trade Screeners")
    
    tarf_section(date, fundation)
    fx_carry_section(date, fundation)
    tail_trades_section(date, fundation)

    return None


# ---------- TARF section ---------- 

def tarf_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None

    ) :
    """
    
    """
    left_h5("TARF Visualizer")
    columns_filter = ["Instrument Type", "Expiry Date", "Underlying Asset"]
    dataframe, md5 = read_tarf_by_date(date, fundation)
    
    df_filtered, md5_filtered = filter_tarf_from_df(dataframe, md5, date, fundation, columns_filter)

    columns_pin = ["Trade Code", "Trade Description"]
    gridOptions = show_screener_tarf_table(df_filtered.to_pandas(), md5_filtered, columns_pin, screeners_js_code)

    AgGrid(
        df_filtered.to_pandas(),
        gridOptions=gridOptions,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        custom_css=screeners_custom_css,
        enable_enterprise_modules=False,
        autoSizeColumns=True,
    )

    return None


@st.cache_data()
def filter_tarf_from_df (
        
        _dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        date : Optional[str] = None,
        fund : Optional[str] = None,

        columns : Optional[List[str]] = None,

        token_exclude : Optional[str] = None,
        token_filter : Optional[str] = None,

    ) -> Tuple[Optional[pl.DataFrame], Optional[str]]  :
    """
    
    """
    _dataframe = find_most_recent_file_by_date(date, fund) if _dataframe is None else _dataframe
    date = str_to_date(date)

    token_exclude = SCREENER_TOKEN_EXCLUDE if token_exclude is None else token_exclude
    token_filter = SCREENER_TOKEN_FILTER if token_filter is None else token_filter

    df_filtered = filter_token_col_from_df(_dataframe, columns[0], token_filter)
    df_grouped = filter_groupby_col_from_df(df_filtered, columns[1])

    return df_grouped, md5


@st.cache_data()
def get_tarf_data (
        
        _dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
        columns : Optional[List] = None,
    
    ) :
    """

    """
    dataframe, md5 = filter_tarf_from_df(_dataframe, md5, date, fundation, columns)

    return dataframe, md5



# ----------  FX Carry trades ---------- 

def fx_carry_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None

    ) :
    """

    """
    left_h5("FX Carry")

    #dataframe, md5 = read_fx_carry_by_date(date, fundation)

    #st.dataframe(dataframe)

    return None



# ---------- Tail Trades ----------  

def tail_trades_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
    
    ) :
    """
    
    """
    left_h5("Tail Trades")
    #dataframe, md5 = read_tail_trades_by_date(date, fundation)

    #st.dataframe(dataframe)
    
    return None