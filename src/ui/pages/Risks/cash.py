from __future__ import annotations

import polars as pl
import streamlit as st
import pandas as pd
import datetime as dt

from typing import Optional, List

from src.ui.components.text import center_bold_paragraph, center_h2, left, left_h5
from src.ui.components.charts import cash_chart

from src.core.data.cash import load_all_cash, load_all_collateral, aggregate_n_groupby, pivot_currency_historic

from src.utils.formatters import str_to_date

# -------- Main function --------

def cash (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
        
    ) :
    """
    
    
    """
    center_h2("Cash Per Counterparty")
    st.write('')
    
    currency = currency_chart_section()
    cash_amount_section(date, fundation, currency=currency) 

    st.write('')

    collateral_detailed(date, fundation)

    return None


def currency_chart_section (
        
        options_ccys : Optional[List[str]] = ["EUR", "USD", "CAD"]

    ) -> Optional[str] :
    """
    
    """
    col1, _ = st.columns(2)

    with col1 :

        currency = st.selectbox("Select a Currency", options=options_ccys)

    return currency


# -------- Counterparty tables and charts --------

def cash_amount_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,

        currency : Optional[str] = None
    
    ) :
    """
    
    """
    dataframe, md5 = load_all_cash(fundation)
    col1, col2 = st.columns(2)

    with col1 :
        print(dataframe)
        fig = cash_history_chart(dataframe, md5, currency)
        st.plotly_chart(fig)

    with col2 :

        st.write('')
        st.write('')
        cash_per_ctpy_table(dataframe, md5, date, ("Bank", "Type"), "Amount in CCY")

    return None


def cash_history_chart (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,
        currency : Optional[str] = None

    ) -> pl.DataFrame :
    """
    
    """
    df_pivot, md5_pivot = pivot_currency_historic(dataframe, md5, ("Bank", "Type"), selected_currency=currency)
    fig = cash_chart(df_pivot, md5_pivot, ("Bank", "Type"), currency)

    return fig


def cash_per_ctpy_table (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        date : Optional[str | dt.datetime | dt.date] = None,

        group_by : Optional[tuple[str, str]] = ("Bank", "Type"),
        aggregate : Optional[str] = "Amount in CCY"

    ) :
    """
    
    """
    left_h5(f"Cash per counterparty, type and currency (Email data) at {date}")
    new_df, md5_hash = aggregate_n_groupby(dataframe, md5, date, group_by, aggregate)
    
    st.dataframe(new_df)

    return None


# -------- Counterparty tables and charts --------

def collateral_detailed (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
    ) :
    """
    
    """
    left_h5("Cash per Counterparty Detailed")

    date = str_to_date(date)
    dataframe, md5 = load_all_collateral(fundation=fundation)

    dataframe = dataframe.filter(pl.col("Date") == date)

    st.dataframe(dataframe)

    return None


# -------- -------- 

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



