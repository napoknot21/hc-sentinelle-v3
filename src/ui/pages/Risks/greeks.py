from __future__ import annotations

import polars as pl
import streamlit as st
import datetime as dt

from typing import Optional, List, Dict

from src.utils.formatters import str_to_date, date_to_str, shift_months, monday_of_week
from src.config.parameters import GREEKS_DEFAULT_DATE, GREEKS_ASSET_CLASSES, GREEKS_COLUMNS, GREEKS_ASSET_CLASSES

from src.ui.components.selector import date_selector
from src.ui.components.text import center_h2, left_h5, left_h3
from src.ui.components.charts import show_history_greeks_graph, show_change_greeks_graph

from src.core.data.greeks import read_history_greeks, read_greeks_by_date


def greeks (

        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    # Start Date and End Date variables
    if "start_date_greeks" not in st.session_state :
        st.session_state.start_date_greeks = str_to_date(GREEKS_DEFAULT_DATE)
        
    if "end_date_greeks" not in st.session_state :
        st.session_state.end_date_greeks = dt.date.today()

    center_h2("Greeks")

    percentage_greeks_change_section(date, fundation)

    history_greeks_section(date, fundation)
    return None


# ---------- Change (%) Greeks ----------

def percentage_greeks_change_section (date, fundation) :
    """
    
    """
    left_h3(f"Pourcentage % change between {st.session_state.start_date_greeks} and {st.session_state.end_date_greeks}")
    start_date, end_date = dates_percentage_selectors_section()

    start_date = date_to_str(start_date)
    end_date = date_to_str(end_date)

    df_start, md5_start = read_greeks_by_date(start_date, fundation)
    print(df_start)
    df_end, md5_end = read_greeks_by_date(end_date, fundation)
    print(df_end)
    if (df_start is None or df_end is None) :
        
        st.error("No data for the selected dates... Retrying with new ones")
        return None
    
    underlying = underlying_change_greek_selector(df_start, df_end)

    pourcentage_change_underlyin_seciton(df_start, md5_start, df_end, md5_end, underlying=underlying)

    return None


# Date Selectors sub section

def dates_percentage_selectors_section () :
    """
    
    """
    col1, col2 = st.columns(2)

    with col1 :
        greeks_date_quick_selectors(end_ref_date=st.session_state.end_date_greeks)
    
    with col2 :
        start_date, end_date = greeks_date_manual_selectors()

    return start_date, end_date


def greeks_date_manual_selectors () :
    """
    
    """
    left_h5("Manual Date Selector")
    col1 , col2 = st.columns(2)

    with col1 :

        start_default = st.session_state.start_date_greeks
        start_val = date_selector("Start Date", default_value=start_default, key="start_date_greeks")
    
    with col2 :

        end_default = st.session_state.end_date_greeks
        end_val = date_selector("End Date", default_value=end_default, key="end_date_greeks")
    
    # Parse locally
    start_date = str_to_date(start_val)
    end_date   = str_to_date(end_val)

    return start_date, end_date


def greeks_date_quick_selectors (
        
        start_default_date : Optional[str | dt.date | dt.datetime] = None,
        end_ref_date : Optional[str | dt.date | dt.datetime] = None
    
    ) :
    """
    
    """
    start_default_date = GREEKS_DEFAULT_DATE if start_default_date is None else start_default_date
    end_ref = str_to_date(end_ref_date) if end_ref_date is not None else dt.date.today()
    start_default = str_to_date(start_default_date)

    left_h5("Quick Date Selector")
    st.write('')

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        
        if st.button("ALL", key="greeks_button_all") :

            st.session_state.start_date_greeks = start_default
            st.session_state.end_date_greeks = end_ref
            
            st.rerun()

    with col2 :

        if st.button("1YTD", key="greeks_ytd_button_year") :

            st.session_state.start_date_greeks = dt.date(end_ref.year, 1, 1)
            st.session_state.end_date_greeks = end_ref
            
            st.rerun()

    with col3 :

        if st.button("6MTD", key="greeks_ytd_button_6_months"):
            
            # rolling 6 months inclusive
            st.session_state.start_date_greeks = shift_months(end_ref, -6) + dt.timedelta(days=1)
            st.session_state.end_date_greeks = end_ref
            
            st.rerun()

    with col4 :

        if st.button("1MTD", key="greeks_ytd_button_1_month"):
        
            st.session_state.start_date_greeks = dt.date(end_ref.year, end_ref.month, 1)
            st.session_state.end_date_greeks = end_ref
        
            st.rerun()

    with col5:
        
        if st.button("1WTD", key="greeks_ytd_button_1_week"):
        
            st.session_state.start_date_greeks = monday_of_week(end_ref)
            st.session_state.end_date_greeks = end_ref
        
            st.rerun()

    return st.session_state.start_date_greeks, st.session_state.end_date_greeks
    
# Underlying selector

def underlying_change_greek_selector (df_start : pl.DataFrame, df_end : pl.DataFrame, column : str = "Underlying") :
    """
    
    """
    start_vals = set(df_start.get_column(column).unique().to_list())
    end_vals = set(df_end.get_column(column).unique().to_list())

    # Intersection → only underlyings present in BOTH
    underlyings = sorted(start_vals & end_vals)

    underlying = st.selectbox("Select an Underlying", options=underlyings)

    return underlying

# Graph underlying section

def pourcentage_change_underlyin_seciton (
        
        df_start : Optional[pl.DataFrame] = None,
        md5_start : Optional[str] = None,
        df_end : Optional[pl.DataFrame] = None,
        md5_end : Optional[str] = None, 
        x_axis : Optional[List[str]] = None,
        underlying : Optional[str] = None,
    
    ) :
    """
    
    """
    if df_start is None or df_end is None :
        return None

    x_axis = df_start.columns[1:] if x_axis is None else x_axis
    underlying = underlying_change_greek_selector(df_start, md5_start, df_end, md5_end) if underlying is None else underlying

    fig = show_change_greeks_graph(df_start, md5_start, df_end, md5_end, x_axis, underlying)

    st.plotly_chart(fig)

    return None


# ---------- History Greeks ----------

def history_greeks_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    left_h3(f"History Greeks by Asset Class and Greek")
    asset_class = history_asset_selector_section()
    greek = history_greek_selector_section()

    history_greek_graph_section(date, fundation, asset_class, greek)

    return None


def history_asset_selector_section (asset_classes : Optional[Dict[str]] = None) :
    """
    
    """
    asset_classes = GREEKS_ASSET_CLASSES if asset_classes is None else asset_classes
    list_assets = list(asset_classes.keys())

    asset_class = st.selectbox("Choose an Asset Class", options=list_assets)

    return asset_class


def history_greek_selector_section (greeks : Optional[Dict[str]] = None) :
    """
    
    """
    greeks = GREEKS_COLUMNS if greeks is None else greeks
    list_greeks = list(greeks.keys())[1:-1]

    greek = st.selectbox("Choose a Greek", options=list_greeks)

    return greek


def history_greek_graph_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None,

        asset_class : Optional[str] = None,
        greek : Optional[str] = None,

        greeks_rules : Optional[Dict] = None,
    
    ) :
    """
    
    """
    dataframe, md5 = read_history_greeks(date, fundation)
    greeks_rules = GREEKS_ASSET_CLASSES if greeks_rules is None else greeks_rules
    print(dataframe)
    fig = show_history_greeks_graph(dataframe, md5, asset_class, greek, greeks_rules)
    st.plotly_chart(fig)
    
    return None


# ------------ Greeks visualizer ------------  

def graphs_greeks_section () :
    """
    """