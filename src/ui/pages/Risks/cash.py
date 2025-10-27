from __future__ import annotations

import polars as pl
import streamlit as st
import datetime as dt

from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

from src.ui.tools.st_functions import center


from typing import Optional


def cash (date : Optional[str | dt.date | dt.datetime], fundation : str) :
    """
    
    
    """
    st.title("Cash Per Counterparty")

    col1, col2 = st.columns(2)

    with col1 :

        # TODO
        st.write(" ")
        st.write(" ")
        center("Cash per counterparty, type, account and currency", "p", "font-weight: bold")
        history_cash_per_counterparty()


    with col2 :

        # TODO
        st.write(" ")
        st.write(" ")
        center("Cash per counterparty, type, account and currency", "p", "font-weight: bold")
        cash_per_counterparty()
    

    return None



@st.cache_data()
def cash_per_counterparty (_dataframe : pl.DataFrame, md5 : str, date : Optional[str | dt.date | dt.datetime], fundation : str) :
    """
    
    """
    center("Cash per counterparty, type, account and currency", "p", "font-weight: bold")
    
    gb = GridOptionsBuilder.from_dataframe(_dataframe)
    grid_options = gb.build()
    
    AgGrid(_dataframe, gridOptions=grid_options, fit_columns_on_grid_load=True)
    return None


@st.cache_data()
def history_cash_per_counterparty (_dataframe : pl.DataFrame, md5 : str , fundation : str) :
    """
    
    """
    return None


def cash_per_counterparty_details (date : Optional[str | dt.date | dt.datetime], fundation : str) :
    """
    
    """
    return None


def exchange_ccy_by_date (date : Optional[str | dt.date | dt.datetime], fundation : str) :
    """
    
    """
    return None



