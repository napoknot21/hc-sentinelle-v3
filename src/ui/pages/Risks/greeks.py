from __future__ import annotations

import streamlit as st
import datetime as dt

from typing import Optional, List, Dict

from src.utils.formatters import str_to_date, date_to_str
from src.config.parameters import GREEKS_DEFAULT_DATE, GREEKS_ASSET_CLASSES

from src.ui.components.selector import date_selector
from src.ui.components.text import center_h2, left_h5
from src.ui.components.tables import show_history_greeks_table

from src.core.data.greeks import read_history_greeks


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

    start, end  = percentage_greeks_change_section(date, fundation)

    history_greeks_section(date, fundation)
    return None


# ---------- History Greeks ----------

def percentage_greeks_change_section (date, fundation) :
    """
    
    """
    start_date, end_date = dates_percentage_selectors_section()

    start_date = str_to_date(start_date)
    end_date = str_to_date(end_date)

    return start_date, end_date


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
    

def shift_months () :
    """
    """
    return None,


def monday_of_week (date) :
    """
    
    """


# ---------- History Greeks ----------

def history_greeks_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """

    history_greek_graph_section(date, fundation)


def history_asset_selector_section (asset_classes : Optional[Dict[str]] = None) :
    """
    
    """
    asset_classes = GREEKS_ASSET_CLASSES if asset_classes is None else asset_classes
    list_assets = list(asset_classes.keys())

    asset_class = st.selectbox("Choose an Asset Class", )



def history_greek_graph_section (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
    
    ) :
    """
    
    """
    dataframe, md5 = read_history_greeks(date, fundation)
    print(dataframe)
    show_history_greeks_table(dataframe, md5)

    return None


# ------------ Greeks visualizer ------------  

def graphs_greeks_section () :
    """
    """