from __future__ import annotations

import polars as pl
import streamlit as st
import pandas as pd
import datetime as dt


from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

from src.ui.components.text import center_bold_paragraph, center_h1, center_h2


from src.core.data.expiries import load_upcomming_expiries

from typing import Optional


def cash (date : Optional[str | dt.date | dt.datetime], fundation : str) :
    """
    
    
    """
    center_h2("Cash Per Counterparty")

    col1, col2 = st.columns(2)

    with col1 :

        # TODO
        st.write("Hello World")
        st.write("Hello world")
        center_bold_paragraph("Cash per counterparty, type, account and currency")
        #history_cash_per_counterparty()


    with col2 :

        # TODO
        df, md5 = load_upcomming_expiries(date, fundation)
        st.write(" ")
        st.write(" ")
        center_bold_paragraph("Cash per counterparty, type, account and currency")
        #cash_per_counterparty(df, md5, date, fundation)
        st.dataframe(df)

    return None



#@st.cache_data()
def cash_per_counterparty (_dataframe : pl.DataFrame, md5 : str, date : Optional[str | dt.date | dt.datetime], fundation : str) :
    """
    
    """
    center_bold_paragraph("Cash per counterparty, type, account and currency")
    df = pd.DataFrame(_dataframe)
    gb = GridOptionsBuilder.from_dataframe(df)
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



