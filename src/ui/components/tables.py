from __future__ import annotations

import datetime as dt
import polars as pl
import pandas as pd

from typing import List, Optional, Any, Dict

import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder


@st.cache_data()
def show_last_n_expiries (_dataframe : pl.DataFrame, md5 : str, specific_cols : Optional[List[str]], max_rows : int = 10) :
    """
    
    """
    _dataframe = _dataframe.select(specific_cols) if specific_cols is not None else _dataframe
    df_head = _dataframe.head(max_rows)

    table = st.dataframe(df_head)
    return table


@st.cache_data()
def show_full_expiries (_dataframe : pl.DataFrame, md5 : str, ) :
    """
    
    """
    return None


def plot_gross_perf_table (_dataframe : pl.DataFrame) :
    """
    """
    return None


@st.cache_data()
def display_payments_table (_dataframe : pl.DataFrame, md5 : str, height : int = 800):
    """
    
    """
    if _dataframe is None :
        
        st.cache_data.clear()
        return None
    
    table = st.dataframe(_dataframe, height=height)

    return table


#@st.cache_data()
def show_screener_tarf_table (
        
        _dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        columns : Optional[List[str]] = None,

        _style_js : Optional[Any] = None,
        custom_css : Optional[Dict] = None,

    ) :
    """
    
    """
    if _dataframe is None :

        st.cache_data.clear()
        return None
    
    gb = GridOptionsBuilder.from_dataframe(_dataframe)
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=False, resizable=True)

    # Pin the first two columns
    for column in columns :

        gb.configure_column(
            column,
            pinned="left",
            type=["textColumn"],
            aggFunc=None,
            enableValue=True,
            valueFormatter=None,
        )


    gridOptions = gb.build()
    gridOptions["onFirstDataRendered"] = _style_js.js_code

    return gridOptions
    """
    table = AgGrid(

        _dataframe,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        custom_css=custom_css,
        enable_enterprise_modules=False,
        autoSizeColumns=True

    )


    return table
    """


