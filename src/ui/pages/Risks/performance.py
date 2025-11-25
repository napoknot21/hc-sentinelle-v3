from __future__ import annotations

import polars as pl
import datetime as dt
import streamlit as st

from typing import Dict, List, Optional, Dict
# from dateutil.relativedelta import relativedelta

from src.ui.components.selector import date_selector
from src.ui.components.text import center_h2, left_h5, left
from src.ui.components.charts import nav_estimate_performance_graph

from src.config.parameters import NAV_ESTIMATE_RENAME_COLUMNS, PERF_DEFAULT_DATE
from src.utils.formatters import date_to_str, str_to_date, shift_months, monday_of_week
from src.core.data.nav import read_nav_estimate_by_fund, rename_nav_estimate_columns


# Main function

def performance (
    
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None
    
    ) -> None :
    """
    
    """
    # Start Date and End Date variables
    if "start_date_perf" not in st.session_state :
        st.session_state.start_date_perf = str_to_date(PERF_DEFAULT_DATE)
        
    if "end_date_perf" not in st.session_state :
        st.session_state.end_date_perf = dt.date.today()
    
    
    center_h2("Performances")
    st.write('')

    estimated_gross_perf_section(date, fundation)
    nav_estimate_section(fundation)

    return None


def nav_estimate_section (fundation : Optional[str] = None) :
    """
    
    """

    start_date, end_date = date_selectors_section()

    charts_performance_section(fundation, start_date, end_date)


# ----------- Table Estimated Perf Section -----------

def estimated_gross_perf_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None
    
    ) -> None :
    """
    
    """
    st.write("Hello World")
    return None


# ----------- Date selector section -----------

def date_selectors_section () :
    """
    
    """
    col1, col2 = st.columns(2)

    with col1 :
        performance_date_quick_selectors(end_ref_date=st.session_state.end_date_perf)
    
    with col2 :
        start_date, end_date = performance_date_manual_selectors()

    return start_date, end_date


def performance_date_manual_selectors () :
    """
    
    """
    left_h5("Manual Date Selector")
    col1 , col2 = st.columns(2)

    with col1 :

        start_default = st.session_state.start_date_perf
        start_val = date_selector("Start Date", default_value=start_default, key="start_date_perf")
    
    with col2 :

        end_default = st.session_state.end_date_perf
        end_val = date_selector("End Date", default_value=end_default, key="end_date_perf")
    
    # Parse locally
    start_date = str_to_date(start_val)
    end_date   = str_to_date(end_val)

    return start_date, end_date


def performance_date_quick_selectors (
        
        start_default_date : Optional[str | dt.date | dt.datetime] = None,
        end_ref_date : Optional[str | dt.date | dt.datetime] = None
    
    ) :
    """
    
    """
    start_default_date = PERF_DEFAULT_DATE if start_default_date is None else start_default_date
    end_ref = str_to_date(end_ref_date) if end_ref_date is not None else dt.date.today()
    start_default = str_to_date(start_default_date)

    left_h5("Quick Date Selector")
    st.write('')

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        
        if st.button("ALL", key="perf_button_all") :

            st.session_state.start_date_perf = start_default
            st.session_state.end_date_perf = end_ref
            
            st.rerun()

    with col2 :

        if st.button("1YTD", key="perf_ytd_button_year") :

            st.session_state.start_date_perf = dt.date(end_ref.year, 1, 1)
            st.session_state.end_date_perf = end_ref
            
            st.rerun()

    with col3 :

        if st.button("6MTD", key="perf_ytd_button_6_months"):
            
            # rolling 6 months inclusive
            st.session_state.start_date_perf = shift_months(end_ref, -6) + dt.timedelta(days=1)
            st.session_state.end_date_perf = end_ref
            
            st.rerun()

    with col4 :

        if st.button("1MTD", key="perf_ytd_button_1_month"):
        
            st.session_state.start_date_perf = dt.date(end_ref.year, end_ref.month, 1)
            st.session_state.end_date_perf = end_ref
        
            st.rerun()

    with col5:
        
        if st.button("1WTD", key="perf_ytd_button_1_week"):
        
            st.session_state.start_date_perf = monday_of_week(end_ref)
            st.session_state.end_date_perf = end_ref
        
            st.rerun()

    return st.session_state.start_date_perf, st.session_state.end_date_perf


# ----------- Charts Perf Section -----------

def charts_performance_section (
    
        fundation : Optional[str] = None,
        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None
    
    ) :
    """
    
    """
    performance_charts_section(start_date, end_date, fundation)

    st.write('')

    left_h5(f"{fundation} Realized Volatility between {start_date} and {end_date}")
    st.plotly_chart(performance_charts_section(start_date, end_date, fundation))

    return None


def performance_charts_section (
        
        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None,

        fundation : Optional[str] = None,
        rename_cols : Optional[Dict] = None,
        
    ) :
    """
    
    """
    left_h5(f"{fundation} Performance between {start_date} and {end_date}")

    rename_cols = NAV_ESTIMATE_RENAME_COLUMNS if rename_cols is None else rename_cols
    columns = list(rename_cols.values())

    dataframe, md5 = read_nav_estimate_by_fund(fundation)
    rename_df , md5 = rename_nav_estimate_columns(dataframe, md5)

    end_date = dt.datetime.now().date() if end_date is None else end_date
    start_date = dt.date(end_date.year, 1, 1) if start_date is None else start_date

    df_filterd = rename_df.filter(
        
        (pl.col("date") >= pl.lit(start_date)) &
        (pl.col("date") <= pl.lit(end_date))
    
    )

    df_na = df_filterd.drop_nulls(subset=columns)

    fig = nav_estimate_performance_graph(
        df_na, md5, fundation, start_date, end_date, columns, "date"
    )

    st.plotly_chart(fig, use_container_width=True)

    return None

# TODO : Need a best formula for computing this results (window fixed ?)
def realized_volatilty_chart_section (
        
        start_date : Optional[str | dt.datetime | dt.date] = None,
        end_date : Optional[str | dt.datetime | dt.date] = None,

        fundation : Optional[str] = None,
        rename_cols : Optional[Dict] = None,

        window : int = 252,
        annual_factor : int = (252 ** 0.5) * 100,

    ) :
    """
    
    """
    rename_cols = NAV_ESTIMATE_RENAME_COLUMNS if rename_cols is None else rename_cols
    columns = list(rename_cols.values())

    dataframe, md5 = read_nav_estimate_by_fund(fundation)
    rename_df , md5 = rename_nav_estimate_columns(dataframe, md5)

    df_filterd = rename_df.filter(
        
        (pl.col("date") >= pl.lit(start_date)) &
        (pl.col("date") <= pl.lit(end_date))
    
    )

    

    return None


# -----------