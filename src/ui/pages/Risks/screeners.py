from __future__ import annotations

import os
import polars as pl
import datetime as dt
import streamlit as st

from typing import Optional, List, Tuple
from st_aggrid import AgGrid

from src.config.parameters import SCREENER_TOKEN_FILTER, SCREENER_TOKEN_EXCLUDE
from src.utils.dates import str_to_date
from src.utils.formatters import date_to_str, format_numeric_columns_to_string 

from src.ui.styles.base import screeners_js_code, screeners_custom_css
from src.ui.components.text import center_h1, center_h2, left_h5
from src.ui.components.tables import show_screener_tarf_table

from src.core.data.screeners import tarf_visualizer_by_date, read_db_gross_data_by_date, fx_carry_by_date, tail_trades_by_date


def screeners (
    
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    center_h2("Trade Screeners")

    dataframe, md5, real_date = read_db_gross_data_by_date(date, fundation)
    
    tarf_section(date, fundation, dataframe, md5)
    fx_carry_section(date, fundation, dataframe, md5)
    tail_trades_section(date, fundation, dataframe, md5)

    return None


# ---------- TARF section ----------

def tarf_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,

        dataframe :  Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

    ) :
    """
    
    """

    columns_filter = ["Instrument Type", "Expiry Date", "Underlying Asset"]
    df_filtered, md5, real_date = tarf_visualizer_by_date(dataframe, md5, date, fundation, columns_filter=columns_filter)

    real_date = date_to_str(real_date)
    left_h5(f"TARF Visualizer at {real_date}")

    if df_filtered.is_empty() or df_filtered is None :

        st.warning("No TARF trades availables at selected date")
        return None

    columns_pin = ["Trade Code", "Trade Description"]
    df_filtered = df_filtered.to_pandas()
    gridOptions = show_screener_tarf_table(df_filtered, md5, columns_pin, screeners_js_code)

    AgGrid(

        df_filtered,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        custom_css=screeners_custom_css,
        enable_enterprise_modules=False,
        autoSizeColumns=True,

    )

    return None



# ----------  FX Carry trades ---------- 

def fx_carry_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,

        dataframe :  Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

    ) :
    """

    """
    df_grouped, md5, real_date = fx_carry_by_date(dataframe, md5, date, fundation)
    formated_df = format_numeric_columns_to_string(df_grouped)
    
    real_date = date_to_str(real_date)
    left_h5(f"FX Carry at {real_date}")

    if formated_df is None or formated_df.is_empty() :
        
        st.warning("No FX Carry trades availables at selected date")
        return None 

    formated_df = formated_df.to_pandas()
    
    columns_pin = ["Trade Code", "Trade Description"]
    gridOptions = show_screener_tarf_table(formated_df, md5, columns_pin, screeners_js_code)

    AgGrid(

        formated_df,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        custom_css=screeners_custom_css,
        enable_enterprise_modules=False,
        autoSizeColumns=True,

    )

    return None


# ---------- Tail Trades ----------  

def tail_trades_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,

        dataframe :  Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,
    
    ) :
    """
    
    """
    df_grouped, md5, real_date = tail_trades_by_date(dataframe, md5, date, fundation)
    formated_df = format_numeric_columns_to_string(df_grouped)
    
    real_date = date_to_str(real_date)
    left_h5(f"Tail Trades at {real_date}")

    if formated_df is None or formated_df.is_empty() :
        
        st.warning("No Tail trades availables at selected date")
        return None 
    
    #formated_df = formated_df.to_pandas()
    st.dataframe(formated_df)
    """
    columns_pin = ["Trade Code", "Trade Description"]
    gridOptions = show_screener_tarf_table(pandas_df, md5, columns_pin, screeners_js_code)

    AgGrid(
        pandas_df,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        custom_css=screeners_custom_css,
        enable_enterprise_modules=False,
        autoSizeColumns=True,
    )
    """

    return None