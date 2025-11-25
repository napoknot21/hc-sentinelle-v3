from __future__ import annotations

import sys
import polars as pl
import streamlit as st
import pandas as pd
import datetime as dt

from typing import Optional, List, Dict

# Add of CCYs from LibApi
from src.config.paths import LIBAPI_ABS_PATH
sys.path.append(LIBAPI_ABS_PATH)
from libapi.config.parameters import CCYS_ORDER # type: ignore

from src.utils.formatters import str_to_date, format_numeric_columns_to_string

from src.ui.components.text import center_bold_paragraph, center_h2, left, left_h5
from src.ui.components.charts import cash_chart, history_criteria_graph

from src.core.data.cash import load_all_cash, load_all_collateral, aggregate_n_groupby, pivot_currency_historic, load_cache_fx_values
from src.core.api.cash import call_api_for_pairs

# -------- Main function --------

def cash (
        
        date : Optional[str | dt.date | dt.datetime] = None,
        fundation : Optional[str] = None
        
    ) :
    """
    
    
    """
    center_h2("Cash Per Counterparty")
    st.write('')
    
    cash_amount_section(date, fundation) 

    st.write('')

    collateral_detailed(date, fundation)

    st.write('')

    render_fx_metrics_section()
    
    im_n_collat_section(fundation)

    vm_n_requirement_section(fundation)
    
    return None


# -------- Counterparty tables and charts --------

def cash_amount_section (
        
        date : Optional[str | dt.datetime | dt.date] = None,
        fundation : Optional[str] = None,
    
    ) :
    """
    
    """
    dataframe, md5 = load_all_cash(fundation)
    col1, col2 = st.columns(2)

    with col1 :
        
        print(dataframe)
        cash_history_chart(dataframe, md5, ("Bank", "Type", "Date"), "Amount in EUR")
        
    with col2 :

        st.write('')
        st.write('')
        cash_per_ctpy_table(dataframe, md5, date, ("Bank", "Type"), "Amount in CCY")

    return None


def cash_history_chart (
        
        dataframe : Optional[pl.DataFrame] = None,
        md5 : Optional[str] = None,

        group_by : Optional[tuple[str, str]] = ("Bank", "Type", "Date"),
        aggregate : Optional[str] = "Amount in EUR"

    ) -> pl.DataFrame :
    """
    
    """
    df_grouped = (
        dataframe
        .group_by(list(group_by))
        .agg(pl.col(aggregate).sum().alias(aggregate))
        .sort("Date")
    )

    print(df_grouped)

    fig = cash_chart(df_grouped, md5, ("Bank", "Type"))
    
    st.plotly_chart(fig)
    
    return None


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
    df_st = format_numeric_columns_to_string(new_df)
    st.dataframe(df_st)

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
    df_st = format_numeric_columns_to_string(dataframe)

    st.dataframe(df_st)

    return None


# -------- FX Values --------

def render_fx_metrics_section (values : Optional[Dict] = None, base : str = "EUR") :
    """
    Docstring for render_fx_metrics_section
    
    :param values: Description
    :type values: Optional[Dict]
    """
    values = fx_metrics_section() if values is None else values

    if values is None :
        return None
    
    left_h5("FX conversion values")

    ccys = [c for c in values.keys() if c != "EUR"]
    cols = st.columns(len(ccys))


    for ccy, col in zip(ccys, cols) :
        
        rate = values.get(ccy, 1.0)

        with col :

            label = f"{base} -> {ccy}"
            value_str = f"{rate:,.4f}"

            # Metrics
            st.metric(
                label=label,
                value=value_str,
            )

            st.markdown(
                f"<div style='font-size:0.75rem; color:#888;'>"
                f"1 {base} = {value_str} {ccy}"
                f"</div>",
                unsafe_allow_html=True,
            )

    return None


def fx_metrics_section () :
    """
    Docstring for fx_metrics_section
    """
    close_values = load_cache_fx_values()

    if close_values is not None :
        return close_values
    
    close_values = call_api_for_pairs(None)

    if close_values is not None :
        return close_values

    return None


# -------- IM & Collat columns -------- 

def im_n_collat_section (fundation : Optional[str] = None) :
    """
    Docstring for im_n_collat_section
    """
    col1, col2 = st.columns(2)

    with col1 :
        im_graph_section(fundation)

    with col2 :
        collat_graph_section(fundation)

    return None

 
def im_graph_section (fundation : Optional[str] = None) :
    """
    Docstring for im_graph_section
    
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5 = load_all_collateral(fundation)
    fig = history_criteria_graph(dataframe, md5, "IM")
    
    st.plotly_chart(fig, use_container_width=True)

    return None


def collat_graph_section (fundation : Optional[str] = None) :
    """
    Docstring for collat_graph_section
    
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5 = load_all_collateral(fundation)
    fig = history_criteria_graph(dataframe, md5, "Total")
    
    st.plotly_chart(fig, use_container_width=True)

    return None
    

# -------- VM & Req columns -------- 

def vm_n_requirement_section (fundation : Optional[str] = None) :

    """
    Docstring for vm_n_requirement_section
    """
    col1, col2 = st.columns(2)

    with col1 :
        vm_graph_section(fundation)

    with col2 :
        requirement_graph_section(fundation)

    return None


def vm_graph_section (fundation : Optional[str] = None) :
    """
    Docstring for collat_graph_section
    
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5 = load_all_collateral(fundation)
    fig = history_criteria_graph(dataframe, md5, "VM")
    
    st.plotly_chart(fig, use_container_width=True)

    return None


def requirement_graph_section (fundation : Optional[str] = None) :
    """
    Docstring for collat_graph_section
    
    :param fundation: Description
    :type fundation: Optional[str]
    """
    dataframe, md5 = load_all_collateral(fundation)
    fig = history_criteria_graph(dataframe, md5, "Requirement")
    
    st.plotly_chart(fig, use_container_width=True)

    return None
