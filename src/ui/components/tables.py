from __future__ import annotations

import datetime as dt
import polars as pl
import pandas as pd

from typing import List, Optional, Any, Dict

import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from src.utils.formatters import format_numeric_columns_to_string


@st.cache_data()
def show_last_n_expiries (_dataframe : pl.DataFrame, md5 : str, specific_cols : Optional[List[str]], max_rows : int = 10) :
    """
    
    """
    _dataframe = _dataframe.select(specific_cols) if specific_cols is not None else _dataframe
    df_head = _dataframe.head(max_rows)

    table = st.dataframe(df_head)
    return table


#@st.cache_data()
def show_expiries_history (_dataframe : pl.DataFrame, md5 : str,  height : int = 800) :
    """
    
    """
    if _dataframe is None :

        st.cache_data.clear()
        return None

    _dataframe = format_numeric_columns_to_string(_dataframe)
    df = _dataframe.to_pandas()

    gb = GridOptionsBuilder.from_dataframe(df) #table = st.dataframe(_dataframe)
    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        floatingFilter=True,
    )

    gb.configure_pagination(
        paginationAutoPageSize=False,
        paginationPageSize=50,
    )

    # sidebar (pour hide/afficher colonnes + filtres avancés)
    gb.configure_side_bar()

    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        height=height,
        update_mode=GridUpdateMode.NO_UPDATE,
        theme="alpine",  # ou "streamlit", "balham", etc.
    )


    return None


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


def leverages_per_trades_tables (_dataframe : Optional[pl.DataFrame] = None, md5 : Optional[str] = None, height : int = 800) :
    """
    Docstring for leverages_per_trades_tables
    
    :param _dataframe: Description
    :type _dataframe: Optional[pl.DataFrame]
    :param md5: Description
    :type md5: Optional[str]
    :param height: Description
    :type height: int
    """
    if _dataframe is None :

        st.cache_data.clear()
        return None
    
    _dataframe = format_numeric_columns_to_string(_dataframe)
    df = _dataframe.to_pandas()

    gb = GridOptionsBuilder.from_dataframe(df) #table = st.dataframe(_dataframe)
    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        floatingFilter=True,
    )

    gb.configure_pagination(
        paginationAutoPageSize=False,
        paginationPageSize=50,
    )

    # sidebar (pour hide/afficher colonnes + filtres avancés)
    gb.configure_side_bar()

    grid_options = gb.build()

    grid_response = AgGrid(

        df,
        gridOptions=grid_options,
        height=height,
        update_mode=GridUpdateMode.NO_UPDATE,
        theme="alpine",  # ou "streamlit", "balham", etc.
    
    )

    return None


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


def show_aum_details_table (_dataframe : Optional[pl.DataFrame] = None, md5 : Optional[str] = None, height : int = 800) :
    """
    Docstring for show_aum_details_table
    
    :param _dataframe: Description
    :type _dataframe: Optional[pl.DataFrame]
    """

    if _dataframe is None :

        st.cache_data.clear()
        return None
    
    _dataframe = format_numeric_columns_to_string(_dataframe)
    df = _dataframe.to_pandas()

    gb = GridOptionsBuilder.from_dataframe(df) #table = st.dataframe(_dataframe)
    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        floatingFilter=True,
    )

    gb.configure_pagination(
        paginationAutoPageSize=False,
        paginationPageSize=50,
    )

    # sidebar (pour hide/afficher colonnes + filtres avancés)
    gb.configure_side_bar()

    grid_options = gb.build()

    grid_response = AgGrid(

        df,
        gridOptions=grid_options,
        height=height,
        update_mode=GridUpdateMode.NO_UPDATE,
        theme="alpine",  # ou "streamlit", "balham", etc.
    
    )

    return None

